# Portia — Secrets Scanner Design Document

**Date**: 2026-02-20
**Project**: Cybersecurity-Projects / intermediate / secrets-scanner
**Replaces**: Container Security Scanner (overlap with Docker Security Audit)
**Module**: `github.com/CarterPerez-dev/portia`

---

## Overview

Portia is a Go CLI tool that scans git repositories and directories for leaked API keys, passwords, tokens, and other secrets. It combines keyword pre-filtering, regex pattern matching, Shannon entropy analysis, and Have I Been Pwned breach verification into a pipeline architecture modeled after production scanners like Gitleaks and TruffleHog.

**Scan targets**: Git history (via go-git in-process) and filesystem directories.
**Not in scope**: Docker image layer extraction (covered by the existing Docker Security Audit project).

---

## CLI Structure

### Commands

```
portia scan [path]          Scan a directory/file for secrets
portia git [path]           Scan git history for secrets
portia init                 Generate .portia.toml config
portia config rules         List all built-in detection rules
portia config test <rule>   Test a specific rule against sample input
```

### Global Flags

```
--format       string   Output format: terminal (default), json, sarif
--rules        string   Path to custom rules TOML file
--verbose/-v            Show full finding details (line context, entropy scores)
--no-color              Disable colored output
--exit-code    int      Exit code when secrets found (default: 1, 0 for CI soft-fail)
```

### Scan Flags

```
portia scan:
  --exclude     []string   Glob patterns to skip (e.g., "vendor/**", "*.lock")
  --max-size    string     Skip files larger than (default: "1MB")
  --entropy     float      Override entropy threshold (default: per-rule)
  --hibp                   Enable HIBP password breach checking

portia git:
  --since       string     Only scan commits after date (e.g., "7 days ago")
  --branch      string     Scan specific branch (default: all)
  --depth       int        Max commit depth (default: unlimited)
  --staged-only            Only scan currently staged changes (pre-commit hook mode)
  --hibp                   Enable HIBP password breach checking
```

---

## Pipeline Architecture

```
Source --> Chunker --> Keyword Filter --> Detector Pool --> Verifier (HIBP) --> Reporter
```

### Stage 1: Source

Two implementations behind a common interface:
- **DirSource**: Walks filesystem, respects .gitignore + .portiaignore, skips binaries and large files.
- **GitSource**: Uses go-git to iterate commits, produces diffs (added lines only).

### Stage 2: Chunker

Splits source output into Chunk structs containing content, file path, line number, and optional git metadata (commit SHA, author, date).

### Stage 3: Keyword Filter

The critical performance optimization. Each rule declares case-insensitive keywords. Before any regex runs, the engine checks whether the chunk contains at least one keyword. This eliminates ~95% of chunks. Only rules whose keywords matched are forwarded to the detector pool for that chunk.

### Stage 4: Detector Pool

Bounded concurrency via errgroup.SetLimit(runtime.NumCPU()). For each chunk that passed keyword filtering, matched rules execute:
1. Regex match on captured group
2. Entropy check on captured value (if rule has a threshold)
3. Stopword/allowlist filtering
4. Structural validation (assignment operator present, not a template variable)

### Stage 5: Verifier (HIBP)

Post-processing enrichment, only when --hibp flag is set. Classifies each finding by secret type, routes passwords to HIBP k-anonymity API, marks results as verified_breach, not_breached, or skipped.

### Stage 6: Reporter

Three implementations behind a Reporter interface:
- **TerminalReporter**: Angela-style colored output with severity colors, spinners, summary.
- **JSONReporter**: Structured JSON to stdout.
- **SARIFReporter**: SARIF v2.1.0 for GitHub/GitLab integration.

### Concurrency Model

- Channels buffered at 256 to prevent backpressure stalls
- errgroup.WithContext for detector pool — first fatal error cancels everything
- HIBP lookups run as a separate bounded pool (20 concurrent, 50 req/s rate limit) after scanning completes
- Context propagation throughout for clean Ctrl+C cancellation

---

## Core Types

### Finding

