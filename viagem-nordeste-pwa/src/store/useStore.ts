import { create } from 'zustand'

/* ============================================================
   TYPES
   ============================================================ */

export interface Traveler {
  id: string
  name: string
  initials: string
  color: string
  role: string
}

export interface Destination {
  id: string
  name: string
  category: 'Praia' | 'Passeio' | 'Natureza' | 'Cultura' | 'Hotel'
  city: 'Natal' | 'Pipa' | 'João Pessoa'
  rating: number
  distance: string
  priceLevel: '$' | '$$' | '$$$'
  imageUrl: string
  description: string
}

export interface Restaurant {
  id: string
  name: string
  cuisine: string
  city: 'Natal' | 'Pipa' | 'João Pessoa'
  rating: number
  distance: string
  priceLevel: '$' | '$$' | '$$$'
  imageUrl: string
  description: string
}

export interface CalendarItem {
  id: string
  date: string
  time: string
  title: string
  subtitle: string
  travelerId: string
  imageUrl?: string
  color: string
}

export type Page = 'home' | 'destinations' | 'restaurants' | 'calendar'

interface AppState {
  travelers: Traveler[]
  currentTraveler: Traveler
  destinations: Destination[]
  restaurants: Restaurant[]
  calendarItems: CalendarItem[]
  currentPage: Page
  selectedDate: string
  activeCategory: string
  showProfileModal: boolean
  showAddModal: boolean
  toast: string | null

  setCurrentPage: (page: Page) => void
  setCurrentTraveler: (id: string) => void
  setSelectedDate: (date: string) => void
  setActiveCategory: (cat: string) => void
  setShowProfileModal: (v: boolean) => void
  setShowAddModal: (v: boolean) => void
  addToCalendar: (item: Omit<CalendarItem, 'id'>) => void
  removeFromCalendar: (id: string) => void
  showToast: (msg: string) => void
}

/* ============================================================
   MOCK DATA
   ============================================================ */

const travelers: Traveler[] = [
  { id: '1', name: 'Danilo',     initials: 'DA', color: '#0EA5E9', role: 'Organizador' },
  { id: '2', name: 'Jenifer',    initials: 'JE', color: '#FF6B6B', role: 'Viajante' },
  { id: '3', name: 'Gilmarques', initials: 'GI', color: '#10B981', role: 'Viajante' },
  { id: '4', name: 'Joseane',    initials: 'JO', color: '#F59E0B', role: 'Viajante' },
  { id: '5', name: 'Rodrigo',    initials: 'RO', color: '#8B5CF6', role: 'Viajante' },
  { id: '6', name: 'Jessica',    initials: 'JS', color: '#EC4899', role: 'Viajante' },
]

