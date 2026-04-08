import { useState } from 'react'
import { Plus, CalendarDays, X, Clock, User } from 'lucide-react'
import { useStore } from '../store/useStore'

/* ============================================================
   TRIP DAYS — April 10–19, 2026 · JPA → Natal → Pipa → JP → JPA
   ============================================================ */

const TRIP_DAYS = [
  { date: '2026-04-10', weekday: 'Sex', number: 10, label: 'Chegada' },
  { date: '2026-04-11', weekday: 'Sáb', number: 11, label: 'Natal' },
  { date: '2026-04-12', weekday: 'Dom', number: 12, label: 'Natal' },
  { date: '2026-04-13', weekday: 'Seg', number: 13, label: 'Natal' },
  { date: '2026-04-14', weekday: 'Ter', number: 14, label: 'Pipa' },
  { date: '2026-04-15', weekday: 'Qua', number: 15, label: 'Pipa' },
  { date: '2026-04-16', weekday: 'Qui', number: 16, label: 'JP' },
  { date: '2026-04-17', weekday: 'Sex', number: 17, label: 'JP' },
  { date: '2026-04-18', weekday: 'Sáb', number: 18, label: 'JP' },
  { date: '2026-04-19', weekday: 'Dom', number: 19, label: 'Volta' },
]

/* ============================================================
   ADD EVENT MODAL (Bottom Sheet)
   ============================================================ */

function AddEventModal({ onClose }: { onClose: () => void }) {
  const { travelers, currentTraveler, addToCalendar, selectedDate } = useStore()
  const [title, setTitle] = useState('')
  const [subtitle, setSubtitle] = useState('')
  const [time, setTime] = useState('09:00')
  const [travelerId, setTravelerId] = useState(currentTraveler.id)

  const handleSubmit = () => {
    if (!title.trim()) return
    const traveler = travelers.find((t) => t.id === travelerId)!
    addToCalendar({
      date: selectedDate,
      time,
      title: title.trim(),
      subtitle: subtitle.trim() || 'Evento adicionado',
      travelerId,
      color: traveler.color,
    })
  }

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="bottom-sheet">
        <div className="bottom-sheet-handle">
          <span className="handle-bar" />
        </div>
        <div className="bottom-sheet-header">
          <span className="bottom-sheet-title">Novo evento</span>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">
            <X size={16} />
          </button>
        </div>
        <div className="bottom-sheet-body">
          {/* Title */}
          <div className="form-group">
            <label className="form-label">Nome do evento</label>
            <input
              className="form-input"
              type="text"
              placeholder="Ex: Praia de Pipa, Almoço..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>

          {/* Subtitle */}
          <div className="form-group">
            <label className="form-label">Detalhes (opcional)</label>
            <input
              className="form-input"
              type="text"
              placeholder="Ex: Reserva para 3 pessoas"
              value={subtitle}
              onChange={(e) => setSubtitle(e.target.value)}
            />
          </div>

          {/* Time */}
          <div className="form-group">
            <label className="form-label">Horário</label>
            <div style={{ position: 'relative' }}>
              <Clock
                size={16}
                style={{
                  position: 'absolute',
                  left: 16,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--color-text-muted)',
                  pointerEvents: 'none',
                }}
              />
              <input
                className="form-input"
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                style={{ paddingLeft: 44 }}
              />
            </div>
          </div>

          {/* Traveler selector */}
          <div className="form-group">
            <label className="form-label">Quem vai?</label>
            <div className="traveler-select">
              {travelers.map((t) => (
                <button
                  key={t.id}
                  className={`traveler-option${travelerId === t.id ? ' selected' : ''}`}
                  onClick={() => setTravelerId(t.id)}
                  style={
                    travelerId === t.id
                      ? {
                          borderColor: t.color,
                          background: `${t.color}15`,
                          color: t.color,
                        }
                      : {}
                  }
                >
                  <span
                    className="avatar avatar-sm"
                    style={{ background: t.color, width: 22, height: 22, fontSize: 9 }}
                  >
                    {t.initials}
                  </span>
                  {t.name}
                </button>
              ))}
            </div>
          </div>

          <button
            className="submit-btn"
            onClick={handleSubmit}
            disabled={!title.trim()}
            style={{ opacity: title.trim() ? 1 : 0.5 }}
          >
            Adicionar ao roteiro
          </button>
        </div>
      </div>
    </>
  )
}

/* ============================================================
   CALENDAR PAGE
   ============================================================ */