```
Finding {
    RuleID      string
    Description string
    Severity    string       // critical, high, medium, low
    Match       string
    Secret      string       // The captured secret value (redactable)
    Entropy     float64
    FilePath    string
    LineNumber  int
    LineContent string
    CommitSHA   string       // Empty for dir scan
    Author      string       // Empty for dir scan
    CommitDate  time.Time    // Empty for dir scan
    HIBPStatus  string       // "breached", "clean", "skipped", "unchecked"
    BreachCount int
}
```

### Rule

```
Rule {
    ID          string
    Description string
    Severity    string
    Keywords    []string
    Pattern     *regexp.Regexp
    SecretGroup int
    Entropy     *float64     // nil = skip entropy check
    Allowlist   Allowlist
    SecretType  SecretType   // Password, APIKey, Token, PrivateKey, etc.
}
```

### Chunk

```
Chunk {
    Content    string
    FilePath   string
    LineStart  int
    CommitSHA  string
    Author     string
    CommitDate time.Time
}
```

---

## Rule Engine

### 50+ Built-in Rules

| Category | Count | Examples | Severity |
|---|---|---|---|
| Cloud providers | ~10 | AWS Access Key, AWS Secret Key, GCP API Key, Azure Client Secret, DigitalOcean PAT | Critical |
| Source control | ~8 | GitHub PAT (classic), Fine-grained PAT, OAuth, GitLab PAT, Bitbucket App Password | Critical |
| Payment/SaaS | ~8 | Stripe Secret Key, Stripe Restricted Key, SendGrid, Twilio, Shopify | Critical |
| Communication | ~5 | Slack Bot/User/App Token, Slack Webhook, Discord Bot Token | High |
| AI/ML services | ~4 | OpenAI, Anthropic, HuggingFace, Replicate | High |
| Infrastructure | ~5 | Heroku, Terraform Cloud, Vault Token, PlanetScale, Supabase | Critical |
| Cryptographic | ~3 | Private Keys (RSA/EC/DSA/OPENSSH), PGP, X.509 | Critical |
| Authentication | ~4 | JWT, Bearer Token, Basic Auth, OAuth Client Secret | High |
| Database | ~5 | PostgreSQL URI, MySQL URI, MongoDB URI, Redis URI, Generic DB URI | Critical |
| Generic | ~3 | Generic API Key (entropy 3.7), Generic Secret (entropy 3.7), Generic Password | Medium |

### False Positive Defenses (5 Layers)

**Layer 1 — Keyword pre-filter**: Part of the pipeline. No keyword match = chunk skipped.

**Layer 2 — Structural validation**: Generic rules require an assignment operator between keyword and value (=, :, =>, :=, ||).

**Layer 3 — Stopwords**: ~1,500 common programming words. If captured secret contains a stopword, finding is dropped.

**Layer 4 — Allowlists**:
- Global path allowlist: go.sum, package-lock.json, pnpm-lock.yaml, *.min.js, vendor/, node_modules/, .git/, dist-info/
- Global value allowlist: placeholder values (EXAMPLE_KEY, your-api-key-here, xxxx, ${VAR}, {{template}}, os.Getenv(...))
- Per-rule allowlists for rule-specific exclusions

**Layer 5 — Entropy validation**: Post-filter on captured secret value.
- Base64 charset: 4.5 threshold
- Hex charset: 3.0 threshold
- Alphanumeric (generic rules): 3.7 threshold
- Provider-specific rules with known prefixes: 3.0 threshold

### TOML Override Format (.portia.toml)

Users can disable built-in rules, add path excludes, allowlist values, and define custom rules. Custom rules use the same structure as built-in rules (id, description, severity, keywords, pattern, secret-group, entropy).

---

## HIBP Integration

### K-Anonymity Protocol

1. SHA-1 hash the plaintext password locally
2. Send only the 5-character hex prefix to api.pwnedpasswords.com/range/{prefix}
3. Receive ~800 suffixes with breach counts
4. Match locally — the API never learns the password

### Architecture

- **HTTP Client**: hashicorp/go-retryablehttp with custom transport (MaxIdleConnsPerHost: 50, HTTP/2, TLS 1.2+)
- **Cache**: hashicorp/golang-lru/v2/expirable — LRU cache keyed by 5-char prefix, 24-hour TTL
- **Circuit Breaker**: sony/gobreaker — trips after 5 consecutive failures, 30s recovery timeout
- **Rate Limiter**: golang.org/x/time/rate at 50 req/s with burst of 10
- **Concurrency**: errgroup.SetLimit(20) for parallel lookups

