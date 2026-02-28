// ===================
// © AngelaMos | 2026
// threat-detail.tsx
// ===================

import { LuX } from 'react-icons/lu'
import type { ThreatEvent } from '@/api/types'
import { SeverityBadge } from './severity-badge'
import styles from './threat-detail.module.scss'

interface ThreatDetailProps {
  threat: ThreatEvent | null
  onClose: () => void
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

export function ThreatDetail({
  threat,
  onClose,
}: ThreatDetailProps): React.ReactElement | null {
  if (!threat) return null

  return (
    <div className={styles.overlay} onClick={onClose} onKeyDown={() => {}}>
      <div
        className={styles.panel}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={() => {}}
      >
        <div className={styles.header}>
          <h2 className={styles.title}>Threat Details</h2>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close"
          >
            <LuX />
          </button>
        </div>

        <div className={styles.body}>
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Overview</h3>
            <div className={styles.grid}>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Severity</span>
                <SeverityBadge severity={threat.severity} />
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Threat Score</span>
                <span className={styles.fieldValue}>
                  {threat.threat_score.toFixed(4)}
                </span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Detected</span>
                <span className={styles.fieldValue}>
                  {formatDate(threat.created_at)}
                </span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Reviewed</span>
                <span className={styles.fieldValue}>
                  {threat.reviewed ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Request</h3>
            <div className={styles.grid}>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Source IP</span>
                <span className={styles.mono}>{threat.source_ip}</span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Method</span>
                <span className={styles.fieldValue}>
                  {threat.request_method}
                </span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Path</span>
                <span className={styles.mono}>{threat.request_path}</span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Status</span>
                <span className={styles.fieldValue}>
                  {threat.status_code}
                </span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>Response Size</span>
                <span className={styles.fieldValue}>
                  {threat.response_size} B
                </span>
              </div>
              <div className={styles.field}>
                <span className={styles.fieldLabel}>User Agent</span>
                <span className={styles.mono}>{threat.user_agent}</span>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Component Scores</h3>
            <div className={styles.scores}>
              {Object.entries(threat.component_scores).map(([key, val]) => (
                <div key={key} className={styles.scoreRow}>
                  <span className={styles.scoreLabel}>{key}</span>
                  <div className={styles.scoreBar}>
                    <div
                      className={styles.scoreFill}
                      style={{ width: `${Math.min(val * 100, 100)}%` }}
                    />
                  </div>
                  <span className={styles.scoreValue}>{val.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </section>

          {threat.geo.country && (
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Geolocation</h3>
              <div className={styles.grid}>
                <div className={styles.field}>
                  <span className={styles.fieldLabel}>Country</span>
                  <span className={styles.fieldValue}>
                    {threat.geo.country}
                  </span>
                </div>
                {threat.geo.city && (
                  <div className={styles.field}>
                    <span className={styles.fieldLabel}>City</span>
                    <span className={styles.fieldValue}>
                      {threat.geo.city}
                    </span>
                  </div>
                )}
              </div>
            </section>
          )}

          {threat.matched_rules && threat.matched_rules.length > 0 && (
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Matched Rules</h3>
              <div className={styles.rules}>
                {threat.matched_rules.map((rule) => (
                  <span key={rule} className={styles.rule}>
                    {rule}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
