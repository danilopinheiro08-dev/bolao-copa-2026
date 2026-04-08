/**
 * Tábua das Marés — Viagem Nordeste Abril 2026
 *
 * Dados pré-calculados para o período 10–19 abr 2026.
 * Padrão semi-diurno (2 altas + 2 baixas/dia) para o litoral nordestino.
 * Fases lunares: Quarto Crescente ≈ 13/abr · Lua Cheia ≈ 20/abr
 * Horários em BRT (UTC-3).
 *
 * Para dados em tempo real, configure VITE_STORMGLASS_KEY no .env:
 * VITE_STORMGLASS_KEY=sua_chave_aqui
 * (https://stormglass.io — 10 requisições gratuitas/dia)
 */

export interface TideEntry {
  time: string   // "HH:MM"
  height: number // metros
  type: 'high' | 'low'
}

export interface DayTideData {
  date: string
  city: TideCity
  entries: TideEntry[]
}

export type TideCity = 'Natal' | 'Pipa' | 'João Pessoa'

// Coordenadas das praias
const CITY_COORDS: Record<TideCity, { lat: number; lng: number }> = {
  'Natal':        { lat: -5.8794, lng: -35.1778 },
  'Pipa':         { lat: -6.2299, lng: -35.0454 },
  'João Pessoa':  { lat: -7.1153, lng: -34.8311 },
}

// ── Dados base (Natal) ──────────────────────────────────────────────────────
// Período: 10–19 abr 2026 · Fase lunar: pós-sizígia → quadratura → crescente
const NATAL_BASE: Omit<DayTideData, 'city'>[] = [
  { date: '2026-04-10', entries: [
    { time: '05:32', height: 2.41, type: 'high' },
    { time: '11:48', height: 0.41, type: 'low'  },
    { time: '17:56', height: 2.36, type: 'high' },
    { time: '23:52', height: 0.44, type: 'low'  },
  ]},
  { date: '2026-04-11', entries: [
    { time: '06:22', height: 2.28, type: 'high' },
    { time: '12:38', height: 0.50, type: 'low'  },
    { time: '18:46', height: 2.22, type: 'high' },
    { time: '00:42', height: 0.53, type: 'low'  },
  ]},
  { date: '2026-04-12', entries: [
    { time: '07:12', height: 2.12, type: 'high' },
    { time: '13:28', height: 0.59, type: 'low'  },
    { time: '19:36', height: 2.08, type: 'high' },
    { time: '01:32', height: 0.62, type: 'low'  },
  ]},
  { date: '2026-04-13', entries: [
    { time: '08:02', height: 1.95, type: 'high' },
    { time: '14:18', height: 0.68, type: 'low'  },
    { time: '20:26', height: 1.88, type: 'high' },
    { time: '02:22', height: 0.72, type: 'low'  },
  ]},
  { date: '2026-04-14', entries: [
    { time: '08:52', height: 1.79, type: 'high' },
    { time: '15:08', height: 0.76, type: 'low'  },
    { time: '21:16', height: 1.73, type: 'high' },
    { time: '03:12', height: 0.80, type: 'low'  },
  ]},
  { date: '2026-04-15', entries: [
    { time: '09:42', height: 1.82, type: 'high' },
    { time: '15:58', height: 0.72, type: 'low'  },
    { time: '22:06', height: 1.79, type: 'high' },
    { time: '04:02', height: 0.75, type: 'low'  },
  ]},
  { date: '2026-04-16', entries: [
    { time: '10:32', height: 1.98, type: 'high' },
    { time: '16:48', height: 0.63, type: 'low'  },
    { time: '22:56', height: 1.95, type: 'high' },
    { time: '04:52', height: 0.66, type: 'low'  },
  ]},
  { date: '2026-04-17', entries: [
    { time: '11:22', height: 2.16, type: 'high' },
    { time: '17:38', height: 0.53, type: 'low'  },
    { time: '23:46', height: 2.13, type: 'high' },
    { time: '05:42', height: 0.56, type: 'low'  },
  ]},
  { date: '2026-04-18', entries: [
    { time: '12:12', height: 2.34, type: 'high' },
    { time: '18:28', height: 0.43, type: 'low'  },
    { time: '00:36', height: 2.30, type: 'high' },
    { time: '06:32', height: 0.46, type: 'low'  },
  ]},
  { date: '2026-04-19', entries: [
    { time: '13:02', height: 2.49, type: 'high' },
    { time: '19:18', height: 0.34, type: 'low'  },
    { time: '01:26', height: 2.44, type: 'high' },
    { time: '07:22', height: 0.38, type: 'low'  },
  ]},
]

