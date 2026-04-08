import { Map, UtensilsCrossed, CalendarDays, Compass } from 'lucide-react'
import { useStore, type Page } from './store/useStore'
import Home from './pages/Home'
import Destinations from './pages/Destinations'
import Restaurants from './pages/Restaurants'
import Calendar from './pages/Calendar'

const NAV_ITEMS: { page: Page; label: string; Icon: typeof Map }[] = [
  { page: 'home', label: 'Início', Icon: Compass },
  { page: 'destinations', label: 'Destinos', Icon: Map },
  { page: 'restaurants', label: 'Restaurantes', Icon: UtensilsCrossed },
  { page: 'calendar', label: 'Roteiro', Icon: CalendarDays },
]

function App() {
  const { currentPage, setCurrentPage, toast } = useStore()

  const renderPage = () => {
    switch (currentPage) {
      case 'home': return <Home />
      case 'destinations': return <Destinations />
      case 'restaurants': return <Restaurants />
      case 'calendar': return <Calendar />
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
              <Icon
                size={22}
                className="nav-icon"
                strokeWidth={active ? 2.5 : 1.8}
              />
              <span className="nav-label">{label}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}

export default App
