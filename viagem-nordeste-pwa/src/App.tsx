import { useEffect, useCallback } from 'react'
import { Map, UtensilsCrossed, CalendarDays, Compass } from 'lucide-react'
import { useStore, type Page } from './store/useStore'
import Home from './pages/Home'
import Destinations from './pages/Destinations'
import Restaurants from './pages/Restaurants'
import Calendar from './pages/Calendar'
import {
  requestNotificationPermission,
  showBrowserNotification,
  listenBroadcast,
  NTFY_TOPIC,
  type BroadcastPayload,
} from './services/notificationService'

const NAV_ITEMS: { page: Page; label: string; Icon: typeof Map }[] = [
  { page: 'home',         label: 'Início',      Icon: Compass },
  { page: 'destinations', label: 'Destinos',    Icon: Map },
  { page: 'restaurants',  label: 'Restaurantes',Icon: UtensilsCrossed },
  { page: 'calendar',     label: 'Roteiro',     Icon: CalendarDays },
]

function App() {
  const { currentPage, setCurrentPage, toast, showToast } = useStore()

  // ── Solicitar permissão de notificação na primeira carga ─────────────────
  useEffect(() => {
    // Aguarda interação do usuário para pedir permissão (melhora UX)
    const timer = setTimeout(async () => {
      const perm = await requestNotificationPermission()
      if (perm === 'granted') {
        console.info(`[ViagemNE] Notificações ativadas. Tópico ntfy: ${NTFY_TOPIC}`)
      }
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  // ── BroadcastChannel: receber eventos de outras abas do mesmo dispositivo ─
  const handleBroadcast = useCallback((payload: BroadcastPayload) => {
    if (payload.type === 'new-event') {
      showBrowserNotification(
        '📅 Roteiro atualizado!',
        `${payload.travelerName} adicionou "${payload.title}" às ${payload.time}.`,
      )
      showToast(`${payload.travelerName} adicionou "${payload.title}" ao roteiro!`)
    }
  }, [showToast])

  useEffect(() => {
    const unsub = listenBroadcast(handleBroadcast)
    return unsub
  }, [handleBroadcast])

  const renderPage = () => {
    switch (currentPage) {
      case 'home':         return <Home />
      case 'destinations': return <Destinations />
      case 'restaurants':  return <Restaurants />
      case 'calendar':     return <Calendar />
    }
  }

  return (
    <div className="app-shell">
      {/* Toast */}
      {toast && (
        <div className="toast">
          <span>✓</span>
          {toast}
        </div>
      )}

      {/* Page Content */}
      <main className="page-content">
        {renderPage()}
      </main>

      {/* Bottom Navigation */}
      <nav className="bottom-nav">
        {NAV_ITEMS.map(({ page, label, Icon }) => {
          const active = currentPage === page
          return (
            <button
              key={page}
              className={`nav-item${active ? ' active' : ''}`}
              onClick={() => setCurrentPage(page)}
              aria-label={label}
            >
              {active && <span className="nav-active-dot" />}
              <Icon size={22} className="nav-icon" strokeWidth={active ? 2.5 : 1.8} />
              <span className="nav-label">{label}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}

export default App
