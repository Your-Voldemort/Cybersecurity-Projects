// ===================
// © AngelaMos | 2026
// tab-entropy.tsx
// ===================

import type { AnalysisResponse, SectionEntropy } from '@/api'
import { ENTROPY_CLASSIFICATION_COLORS } from '@/config'
import styles from './analysis.module.scss'

const MAX_ENTROPY = 8

function EntropyBar({
  section,
}: {
  section: SectionEntropy
}): React.ReactElement {
  const pct = (section.entropy / MAX_ENTROPY) * 100
  const color = ENTROPY_CLASSIFICATION_COLORS[section.classification] ?? '#888'

  return (
    <div
      className={`${styles.entropyRow} ${section.is_anomalous ? styles.anomalous : ''}`}
    >
      <div className={styles.entropyMeta}>
        <span className={styles.entropySectionName}>{section.name}</span>
        <span className={styles.entropyClassification} style={{ color }}>
          {section.classification}
        </span>
      </div>
      <div className={styles.entropyBarWrap}>
        <div className={styles.entropyBarTrack}>
          <div
            className={styles.entropyBarFill}
            style={{ width: `${pct}%`, background: color }}
          />
        </div>
        <span className={styles.entropyValue}>{section.entropy.toFixed(2)}</span>
      </div>
      <div className={styles.entropyDetails}>
        <span className={styles.entropyDetail}>
          SIZE {section.size.toLocaleString()}
        </span>
        <span className={styles.entropyDetail}>
          V/R {section.virtual_to_raw_ratio.toFixed(2)}
        </span>
        {section.flags.length > 0 && (
          <div className={styles.entropyFlags}>
            {section.flags.map((flag) => (
              <span key={flag} className={styles.entropyFlag}>
                {flag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export function TabEntropy({
  data,
}: {
  data: AnalysisResponse
}): React.ReactElement {
  const ent = data.passes.entropy

  if (!ent) {
    return (
      <div className={styles.tabPanel}>
        <span className={styles.noData}>No entropy data available</span>
      </div>
    )
  }

  return (
    <div className={styles.tabPanel}>
      <div className={styles.entropyOverall}>
        <span className={styles.entropyOverallLabel}>OVERALL ENTROPY</span>
        <span className={styles.entropyOverallValue}>
          {ent.overall_entropy.toFixed(4)}
        </span>
        <span className={styles.entropyOverallScale}>/ {MAX_ENTROPY}</span>
      </div>

      {ent.packing_detected && (
        <div className={styles.packingAlert}>
          <span className={styles.packingTitle}>PACKING DETECTED</span>
          {ent.packer_name && (
            <span className={styles.packingName}>{ent.packer_name}</span>
          )}
          {ent.packing_indicators.map((ind, i) => (
            <div key={`ind-${i.toString()}`} className={styles.packingIndicator}>
              <span className={styles.packingType}>{ind.indicator_type}</span>
              <span className={styles.packingEvidence}>{ind.description}</span>
            </div>
          ))}
        </div>
      )}

      <section className={styles.overviewSection}>
        <span className={styles.sectionLabel}>PER-SECTION ENTROPY</span>
        <div className={styles.entropyBars}>
          {ent.sections.map((sec) => (
            <EntropyBar key={sec.name} section={sec} />
          ))}
        </div>
      </section>
    </div>
  )
}