const destinations: Destination[] = [
  {
    id: 'd1',
    name: 'Praia de Pipa',
    category: 'Praia',
    city: 'Pipa',
    rating: 4.9,
    distance: '85 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80',
    description: 'Uma das praias mais bonitas do Brasil, com falésias avermelhadas e águas cristalinas.',
  },
  {
    id: 'd2',
    name: 'Passeio de Buggy',
    category: 'Passeio',
    city: 'Natal',
    rating: 4.8,
    distance: '12 km',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&q=80',
    description: 'Explore as dunas de Genipabu e Pitangui ao pôr do sol em um buggy 4x4.',
  },
  {
    id: 'd3',
    name: 'Forte dos Reis Magos',
    category: 'Cultura',
    city: 'Natal',
    rating: 4.6,
    distance: '3 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1580664558441-5a01c1af5088?w=400&q=80',
    description: 'Fortaleza histórica do século XVI na foz do Rio Potengi, ícone de Natal.',
  },
  {
    id: 'd4',
    name: 'Praia de Tambaba',
    category: 'Praia',
    city: 'João Pessoa',
    rating: 4.7,
    distance: '27 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?w=400&q=80',
    description: 'Praia naturista cercada por mata atlântica com piscinas naturais.',
  },
  {
    id: 'd5',
    name: 'Lagoa de Guaraíras',
    category: 'Natureza',
    city: 'Pipa',
    rating: 4.8,
    distance: '8 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&q=80',
    description: 'Lagoa de água doce perfeita para kitesurf, stand-up paddle e passeios de barco.',
  },
  {
    id: 'd6',
    name: 'Centro Histórico JP',
    category: 'Cultura',
    city: 'João Pessoa',
    rating: 4.5,
    distance: '2 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80',
    description: 'Igrejas barrocas, casarões coloniais e a famosa ladeira de São Francisco.',
  },
  {
    id: 'd7',
    name: 'Ponta Negra Beach',
    category: 'Praia',
    city: 'Natal',
    rating: 4.7,
    distance: '8 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400&q=80',
    description: 'A praia urbana mais famosa de Natal, com Morro do Careca e boa infraestrutura.',
  },
  {
    id: 'd8',
    name: 'Pousada Minas Gerais',
    category: 'Hotel',
    city: 'Pipa',
    rating: 4.9,
    distance: '86 km',
    priceLevel: '$$$',
    imageUrl: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=400&q=80',
    description: 'Charming pousada com vista para o mar, piscina infinity e café da manhã incluso.',
  },
  // ── Sugestões do grupo ──
  {
    id: 'd9',
    name: 'Praia de Redinha',
    category: 'Praia',
    city: 'Natal',
    rating: 4.6,
    distance: '18 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400&q=80',
    description: 'Sugestão do grupo · Praia calma e ótima para ir com crianças, famosa pelo sururu e pelo visual do Rio Potengi.',
  },
  {
    id: 'd10',
    name: 'Praia do Forte',
    category: 'Praia',
    city: 'Natal',
    rating: 4.7,
    distance: '5 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?w=400&q=80',
    description: 'Sugestão do grupo · Praia urbana de águas tranquilas, ideal para famílias. Próxima ao Forte dos Reis Magos.',
  },
  {
    id: 'd11',
    name: 'Mercado do Peixe',
    category: 'Cultura',
    city: 'Natal',
    rating: 4.5,
    distance: '7 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80',
    description: 'Sugestão do grupo · Comer a ginga com tapioca — experiência gastronômica típica de Natal que não pode faltar!',
  },
]

const restaurants: Restaurant[] = [
  {
    id: 'r1',
    name: 'Camarões Restaurante',
    cuisine: 'Frutos do Mar',
    city: 'Natal',
    rating: 4.8,
    distance: '6 km',
    priceLevel: '$$$',
    imageUrl: 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&q=80',
    description: 'O mais famoso restaurante de frutos do mar de Natal, com camarão ao leite de coco.',
  },
  {
    id: 'r2',
    name: 'Peixe na Telha',
    cuisine: 'Regional',
    city: 'Pipa',
    rating: 4.7,
    distance: '85 km',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&q=80',
    description: 'Especialidade em peixe assado na telha com pirão e farofa na beira da praia.',
  },
  {
    id: 'r3',
    name: 'Mangai',
    cuisine: 'Nordestina',
    city: 'João Pessoa',
    rating: 4.9,
    distance: '3 km',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&q=80',
    description: 'Culinária típica nordestina em ambiente festivo, servido no estilo self-service farto.',
  },
  {
    id: 'r4',
    name: 'Canto da Praia',
    cuisine: 'Frutos do Mar',
    city: 'Natal',
    rating: 4.6,
    distance: '9 km',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=80',
    description: 'Ambiente casual com vista para o mar, perfeito para lagostas e peixes frescos.',
  },
  {
    id: 'r5',
    name: 'Cruzeiro do Mar',
    cuisine: 'Brasileiro',
    city: 'Pipa',
    rating: 4.5,
    distance: '85 km',
    priceLevel: '$',
    imageUrl: 'https://images.unsplash.com/photo-1546833998-877b37c2e5c6?w=400&q=80',
    description: 'Café da manhã e almoço leve com pão de queijo, tapiocas e frutas tropicais.',
  },
  {
    id: 'r6',
    name: 'Tambaú Grill',
    cuisine: 'Churrasco',
    city: 'João Pessoa',
    rating: 4.4,
    distance: '5 km',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&q=80',
    description: 'Rodízio premium com cortes nobres, vista para a praia de Tambaú ao entardecer.',
  },
  // ── Sugestões do grupo ──
  {
    id: 'r7',
    name: 'Restaurante Bidoca',
    cuisine: 'Regional',
    city: 'Natal',
    rating: 4.6,
    distance: 'Natal/RN',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&q=80',
    description: 'Sugestão do grupo · Culinária nordestina autêntica em ambiente aconchegante.',
  },
  {
    id: 'r8',
    name: 'Ô Bar Praia',
    cuisine: 'Bar & Petiscos',
    city: 'Natal',
    rating: 4.5,
    distance: 'Natal/RN',
    priceLevel: '$$',
    imageUrl: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=80',
    description: 'Sugestão do grupo · Bar à beira-mar em Natal/RN com petiscos e vista panorâmica para o oceano.',
  },
]

