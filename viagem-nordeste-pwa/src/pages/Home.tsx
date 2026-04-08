import { useState } from 'react'
import {
  Search,
  Bell,
  ChevronDown,
  Plus,
  Star,
  MapPin,
  Waves,
  Bus,
  UtensilsCrossed,
  Hotel,
  TreePine,
  Landmark,
} from 'lucide-react'
import { useStore } from '../store/useStore'
import ProfileModal from '../components/ProfileModal'
import WeatherWidget from '../components/WeatherWidget'
import RouteMap from '../components/RouteMap'
import EmergencyContacts from '../components/EmergencyContacts'

/* ============================================================
   DATA
   ============================================================ */

const CATEGORIES = [
  { label: 'Todos', Icon: null },
  { label: 'Praias', Icon: Waves },
  { label: 'Passeios', Icon: Bus },
  { label: 'Restaurantes', Icon: UtensilsCrossed },
  { label: 'Hotéis', Icon: Hotel },
  { label: 'Natureza', Icon: TreePine },
  { label: 'Cultura', Icon: Landmark },
]

const BANNERS = [
  {
    id: 'b1',
    title: 'Passeio de Buggy',
    subtitle: 'Dunas de Genipabu · Natal',
    badge: 'Imperdível',
    badgeColor: '#FBBF24',
    badgeText: '#0F172A',
    imageUrl: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&q=80',
  },
  {
    id: 'b2',
    title: 'Praia de Pipa',
    subtitle: 'Falésias + Golfinhos · 85 km',
    badge: 'Top Rated',
    badgeColor: '#0EA5E9',
    badgeText: '#FFFFFF',
    imageUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
  },
  {
    id: 'b3',
    title: 'Camarões Restaurante',
    subtitle: 'Frutos do Mar Premium · Natal',
    badge: '4.8 ★',
    badgeColor: '#FF6B6B',
    badgeText: '#FFFFFF',
    imageUrl: 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=80',
  },
  {
    id: 'b4',
    title: 'Centro Histórico JP',
    subtitle: 'Igrejas Barrocas · João Pessoa',
    badge: 'Cultural',
    badgeColor: '#10B981',
    badgeText: '#FFFFFF',
    imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
  },
]

const MOCK_HOTELS = [
  {
    id: 'h1',
    name: 'Serhs Natal Grand Hotel',
    imageUrl: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&q=80',
    category: 'Resort 5 Estrelas',
    rating: 4.8,
    distance: 'Beira-mar (Via Costeira)',
    priceLevel: '$$$$'
  },
  {
    id: 'h2',
    name: 'Boutique Hotel Pipa',
    imageUrl: 'https://images.unsplash.com/photo-1549294413-26f195200c16?w=600&q=80',
    category: 'Pousada Boutique',
    rating: 4.9,
    distance: '300m do centro',
    priceLevel: '$$$'
  }
]

/* ============================================================
   PREMIUM CARD COMPONENT
   ============================================================ */

interface PremiumCardProps {
  imageUrl: string
  name: string
  category: string
  rating: number
  distance: string
  priceLevel: string
  isSuggestion?: boolean
  onAdd: () => void
}

