import { useState } from 'react'
import { Star, MapPin, Plus } from 'lucide-react'
import { useStore } from '../store/useStore'
import TideWidget from '../components/TideWidget'
import type { TideCity } from '../services/tideService'

const CITY_FILTERS = ['Todos', 'Natal', 'Pipa', 'João Pessoa']
const CATEGORY_FILTERS = ['Todos', 'Praia', 'Passeio', 'Natureza', 'Cultura', 'Hotel']

// Mostra marés do dia atual (ou próximo dia da viagem) para praias
const TODAY_DATE = '2026-04-10' // primeiro dia da viagem como default

export default function Destinations() {
  const { destinations, showToast } = useStore()
  const [cityFilter, setCityFilter] = useState('Todos')
  const [catFilter, setCatFilter] = useState('Todos')

  const filtered = destinations.filter((d) => {
    const cityOk = cityFilter === 'Todos' || d.city === cityFilter
    const catOk = catFilter === 'Todos' || d.category === catFilter
    return cityOk && catOk
  })

  const handleAdd = (name: string) => {
    showToast(`"${name}" adicionado ao roteiro!`)
  }

  return (
    <>
      <header className="page-header">
        <span className="page-title">Destinos</span>
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

      {/* Category filter */}
      <div className="filter-bar" style={{ paddingTop: 0 }}>
        {CATEGORY_FILTERS.map((cat) => (
          <button
            key={cat}
            className={`chip${catFilter === cat ? ' active' : ''}`}
            style={{
              background: catFilter === cat ? 'var(--color-secondary)' : undefined,
              boxShadow: catFilter === cat ? 'var(--shadow-secondary)' : undefined,
            }}
            onClick={() => setCatFilter(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="page-list">
        {['Natal', 'Pipa', 'João Pessoa'].map((city) => {
          const cityItems = filtered.filter((d) => d.city === city)
          if (!cityItems.length) return null
          const hasBeaches = cityItems.some((d) => d.category === 'Praia')
          const showTides = hasBeaches && (catFilter === 'Todos' || catFilter === 'Praia')
          return (
            <div key={city}>
              {cityFilter === 'Todos' && (
                <div className="list-section-header">{city}</div>
              )}
              {/* Marés para cidades com praias */}
              {showTides && (
                <TideWidget date={TODAY_DATE} city={city as TideCity} />
              )}
              <div className="feed-section" style={{ margin: '0 var(--space-5) var(--space-4)', borderRadius: 'var(--radius-md)' }}>
                {cityItems.map((d, i) => (
                  <div
                    key={d.id}
                    className="premium-card"
                    style={{ borderBottom: i === cityItems.length - 1 ? 'none' : undefined }}
                  >
                    <img
                      src={d.imageUrl}
                      alt={d.name}
                      className="premium-card-img"
                      loading="lazy"
                    />
                    <div className="premium-card-body">
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span className="premium-card-category">{d.category}</span>
                        {d.description.startsWith('Sugestão do grupo') && (
                          <span style={{ fontSize: 9, fontWeight: 700, background: '#FEF3C7', color: '#D97706', padding: '1px 6px', borderRadius: 'var(--radius-full)', textTransform: 'uppercase' as const }}>
                            💬 Sugestão
                          </span>
                        )}
                      </div>
                      <span className="premium-card-name">{d.name}</span>
                      <p style={{
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-muted)',
                        marginTop: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}>
                        {d.description}
                      </p>
                      <div className="premium-card-meta" style={{ marginTop: 6 }}>
                        <span className="rating">
                          <Star size={12} fill="#FBBF24" color="#FBBF24" />
                          {d.rating.toFixed(1)}
                        </span>
                        <span className="meta-dot" />
                        <span className="distance">
                          <MapPin size={11} style={{ display: 'inline', marginRight: 2 }} />
                          {d.distance}
                        </span>
                        <span className="meta-dot" />
                        <span className="price-tag">{d.priceLevel}</span>
                      </div>
                    </div>
                    <button
                      className="add-btn"
                      onClick={() => handleAdd(d.name)}
                      aria-label={`Adicionar ${d.name}`}
                    >
                      <Plus size={18} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )
        })}

        {filtered.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: 'var(--space-12) var(--space-5)',
            color: 'var(--color-text-muted)',
          }}>
            <div style={{ fontSize: 48, marginBottom: 'var(--space-4)' }}>🏖️</div>
            <p style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>
              Nenhum destino encontrado
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