### Secret Classification Router

Only human-chosen passwords are sent to HIBP. Machine-generated secrets (API keys, tokens, private keys) are skipped based on:
- Known format prefixes (AKIA, ghp_, sk_live_, xoxb-, SG., sk-)
- Keyword context (password, passwd, pwd in surrounding code)
- Entropy heuristic (< 3.5 bits + < 32 chars = likely human-chosen)

### Privacy Safeguards

- Never transmit full hash or plaintext
- Logger set to nil to prevent logging of /range/{prefix} URLs
- Results reported as boolean compromised/not-compromised (breach count available in verbose mode only)
- HTTPS exclusively, TLS 1.2+ enforced

---

## Terminal Output Design

### Color Mapping

- CRITICAL: red
- HIGH: bold red
- MEDIUM: yellow
- LOW: cyan
- File paths: hi-cyan
- Rule IDs: blue
- Secret values: dim (partially redacted)
- Line numbers: dim italic
- HIBP breach warnings: bold yellow

### Output Sections

1. Banner (alternating red/blue ASCII art)
2. Spinner during scan (cyan braille frame + magenta message)
3. Findings grouped by file, sorted by severity
4. HIBP breach check section (when --hibp used)
5. Summary (files scanned, rules evaluated, secrets found, duration)

### Redaction

Secret values are partially redacted by default: first 6 characters shown, rest replaced with "...". Full values shown only with --verbose flag.

---

## Project Structure

```
PROJECTS/intermediate/secrets-scanner/
  cmd/portia/main.go
  internal/
    cli/          root.go, scan.go, git.go, init.go, config.go
    engine/       pipeline.go, chunk.go, detector.go, filter.go
    source/       source.go, directory.go, git.go
    rules/        registry.go, builtin.go, custom.go, entropy.go
    hibp/         client.go, cache.go, breaker.go, classify.go
    report/       reporter.go, terminal.go, json.go, sarif.go
    ui/           banner.go, color.go, symbol.go, spinner.go
    config/       config.go
  pkg/types/      types.go
  testdata/       repos/, fixtures/, golden/
  learn/          00-OVERVIEW.md through 04-CHALLENGES.md
  .portia.toml, .golangci.yml, .gitignore, Justfile, go.mod, LICENSE, README.md
```

### Dependencies

```
github.com/spf13/cobra
github.com/fatih/color
github.com/go-git/go-git/v5
github.com/pelletier/go-toml/v2
github.com/hashicorp/golang-lru/v2
github.com/sony/gobreaker/v2
github.com/hashicorp/go-retryablehttp
golang.org/x/sync
golang.org/x/time
```

---

## Testing Strategy

### Unit Tests

- **rules/**: Table-driven tests for each of the 50+ rules with true positives, true negatives, and known false positive patterns.
- **engine/**: Pipeline stages tested in isolation (chunker, keyword filter, detector, structural validation).
- **rules/entropy.go**: Shannon entropy tested against known values from detect-secrets' test suite.
- **hibp/**: HTTP test server mocks, cache behavior, circuit breaker states, classification routing.
- **source/**: Directory walker respects gitignore, skips binaries, respects max-size. Git source produces correct diffs.
- **report/**: JSON and SARIF output compared against golden files.
- **config/**: TOML parsing, rule merging, disable/override behavior.

### Integration Tests

- testdata/fixtures/ with planted secrets across Python, YAML, .env, JSON, Go, JS files.
- testdata/repos/ with small git repos containing commits with secrets added then deleted.
- Golden file tests for JSON and SARIF output.

### CI

- go test -race ./... (mandatory)
- golangci-lint v2 with Tier 1/2/3 linters
- gofumpt + golines (80-char max)

---

## Learn Folder

Grounded in three real-world incidents:
- **Uber 2022**: Hardcoded HCP Vault credentials in PowerShell script on GitHub
- **Samsung 2022**: Leaked SmartThings secrets via accidental git push
- **CircleCI 2023**: Rotated all customer secrets after infrastructure breach

Documentation follows the standard learn/ template: 00-OVERVIEW, 01-CONCEPTS, 02-ARCHITECTURE, 03-IMPLEMENTATION, 04-CHALLENGES.