function PremiumCard({ imageUrl, name, category, rating, distance, priceLevel, isSuggestion, onAdd }: PremiumCardProps) {
  return (
    <div className="premium-card">
      <img src={imageUrl} alt={name} className="premium-card-img" loading="lazy" />
      <div className="premium-card-body">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="premium-card-category">{category}</span>
          {isSuggestion && (
            <span style={{
              fontSize: 9,
              fontWeight: 700,
              background: '#FEF3C7',
              color: '#D97706',
              padding: '1px 6px',
              borderRadius: 'var(--radius-full)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}>
              💬 Sugestão
            </span>
          )}
        </div>
        <span className="premium-card-name">{name}</span>
        <div className="premium-card-meta">
          <span className="rating">
            <Star size={13} fill="#FBBF24" color="#FBBF24" className="rating-star" />
            {rating.toFixed(1)}
          </span>
          <span className="meta-dot" />
          <span className="distance">
            <MapPin size={11} style={{ display: 'inline', marginRight: 2 }} />
            {distance}
          </span>
          <span className="meta-dot" />
          <span className="price-tag">{priceLevel}</span>
        </div>
      </div>
      <button className="add-btn" onClick={onAdd} aria-label={`Adicionar ${name} ao roteiro`}>
        <Plus size={18} />
      </button>
    </div>
  )
}

/* ============================================================
   HOME PAGE
   ============================================================ */

export default function Home() {
  const {
    currentTraveler,
    destinations,
    restaurants,
    activeCategory,
    setActiveCategory,
    setCurrentPage,
    setShowProfileModal,
    showProfileModal,
    showToast,
    setShowAddModal,
  } = useStore()

  const [_searchQuery, setSearchQuery] = useState('')

  // Filter destinations by active category
  const filteredDestinations = destinations.filter((d) => {
    if (activeCategory === 'Todos') return true
    if (activeCategory === 'Praias') return d.category === 'Praia'
    if (activeCategory === 'Passeios') return d.category === 'Passeio'
    if (activeCategory === 'Hotéis') return d.category === 'Hotel'
    if (activeCategory === 'Natureza') return d.category === 'Natureza'
    if (activeCategory === 'Cultura') return d.category === 'Cultura'
    return false
  })

  const filteredRestaurants = restaurants.filter(
    () => activeCategory === 'Todos' || activeCategory === 'Restaurantes',
  )

  const showRestaurants = activeCategory === 'Todos' || activeCategory === 'Restaurantes'
  const showDestinations = activeCategory !== 'Restaurantes'

  const handleAddDestination = (name: string) => {
    showToast(`"${name}" adicionado ao roteiro!`)
    setShowAddModal(true)
    setTimeout(() => setShowAddModal(false), 100)
  }

  return (
    <>
      {/* Header */}
      <header className="home-header">
        <button
          className="trip-selector"
          onClick={() => setCurrentPage('calendar')}
        >
          <span className="trip-dot" />
          Viagem: Natal
          <ChevronDown size={14} color="var(--color-text-muted)" />
        </button>
        <div style={{ paddingLeft: '22px', marginTop: '2px' }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-primary)' }}>
            Faltam 12 dias! ✈️
          </span>
        </div>

        <div className="header-right">
          <button className="icon-btn" aria-label="Notificações">
            <Bell size={18} />
            <span className="badge" />
          </button>
          <button
            className="avatar avatar-md"
            style={{ background: currentTraveler.color }}
            onClick={() => setShowProfileModal(true)}
            aria-label="Perfil do viajante"
          >
            {currentTraveler.initials}
          </button>
        </div>
      </header>

      {/* Search */}
      <section className="search-section">
        <div className="search-bar">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Buscar destinos, restaurantes..."
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Busca"
          />
        </div>
      </section>

      {/* Weather & Ocean Widget */}
      <section className="px-6">
        <WeatherWidget />
      </section>

      {/* Categories */}
      <div className="chips-scroll">
        {CATEGORIES.map(({ label, Icon }) => (
          <button
            key={label}
            className={`chip${activeCategory === label ? ' active' : ''}`}
            onClick={() => setActiveCategory(label)}
          >
            {Icon && <Icon size={14} />}
            {label}
          </button>
        ))}
      </div>

      {/* Banner Carousel */}
      <section>
        <div className="section-header">
          <span className="section-title">Em destaque</span>
          <button className="see-all-btn" onClick={() => setCurrentPage('destinations')}>
            Ver todos
          </button>
        </div>
        <div className="banner-scroll">
          {BANNERS.map((b) => (
            <div key={b.id} className="banner-card">
              <img src={b.imageUrl} alt={b.title} loading="lazy" />
              <div className="banner-overlay">
                <span
                  className="banner-badge"
                  style={{ background: b.badgeColor, color: b.badgeText }}
                >
                  {b.badge}
                </span>
                <span className="banner-title">{b.title}</span>
                <span className="banner-subtitle">{b.subtitle}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Destinations Feed */}
      {showDestinations && filteredDestinations.length > 0 && (
        <section>
          <div className="section-header">
            <span className="section-title">
              {activeCategory === 'Todos' ? 'Destinos famosos' : activeCategory}
            </span>
            <button className="see-all-btn" onClick={() => setCurrentPage('destinations')}>
              Ver todos
            </button>
          </div>
          <div className="feed-section">
            {filteredDestinations.slice(0, 5).map((d) => (
              <PremiumCard
                key={d.id}
                imageUrl={d.imageUrl}
                name={d.name}
                category={d.category}
                rating={d.rating}
                distance={d.distance}
                priceLevel={d.priceLevel}
                isSuggestion={d.description.startsWith('Sugestão do grupo')}
                onAdd={() => handleAddDestination(d.name)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Restaurants Feed */}
      {showRestaurants && filteredRestaurants.length > 0 && (
        <section>
          <div className="section-header">
            <span className="section-title">Restaurantes em alta</span>
            <button className="see-all-btn" onClick={() => setCurrentPage('restaurants')}>
              Ver todos
            </button>
          </div>
          <div className="feed-section">
            {filteredRestaurants.slice(0, 3).map((r) => (
              <PremiumCard
                key={r.id}
                imageUrl={r.imageUrl}
                name={r.name}
                category={r.cuisine}
                rating={r.rating}
                distance={r.distance}
                priceLevel={r.priceLevel}
                isSuggestion={r.description.startsWith('Sugestão do grupo')}
                onAdd={() => handleAddDestination(r.name)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Hotels Feed */}
      {(activeCategory === 'Todos' || activeCategory === 'Hotéis') && (
        <section>
          <div className="section-header">
            <span className="section-title">Onde se hospedar</span>
          </div>
          <div className="feed-section">
            {MOCK_HOTELS.map((h) => (
              <PremiumCard
                key={h.id}
                imageUrl={h.imageUrl}
                name={h.name}
                category={h.category}
                rating={h.rating}
                distance={h.distance}
                priceLevel={h.priceLevel}
                onAdd={() => handleAddDestination(h.name)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Route Map */}
      <section className="px-6 mt-4">
        <RouteMap />
      </section>

      {/* Emergency Contacts */}
      <EmergencyContacts />

      {/* Profile Modal */}
      {showProfileModal && <ProfileModal />}
    </>
  )
}
