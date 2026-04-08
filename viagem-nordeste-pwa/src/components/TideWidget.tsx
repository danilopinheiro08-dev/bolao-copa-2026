import { useEffect, useState } from 'react'
import { Waves } from 'lucide-react'
import { getTidesForDay, getNextTide, type DayTideData, type TideCity } from '../services/tideService'

interface TideWidgetProps {
  date: string
  city: TideCity
  compact?: boolean
}

export default function TideWidget({ date, city, compact = false }: TideWidgetProps) {
  const [data, setData] = useState<DayTideData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getTidesForDay(date, city).then((d) => {
      setData(d)
      setLoading(false)
    })
  }, [date, city])

  if (loading) {
    return (
      <div style={{ padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-text-muted)' }}>
        <Waves size={14} />
        <span style={{ fontSize: 'var(--font-size-xs)' }}>Carregando marés…</span>
      </div>
    )
  }

  if (!data) return null

  const next = getNextTide(data.entries)
  const sorted = [...data.entries].sort((a, b) => {
    const [ah, am] = a.time.split(':').map(Number)
    const [bh, bm] = b.time.split(':').map(Number)
    return ah * 60 + am - (bh * 60 + bm)
  })

  if (compact) {
    // Versão compacta para cards de destino
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        padding: '4px 10px',
        background: 'rgba(14,165,233,0.08)',
        borderRadius: 'var(--radius-full)',
        width: 'fit-content',
        marginTop: 4,
      }}>
        <Waves size={11} color="var(--color-primary)" />
        {next && (
          <span style={{ fontSize: 10, fontWeight: 600, color: 'var(--color-primary)' }}>
            {next.type === 'high' ? '▲ Alta' : '▼ Baixa'} {next.time} · {next.height}m
          </span>
        )}
      </div>
    )
  }

  // Versão completa para o calendário
  const maxHeight = Math.max(...data.entries.map((e) => e.height))

  return (
    <div style={{
      margin: '0 var(--space-5) var(--space-4)',
      background: 'linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-4)',
      color: 'white',
      overflow: 'hidden',
      position: 'relative',
    }}>
      {/* Background wave decoration */}
      <svg
        style={{ position: 'absolute', bottom: 0, left: 0, right: 0, opacity: 0.12 }}
        viewBox="0 0 400 60"
        preserveAspectRatio="none"
        height={60}
      >
        <path
          d="M0,30 C50,10 100,50 150,30 C200,10 250,50 300,30 C350,10 400,50 400,30 L400,60 L0,60 Z"
          fill="white"
        />
      </svg>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Waves size={16} />
          <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700 }}>
            Tábua das Marés · {city}
          </span>
        </div>
        {next && (
          <span style={{
            fontSize: 10,
            fontWeight: 700,
            background: 'rgba(255,255,255,0.25)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-full)',
          }}>
            Próxima: {next.type === 'high' ? '▲' : '▼'} {next.time}
          </span>
        )}
      </div>

      {/* Tide bars */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', height: 64, position: 'relative', zIndex: 1 }}>
        {sorted.map((entry, i) => {
          const pct = (entry.height / (maxHeight * 1.1)) * 100
          const isHigh = entry.type === 'high'
          return (
            <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
              {/* Height label */}
              <span style={{ fontSize: 9, fontWeight: 700, color: 'rgba(255,255,255,0.9)', whiteSpace: 'nowrap' }}>
                {entry.height.toFixed(1)}m
              </span>
              {/* Bar */}
              <div style={{
                width: '100%',
                height: `${pct * 0.5}px`,
                background: isHigh
                  ? 'rgba(255,255,255,0.95)'
                  : 'rgba(255,255,255,0.35)',
                borderRadius: '3px 3px 0 0',
                minHeight: 4,
                transition: 'height 0.5s ease',
              }} />
              {/* Time */}
              <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.85)', fontWeight: 600, whiteSpace: 'nowrap' }}>
                {entry.time}
              </span>
              {/* Type label */}
              <span style={{
                fontSize: 8,
                fontWeight: 700,
                color: isHigh ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.6)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                {isHigh ? 'Alta' : 'Baixa'}
              </span>
            </div>
          )
        })}
      </div>

      {/* Footer note */}
      <div style={{
        marginTop: 10,
        paddingTop: 8,
        borderTop: '1px solid rgba(255,255,255,0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'relative',
        zIndex: 1,
      }}>
        <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.7)', fontStyle: 'italic' }}>
          Horários em BRT (UTC-3)
        </span>
        <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.7)' }}>
          DHN · Litoral Nordestino
        </span>
      </div>
    </div>
  )
}
