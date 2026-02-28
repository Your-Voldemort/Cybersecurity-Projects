// ===================
// © AngelaMos | 2026
// alert-feed.tsx
// ===================

import { useEffect, useRef } from 'react'
import type { WebSocketAlert } from '@/api/types'
import { SeverityBadge } from './severity-badge'
import styles from './alert-feed.module.scss'

interface AlertFeedProps {
  alerts: WebSocketAlert[]
  isConnected: boolean
  maxHeight?: string
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}

export function AlertFeed({
  alerts,
  isConnected,
  maxHeight,
}: AlertFeedProps): React.ReactElement {
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = 0
    }
  }, [alerts.length])

  return (
    <div className={styles.feed}>
      <div className={styles.header}>
        <h3 className={styles.title}>Live Alerts</h3>
        <span
          className={`${styles.status} ${isConnected ? styles.connected : styles.disconnected}`}
        />
      </div>

      <div
        ref={listRef}
        className={styles.list}
        style={maxHeight ? { maxHeight } : undefined}
      >
        {alerts.length === 0 ? (
          <div className={styles.empty}>Waiting for alerts...</div>
        ) : (
          alerts.map((alert, i) => (
            <div key={`${alert.timestamp}-${i}`} className={styles.row}>
              <span className={styles.time}>
                {formatTime(alert.timestamp)}
              </span>
              <span className={styles.ip}>{alert.source_ip}</span>
              <span className={styles.path}>{alert.request_path}</span>
              <SeverityBadge
                severity={alert.severity as 'HIGH' | 'MEDIUM' | 'LOW'}
              />
              <span className={styles.score}>
                {alert.threat_score.toFixed(2)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
