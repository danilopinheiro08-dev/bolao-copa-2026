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
  { id: '1', name: 'Danilo', initials: 'DA', color: '#0EA5E9', role: 'Organizador' },
  { id: '2', name: 'Carol', initials: 'CA', color: '#FF6B6B', role: 'Viajante' },
  { id: '3', name: 'Lucas', initials: 'LU', color: '#10B981', role: 'Viajante' },
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
]

// Upcoming trip dates: May 12–19, 2026
const calendarItems: CalendarItem[] = [
  {
    id: 'c1',
    date: '2026-05-12',
    time: '14:00',
    title: 'Chegada em Natal',
    subtitle: 'Aeroporto Internacional Augusto Severo',
    travelerId: '1',
    color: '#0EA5E9',
  },
  {
    id: 'c2',
    date: '2026-05-13',
    time: '09:00',
    title: 'Praia de Ponta Negra',
    subtitle: 'Banho de mar + Morro do Careca',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=200&q=80',
    color: '#0EA5E9',
  },
  {
    id: 'c3',
    date: '2026-05-13',
    time: '12:30',
    title: 'Camarões Restaurante',
    subtitle: 'Almoço — reserva para 3 pessoas',
    travelerId: '2',
    imageUrl: 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=200&q=80',
    color: '#FF6B6B',
  },
  {
    id: 'c4',
    date: '2026-05-14',
    time: '07:00',
    title: 'Passeio de Buggy',
    subtitle: 'Dunas de Genipabu ao nascer do sol',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=200&q=80',
    color: '#0EA5E9',
  },
  {
    id: 'c5',
    date: '2026-05-15',
    time: '10:00',
    title: 'Praia de Pipa',
    subtitle: 'Snorkel + observação de golfinhos',
    travelerId: '3',
    imageUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200&q=80',
    color: '#10B981',
  },
  {
    id: 'c6',
    date: '2026-05-16',
    time: '11:00',
    title: 'Centro Histórico JP',
    subtitle: 'Visita guiada às igrejas barrocas',
    travelerId: '2',
    imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=200&q=80',
    color: '#FF6B6B',
  },
  {
    id: 'c7',
    date: '2026-05-16',
    time: '19:30',
    title: 'Mangai Restaurante',
    subtitle: 'Jantar nordestino — para todos',
    travelerId: '1',
    imageUrl: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=200&q=80',
    color: '#0EA5E9',
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
  selectedDate: '2026-05-12',
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
