// ===================
// © AngelaMos | 2026
// severity-badge.tsx
// ===================

import styles from './severity-badge.module.scss'

interface SeverityBadgeProps {
  severity: 'HIGH' | 'MEDIUM' | 'LOW'
}

export function SeverityBadge({
  severity,
}: SeverityBadgeProps): React.ReactElement {
  return (
    <span className={`${styles.badge} ${styles[severity.toLowerCase()]}`}>
      {severity}
    </span>
  )
}
