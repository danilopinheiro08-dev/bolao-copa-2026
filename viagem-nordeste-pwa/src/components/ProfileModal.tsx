import { Check } from 'lucide-react'
import { useStore } from '../store/useStore'

export default function ProfileModal() {
  const { travelers, currentTraveler, setCurrentTraveler, setShowProfileModal } = useStore()

  return (
    <>
      <div
        className="modal-overlay"
        onClick={() => setShowProfileModal(false)}
      />
      <div className="bottom-sheet">
        <div className="bottom-sheet-handle">
          <span className="handle-bar" />
        </div>
        <div className="bottom-sheet-header">
          <span className="bottom-sheet-title">Trocar viajante</span>
          <button
            className="close-btn"
            onClick={() => setShowProfileModal(false)}
            aria-label="Fechar"
          >
            ✕
          </button>
        </div>
        <div className="profile-list">
          {travelers.map((t) => (
            <button
              key={t.id}
              className={`profile-item${t.id === currentTraveler.id ? ' active' : ''}`}
              onClick={() => setCurrentTraveler(t.id)}
            >
              <span
                className="avatar avatar-md"
                style={{ background: t.color }}
              >
                {t.initials}
              </span>
              <div>
                <div className="profile-item-name">{t.name}</div>
                <div className="profile-item-role">{t.role}</div>
              </div>
              {t.id === currentTraveler.id && (
                <Check size={18} className="profile-check" />
              )}
            </button>
          ))}
        </div>
      </div>
    </>
  )
}