export default function Calendar() {
  const {
    calendarItems,
    selectedDate,
    setSelectedDate,
    travelers,
    removeFromCalendar,
    showToast,
  } = useStore()

  const [showAddModal, setShowAddModal] = useState(false)

  const dayItems = calendarItems
    .filter((item) => item.date === selectedDate)
    .sort((a, b) => a.time.localeCompare(b.time))

  const hasItemsOnDate = (date: string) => calendarItems.some((i) => i.date === date)

  const getTravelerById = (id: string) => travelers.find((t) => t.id === id)

  const handleRemove = (id: string, title: string) => {
    removeFromCalendar(id)
    showToast(`"${title}" removido do roteiro`)
  }

  const selectedDay = TRIP_DAYS.find((d) => d.date === selectedDate)
  const tripDayIndex = TRIP_DAYS.findIndex((d) => d.date === selectedDate)

  return (
    <>
      {/* Sticky Header */}
      <div className="calendar-header">
        <div className="calendar-header-top">
          <div>
            <div className="page-title">Roteiro</div>
            <div className="trip-month">
              {selectedDay
                ? `${selectedDay.label} · Dia ${tripDayIndex + 1} de ${TRIP_DAYS.length}`
                : 'Selecione um dia'}
            </div>
          </div>
          <div className="header-actions">
            <span
              style={{
                padding: '4px 12px',
                borderRadius: 'var(--radius-full)',
                background: 'var(--color-primary)',
                color: 'white',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 700,
              }}
            >
              Abr 2026
            </span>
          </div>
        </div>

        {/* Day Carousel */}
        <div className="day-carousel">
          {TRIP_DAYS.map((day) => (
            <button
              key={day.date}
              className={`day-item${selectedDate === day.date ? ' active' : ''}`}
              onClick={() => setSelectedDate(day.date)}
              aria-label={`Dia ${day.number} - ${day.label}`}
            >
              <span className="day-weekday">{day.weekday}</span>
              <span className="day-number">{day.number}</span>
              <span
                style={{
                  fontSize: 9,
                  fontWeight: 600,
                  opacity: selectedDate === day.date ? 0.85 : 0.55,
                  color: selectedDate === day.date ? 'white' : 'var(--color-text-muted)',
                  letterSpacing: '0.02em',
                  textTransform: 'uppercase',
                }}
              >
                {day.label}
              </span>
              {hasItemsOnDate(day.date) && <span className="day-dot" />}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="timeline">
        {dayItems.length === 0 ? (
          <div className="timeline-empty">
            <div className="timeline-empty-icon">
              <CalendarDays size={32} />
            </div>
            <span className="timeline-empty-title">Dia livre</span>
            <p className="timeline-empty-text">
              Nenhuma atividade planejada. Toque no botão{' '}
              <strong style={{ color: 'var(--color-secondary)' }}>+</strong> para adicionar.
            </p>
          </div>
        ) : (
          dayItems.map((item, index) => {
            const traveler = getTravelerById(item.travelerId)
            const isLast = index === dayItems.length - 1
            return (
              <div key={item.id} className="timeline-item">
                {/* Time column */}
                <div className="timeline-time-col">
                  <span className="timeline-time">{item.time}</span>
                  {!isLast && <span className="timeline-line" />}
                </div>

                {/* Card */}
                <div
                  className="timeline-card"
                  style={{ borderLeftColor: item.color }}
                >
                  <div className="timeline-card-body">
                    <div className="timeline-card-title">{item.title}</div>
                    <div className="timeline-card-sub">{item.subtitle}</div>
                    <div className="timeline-avatars">
                      {traveler && (
                        <div
                          className="timeline-avatar"
                          style={{ background: traveler.color }}
                          title={traveler.name}
                        >
                          {traveler.initials}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Thumbnail if present */}
                  {item.imageUrl && (
                    <img
                      src={item.imageUrl}
                      alt={item.title}
                      className="timeline-card-img"
                      loading="lazy"
                    />
                  )}

                  {/* Remove button */}
                  <button
                    onClick={() => handleRemove(item.id, item.title)}
                    style={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      background: 'var(--color-surface-alt)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--color-text-muted)',
                    }}
                    aria-label={`Remover ${item.title}`}
                  >
                    <X size={12} />
                  </button>
                </div>
              </div>
            )
          })
        )}

        {/* Summary row */}
        {dayItems.length > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-3)',
              padding: 'var(--space-4) var(--space-2)',
              color: 'var(--color-text-muted)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            <User size={14} />
            <span>
              {dayItems.length} atividade{dayItems.length > 1 ? 's' : ''} planejada
              {dayItems.length > 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* FAB */}
      <button
        className="fab"
        onClick={() => setShowAddModal(true)}
        aria-label="Adicionar evento"
      >
        <Plus size={24} />
      </button>

      {/* Add Event Modal */}
      {showAddModal && <AddEventModal onClose={() => setShowAddModal(false)} />}
    </>
  )
}
