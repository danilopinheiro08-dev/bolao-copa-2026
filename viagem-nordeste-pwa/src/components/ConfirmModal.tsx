import { X, Check, CalendarDays } from 'lucide-react'
import type { Traveler } from '../store/useStore'

interface ConfirmModalProps {
  title: string
  subtitle: string
  time: string
  date: string
  traveler: Traveler
  onConfirm: () => void
  onCancel: () => void
}

const DATE_LABELS: Record<string, string> = {
  '2026-04-10': 'Sex, 10 de Abril',
  '2026-04-11': 'Sáb, 11 de Abril',
  '2026-04-12': 'Dom, 12 de Abril',
  '2026-04-13': 'Seg, 13 de Abril',
  '2026-04-14': 'Ter, 14 de Abril',
  '2026-04-15': 'Qua, 15 de Abril',
  '2026-04-16': 'Qui, 16 de Abril',
  '2026-04-17': 'Sex, 17 de Abril',
  '2026-04-18': 'Sáb, 18 de Abril',
  '2026-04-19': 'Dom, 19 de Abril',
}

export default function ConfirmModal({
  title,
  subtitle,
  time,
  date,
  traveler,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  const dateLabel = DATE_LABELS[date] ?? date

  return (
    <>
      <div className="modal-overlay" onClick={onCancel} />
      <div className="bottom-sheet" style={{ maxHeight: '60dvh' }}>
        <div className="bottom-sheet-handle">
          <span className="handle-bar" />
        </div>

        {/* Header */}
        <div className="bottom-sheet-header">
          <span className="bottom-sheet-title">Confirmar evento?</span>
          <button className="close-btn" onClick={onCancel} aria-label="Cancelar">
            <X size={16} />
          </button>
        </div>

        {/* Preview card */}
        <div style={{ padding: 'var(--space-5) var(--space-6)' }}>
          <div style={{
            background: 'var(--color-surface-alt)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-4)',
            borderLeft: `4px solid ${traveler.color}`,
            display: 'flex',
            gap: 'var(--space-3)',
            alignItems: 'flex-start',
          }}>
            <CalendarDays size={20} color={traveler.color} style={{ flexShrink: 0, marginTop: 2 }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-size-base)', color: 'var(--color-text-primary)', marginBottom: 2 }}>
                {title}
              </div>
              {subtitle && (
                <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)', marginBottom: 6 }}>
                  {subtitle}
                </div>
              )}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                <span style={{
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                  background: `${traveler.color}18`,
                  color: traveler.color,
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-full)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}>
                  <span
                    style={{
                      width: 16,
                      height: 16,
                      borderRadius: '50%',
                      background: traveler.color,
                      color: 'white',
                      fontSize: 8,
                      fontWeight: 800,
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {traveler.initials}
                  </span>
                  {traveler.name}
                </span>
                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                  🕐 {time}
                </span>
                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                  📅 {dateLabel}
                </span>
              </div>
            </div>
          </div>

          <p style={{
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-muted)',
            marginTop: 'var(--space-4)',
            textAlign: 'center',
            lineHeight: 1.6,
          }}>
            O grupo será notificado sobre este novo evento.
          </p>
        </div>

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: 'var(--space-3)', padding: '0 var(--space-6) var(--space-6)' }}>
          <button
            onClick={onCancel}
            style={{
              flex: 1,
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-surface-alt)',
              color: 'var(--color-text-secondary)',
              fontWeight: 600,
              fontSize: 'var(--font-size-base)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
            }}
          >
            <X size={16} />
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            style={{
              flex: 2,
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-primary)',
              color: 'white',
              fontWeight: 700,
              fontSize: 'var(--font-size-base)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              boxShadow: 'var(--shadow-primary)',
            }}
          >
            <Check size={16} />
            Confirmar e notificar
          </button>
        </div>
      </div>
    </>
  )
}
