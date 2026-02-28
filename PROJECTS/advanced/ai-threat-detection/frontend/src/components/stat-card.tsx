// ===================
// © AngelaMos | 2026
// stat-card.tsx
// ===================

import styles from './stat-card.module.scss'

interface StatCardProps {
  label: string
  value: string | number
  sublabel?: string
}

export function StatCard({
  label,
  value,
  sublabel,
}: StatCardProps): React.ReactElement {
  return (
    <div className={styles.card}>
      <span className={styles.value}>{value}</span>
      <span className={styles.label}>{label}</span>
      {sublabel && <span className={styles.sublabel}>{sublabel}</span>}
    </div>
  )
}