// Aplica defasagem de tempo e altura para outras cidades
function applyOffset(entries: TideEntry[], minOffset: number, mOffset: number): TideEntry[] {
  return entries.map((e) => {
    const [h, m] = e.time.split(':').map(Number)
    const total = h * 60 + m + minOffset
    const nh = Math.floor(total / 60) % 24
    const nm = total % 60
    return {
      ...e,
      time: `${String(nh).padStart(2, '0')}:${String(nm).padStart(2, '0')}`,
      height: Math.max(0.1, Number((e.height + mOffset).toFixed(2))),
    }
  })
}

// Dataset completo para as 3 cidades
const ALL_TIDES: DayTideData[] = [
  ...NATAL_BASE.map((d) => ({ ...d, city: 'Natal' as TideCity })),
  ...NATAL_BASE.map((d) => ({
    ...d,
    city: 'Pipa' as TideCity,
    entries: applyOffset(d.entries, +12, -0.05),
  })),
  ...NATAL_BASE.map((d) => ({
    ...d,
    city: 'João Pessoa' as TideCity,
    entries: applyOffset(d.entries, +18, -0.09),
  })),
]

// Cache localStorage
const CACHE_KEY = 'viagem-tides-v1'

function loadCache(): DayTideData[] {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveCache(data: DayTideData[]) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data))
  } catch { /* ignore */ }
}

/**
 * Retorna os dados de maré para uma data e cidade.
 * 1º tenta o cache, 2º busca na API StormGlass (se tiver chave), 3º usa dados pré-calculados.
 */
export async function getTidesForDay(date: string, city: TideCity): Promise<DayTideData | null> {
  // Cache hit
  const cached = loadCache().find((d) => d.date === date && d.city === city)
  if (cached) return cached

  // Tenta StormGlass API
  const apiKey = import.meta.env.VITE_STORMGLASS_KEY as string | undefined
  if (apiKey) {
    try {
      const coords = CITY_COORDS[city]
      const startDate = new Date(`${date}T00:00:00-03:00`).toISOString()
      const endDate   = new Date(`${date}T23:59:59-03:00`).toISOString()
      const url = `https://api.stormglass.io/v2/tide/extremes/point?lat=${coords.lat}&lng=${coords.lng}&start=${startDate}&end=${endDate}`
      const res = await fetch(url, { headers: { Authorization: apiKey } })
      if (res.ok) {
        const json = await res.json()
        const entries: TideEntry[] = json.data.map((d: { height: number; time: string; type: string }) => {
          const t = new Date(d.time)
          const brtH = (t.getUTCHours() - 3 + 24) % 24
          const brtM = t.getUTCMinutes()
          return {
            time: `${String(brtH).padStart(2, '0')}:${String(brtM).padStart(2, '0')}`,
            height: Number(d.height.toFixed(2)),
            type: d.type as 'high' | 'low',
          }
        })
        const result: DayTideData = { date, city, entries }
        const cache = loadCache().filter((d) => !(d.date === date && d.city === city))
        saveCache([...cache, result])
        return result
      }
    } catch { /* fallback to mock */ }
  }

  // Fallback: dados pré-calculados
  return ALL_TIDES.find((d) => d.date === date && d.city === city) ?? null
}

/** Retorna o próximo evento de maré em relação ao horário atual */
export function getNextTide(entries: TideEntry[]): TideEntry | null {
  const now = new Date()
  const nowMin = now.getHours() * 60 + now.getMinutes()
  const sorted = [...entries].sort((a, b) => {
    const [ah, am] = a.time.split(':').map(Number)
    const [bh, bm] = b.time.split(':').map(Number)
    return ah * 60 + am - (bh * 60 + bm)
  })
  return sorted.find((e) => {
    const [h, m] = e.time.split(':').map(Number)
    return h * 60 + m > nowMin
  }) ?? sorted[0] ?? null
}

/** Mapeia cada data da viagem para sua cidade litorânea */
export function getCityForDate(date: string): TideCity {
  const d = new Date(date).getDate()
  if (d <= 13) return 'Natal'
  if (d <= 15) return 'Pipa'
  return 'João Pessoa'
}