// Trip: April 10–19, 2026 · JPA → Natal → Pipa → João Pessoa → JPA
const calendarItems: CalendarItem[] = [
  // ── 10/04 (Sex) · SAÍDA DE JPA ──────────────────────────────
  {
    id: 'c01',
    date: '2026-04-10',
    time: '08:00',
    title: 'Saída de João Pessoa',
    subtitle: 'Trânsito JPA → Natal · 173 km · aprox. 02h45',
    travelerId: '1',
    color: '#0EA5E9',
  },
  {
    id: 'c02',
    date: '2026-04-10',
    time: '14:00',
    title: 'Check In — Coral Plaza Hotel',
    subtitle: 'Natal/RN · Check In após às 14:00 · Noite 1',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=200&q=80',
    color: '#0EA5E9',
  },

  // ── 11/04 (Sáb) · NATAL — NOITE 2 ──────────────────────────
  {
    id: 'c03',
    date: '2026-04-11',
    time: '09:00',
    title: 'Passeio: Rio do Fogo',
    subtitle: 'Natal/RN · Noite 2 · Coral Plaza',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200&q=80',
    color: '#0EA5E9',
  },

  // ── 12/04 (Dom) · NATAL — NOITE 3 ──────────────────────────
  {
    id: 'c04',
    date: '2026-04-12',
    time: '09:00',
    title: 'Passeio a definir (?)',
    subtitle: 'Natal/RN · Noite 3 · Coral Plaza',
    travelerId: '1',
    color: '#0EA5E9',
  },

  // ── 13/04 (Seg) · NATAL — NOITE 4 + CHECK OUT ───────────────
  {
    id: 'c05',
    date: '2026-04-13',
    time: '08:00',
    title: 'Quadriciclo ou Buggy — Dunas',
    subtitle: 'Natal/RN · Antes do Check Out',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=200&q=80',
    color: '#0EA5E9',
  },
  {
    id: 'c06',
    date: '2026-04-13',
    time: '12:00',
    title: 'Check Out — Coral Plaza Hotel',
    subtitle: 'Natal/RN · Check Out até às 12:00 · Noite 4',
    travelerId: '1',
    color: '#0EA5E9',
  },

  // ── 14/04 (Ter) · TRÂNSITO NATAL → PIPA ─────────────────────
  {
    id: 'c07',
    date: '2026-04-14',
    time: '13:00',
    title: 'Trânsito: Natal → Pipa',
    subtitle: 'Coral Plaza → Serhs Villas Pipa · 82 km · 01h40',
    travelerId: '1',
    color: '#FF6B6B',
  },
  {
    id: 'c08',
    date: '2026-04-14',
    time: '15:00',
    title: 'Check In — Serhs Villas de Pipa Hotel',
    subtitle: 'Pipa/RN · Check In após às 15:00 · Noite 5',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=200&q=80',
    color: '#FF6B6B',
  },

  // ── 15/04 (Qua) · PIPA — NOITE 6 + CHECK OUT ────────────────
  {
    id: 'c09',
    date: '2026-04-15',
    time: '09:00',
    title: 'Passeio em Pipa',
    subtitle: 'Pipa/RN · Noite 6 · Aqui faz mais sentido',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200&q=80',
    color: '#FF6B6B',
  },
  {
    id: 'c10',
    date: '2026-04-15',
    time: '15:00',
    title: 'Check Out — Serhs Villas de Pipa Hotel',
    subtitle: 'Pipa/RN · Check Out até às 15:00',
    travelerId: '1',
    color: '#FF6B6B',
  },

  // ── 16/04 (Qui) · TRÂNSITO PIPA → JOÃO PESSOA ───────────────
  {
    id: 'c11',
    date: '2026-04-16',
    time: '15:30',
    title: 'Trânsito: Pipa → João Pessoa',
    subtitle: 'Serhs Villas → Jardins Almare · 155 km · 02h30',
    travelerId: '1',
    color: '#10B981',
  },
  {
    id: 'c12',
    date: '2026-04-16',
    time: '18:00',
    title: 'Check In — Jardins Almare Apart Hotel',
    subtitle: 'João Pessoa/PB · Check In após às 15:00 · Noite 7',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=200&q=80',
    color: '#10B981',
  },

  // ── 17/04 (Sex) · JOÃO PESSOA — NOITE 8 ─────────────────────
  {
    id: 'c13',
    date: '2026-04-17',
    time: '09:00',
    title: 'Passeio em João Pessoa',
    subtitle: 'João Pessoa/PB · Noite 8 · Aqui faz mais sentido',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=200&q=80',
    color: '#10B981',
  },

  // ── 18/04 (Sáb) · JOÃO PESSOA — NOITE 9 + CHECK OUT ─────────
  {
    id: 'c14',
    date: '2026-04-18',
    time: '09:00',
    title: 'Passeio a definir (?)',
    subtitle: 'João Pessoa/PB · Noite 9',
    travelerId: '1',
    color: '#10B981',
  },
  {
    id: 'c15',
    date: '2026-04-18',
    time: '12:00',
    title: 'Check Out — Jardins Almare Apart Hotel',
    subtitle: 'João Pessoa/PB · Check Out até às 12:00',
    travelerId: '1',
    color: '#10B981',
  },

  // ── 19/04 (Dom) · VOLTA PARA JPA ────────────────────────────
  {
    id: 'c16',
    date: '2026-04-19',
    time: '12:30',
    title: 'Trânsito: JP → JPA · Volta para casa',
    subtitle: 'Jardins Almare → JPA · 23 km · aprox. 00h35',
    travelerId: '1',
    color: '#10B981',
  },
]

