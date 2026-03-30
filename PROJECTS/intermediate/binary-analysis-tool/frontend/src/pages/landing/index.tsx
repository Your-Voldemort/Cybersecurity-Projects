// ===================
// © AngelaMos | 2026
// index.tsx
// ===================

import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { useUpload } from '@/api'
import { formatBytes } from '@/core/lib'
import styles from './landing.module.scss'

const HEX_OFFSETS = Array.from(
  { length: 16 },
  (_, i) => `0x${(i * 16).toString(16).toUpperCase().padStart(4, '0')}`
)

const ANALYSIS_PASSES = [
  { id: '01', name: 'FORMAT' },
  { id: '02', name: 'IMPORTS' },
  { id: '03', name: 'STRINGS' },
  { id: '04', name: 'ENTROPY' },
  { id: '05', name: 'DISASM' },
  { id: '06', name: 'THREAT' },
] as const

export function Component(): React.ReactElement {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const upload = useUpload()

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }, [])

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    const related = e.relatedTarget as Node | null
    if (related && e.currentTarget.contains(related)) return
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) setFile(droppedFile)
  }, [])

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0]
      if (selected) setFile(selected)
    },
    []
  )

  const handleSubmit = useCallback(() => {
    if (!file) return
    upload.mutate(file, {
      onSuccess: (data) => navigate(`/analysis/${data.slug}`),
      onError: () => toast.error('Failed to analyze binary'),
    })
  }, [file, upload, navigate])

  const handleClear = useCallback(() => {
    setFile(null)
    upload.reset()
    if (inputRef.current) inputRef.current.value = ''
  }, [upload])

  return (
    <div className={styles.page}>
      <div className={styles.hexMargin} aria-hidden="true">
        {HEX_OFFSETS.map((offset) => (
          <span key={offset}>{offset}</span>
        ))}
      </div>

      <div className={styles.cornerTL} aria-hidden="true" />
      <div className={styles.cornerTR} aria-hidden="true" />
      <div className={styles.cornerBL} aria-hidden="true" />
      <div className={styles.cornerBR} aria-hidden="true" />

      <header className={styles.metaStrip}>
        <span>AXM-001</span>
        <span className={styles.metaCenter}>STATIC ANALYSIS SUITE</span>
        <span>v0.1.0</span>
      </header>

      <div className={styles.rule} />

      <section className={styles.hero}>
        <h1 className={styles.title}>AXUMORTEM</h1>
        <p className={styles.subtitle}>BINARY DISSECTION ENGINE</p>
        <p className={styles.formats}>
          <span>ELF</span>
          <span className={styles.formatDivider}>/</span>
          <span>PE</span>
          <span className={styles.formatDivider}>/</span>
          <span>MACH-O</span>
        </p>
      </section>

      <section className={styles.intake}>
        <div className={styles.intakeHeader}>
          <span className={styles.intakeLabel}>SPECIMEN INTAKE</span>
          {file && (
            <button
              type="button"
              className={styles.clearBtn}
              onClick={handleClear}
            >
              CLEAR
            </button>
          )}
        </div>

        <section
          className={`${styles.dropZone} ${isDragging ? styles.dragActive : ''} ${file ? styles.hasFile : ''}`}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          aria-label="File drop zone"
        >
          <input ref={inputRef} type="file" hidden onChange={handleFileSelect} />

          {file ? (
            <div className={styles.fileInfo}>
              <div className={styles.fileField}>
                <span className={styles.fieldLabel}>FILE</span>
                <span className={styles.fieldValue}>{file.name}</span>
              </div>
              <div className={styles.fileField}>
                <span className={styles.fieldLabel}>SIZE</span>
                <span className={styles.fieldValue}>
                  {formatBytes(file.size)}
                </span>
              </div>
              <div className={styles.fileField}>
                <span className={styles.fieldLabel}>TYPE</span>
                <span className={styles.fieldValue}>
                  {file.type || 'application/octet-stream'}
                </span>
              </div>
            </div>
          ) : (
            <button
              type="button"
              className={styles.dropPrompt}
              onClick={() => inputRef.current?.click()}
            >
              <span className={styles.dropStatus}>AWAITING SPECIMEN</span>
              <span className={styles.dropInstruction}>
                DRAG + DROP BINARY / CLICK TO BROWSE
              </span>
            </button>
          )}
        </section>

        {file && (
          <button
            type="button"
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={upload.isPending}
          >
            {upload.isPending ? 'ANALYZING\u2026' : 'SUBMIT SPECIMEN'}
          </button>
        )}
      </section>

      <div className={styles.dashedRule} />

      <section className={styles.pipeline}>
        <span className={styles.pipelineLabel}>ANALYSIS PIPELINE</span>
        <div className={styles.passes}>
          {ANALYSIS_PASSES.map((pass) => (
            <div key={pass.id} className={styles.pass}>
              <span className={styles.passNumber}>{pass.id}</span>
              <span className={styles.passName}>{pass.name}</span>
            </div>
          ))}
        </div>
      </section>

      <div className={styles.rule} />

      <footer className={styles.footer}>
        <span>&copy; ANGELAMOS 2026</span>
        <span>AXUMORTEM</span>
      </footer>
    </div>
  )
}

Component.displayName = 'Landing'
