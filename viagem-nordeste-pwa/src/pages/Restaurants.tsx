import { useState } from 'react'
import { Star, MapPin, Plus } from 'lucide-react'
import { useStore } from '../store/useStore'

const CITY_FILTERS = ['Todos', 'Natal', 'Pipa', 'João Pessoa']
const PRICE_FILTERS = ['Todos', '$', '$$', '$$$']

export default function Restaurants() {
  const { restaurants, showToast } = useStore()
  const [cityFilter, setCityFilter] = useState('Todos')
  const [priceFilter, setPriceFilter] = useState('Todos')

  const filtered = restaurants.filter((r) => {
    const cityOk = cityFilter === 'Todos' || r.city === cityFilter
    const priceOk = priceFilter === 'Todos' || r.priceLevel === priceFilter
    return cityOk && priceOk
  })

  const handleAdd = (name: string) => {
    showToast(`"${name}" adicionado ao roteiro!`)
  }

  const priceLabel = (p: string) => {
    if (p === '$') return 'Econômico'
    if (p === '$$') return 'Moderado'
    return 'Premium'
  }

  return (
    <>
      <header className="page-header">
        <span className="page-title">Restaurantes</span>
        <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}>
          {filtered.length} locais
        </span>
      </header>

      {/* City filter */}
      <div className="filter-bar">
        {CITY_FILTERS.map((city) => (
          <button
            key={city}
            className={`chip${cityFilter === city ? ' active' : ''}`}
            onClick={() => setCityFilter(city)}
          >
            {city}
          </button>
        ))}
      </div>

      {/* Price filter */}
      <div className="filter-bar" style={{ paddingTop: 0 }}>
        {PRICE_FILTERS.map((p) => (
          <button
            key={p}
            className={`chip${priceFilter === p ? ' active' : ''}`}
            style={{
              background: priceFilter === p ? 'var(--color-accent)' : undefined,
              color: priceFilter === p ? 'var(--color-text-primary)' : undefined,
              boxShadow: priceFilter === p ? '0 4px 12px rgba(251,191,36,0.35)' : undefined,
            }}
            onClick={() => setPriceFilter(p)}
          >
            {p === 'Todos' ? 'Todos os preços' : `${p} ${priceLabel(p)}`}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="page-list">
        <div className="feed-section" style={{ margin: '0 var(--space-5) var(--space-4)', borderRadius: 'var(--radius-md)' }}>
          {filtered.map((r, i) => (
            <div
              key={r.id}
              className="premium-card"
              style={{ borderBottom: i === filtered.length - 1 ? 'none' : undefined }}
            >
              <img
                src={r.imageUrl}
                alt={r.name}
                className="premium-card-img"
                loading="lazy"
              />
              <div className="premium-card-body">
                <span className="premium-card-category">{r.cuisine}</span>
                <span className="premium-card-name">{r.name}</span>
                <p style={{
                  fontSize: 'var(--font-size-sm)',
                  color: 'var(--color-text-muted)',
                  marginTop: 2,
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {r.description}
                </p>
                <div className="premium-card-meta" style={{ marginTop: 6 }}>
                  <span className="rating">
                    <Star size={12} fill="#FBBF24" color="#FBBF24" />
                    {r.rating.toFixed(1)}
                  </span>
                  <span className="meta-dot" />
                  <span className="distance">
                    <MapPin size={11} style={{ display: 'inline', marginRight: 2 }} />
                    {r.distance}
                  </span>
                  <span className="meta-dot" />
                  <span className="price-tag">{r.priceLevel}</span>
                </div>
              </div>
              <button
                className="add-btn"
                onClick={() => handleAdd(r.name)}
                aria-label={`Adicionar ${r.name}`}
                style={{ background: 'var(--color-secondary)', boxShadow: 'var(--shadow-secondary)' }}
              >
                <Plus size={18} />
              </button>
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: 'var(--space-12) var(--space-5)',
            color: 'var(--color-text-muted)',
          }}>
            <div style={{ fontSize: 48, marginBottom: 'var(--space-4)' }}>🍽️</div>
            <p style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>
              Nenhum restaurante encontrado
            </p>
            <p style={{ fontSize: 'var(--font-size-sm)', marginTop: 'var(--space-2)' }}>
              Tente mudar os filtros
            </p>
          </div>
        )}
      </div>
    </>
  )
}