/* ============================================================
   STORE
   ============================================================ */

export const useStore = create<AppState>((set, get) => ({
  travelers,
  currentTraveler: travelers[0]!,
  destinations,
  restaurants,
  calendarItems,
  currentPage: 'home',
  selectedDate: '2026-04-10',
  activeCategory: 'Todos',
  showProfileModal: false,
  showAddModal: false,
  toast: null,

  setCurrentPage: (page) => set({ currentPage: page }),

  setCurrentTraveler: (id) => {
    const t = get().travelers.find((t) => t.id === id)
    if (t) set({ currentTraveler: t, showProfileModal: false })
  },

  setSelectedDate: (date) => set({ selectedDate: date }),
  setActiveCategory: (cat) => set({ activeCategory: cat }),
  setShowProfileModal: (v) => set({ showProfileModal: v }),
  setShowAddModal: (v) => set({ showAddModal: v }),

  addToCalendar: (item) =>
    set((state) => ({
      calendarItems: [
        ...state.calendarItems,
        { ...item, id: `c${Date.now()}` },
      ],
      showAddModal: false,
    })),

  removeFromCalendar: (id) =>
    set((state) => ({
      calendarItems: state.calendarItems.filter((i) => i.id !== id),
    })),

  showToast: (msg) => {
    set({ toast: msg })
    setTimeout(() => set({ toast: null }), 3000)
  },
}))
