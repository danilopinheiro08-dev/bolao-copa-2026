// Auth Types
export interface User {
  id: number
  email: string
  name: string
  is_admin: boolean
  email_verified: boolean
  provider: 'email' | 'google' | 'facebook'
  created_at: string
}

// Match Types
export interface Match {
  id: number
  home_team: string
  away_team: string
  stage: 'group' | 'round_of_16' | 'quarterfinal' | 'semifinal' | 'third_place' | 'final'
  kickoff_at_utc: string
  status: 'scheduled' | 'live' | 'finished' | 'cancelled'
  home_score: number | null
  away_score: number | null
  created_at: string
  updated_at: string
}

// Prediction Types
export interface Prediction {
  id: number
  match_id: number
  user_id: number
  home_score: number
  away_score: number
  advance_team?: string | null
  status: 'pending' | 'correct' | 'incorrect' | 'void'
  points: number
  created_at: string
  updated_at: string
}

// Group Types
export interface Group {
  id: number
  name: string
  owner_id: number
  join_code: string
  is_public: boolean
  created_at: string
  updated_at: string
  member_count?: number
}

export interface GroupMember {
  id: number
  group_id: number
  user_id: number
  role: 'admin' | 'member'
  joined_at: string
  user?: User
}

// Ranking Types
export interface RankingEntry {
  id: number
  user_id: number
  group_id: number | null
  total_points: number
  correct_predictions: number
  total_predictions: number
  rank: number
  user: User
  updated_at: string
}

// AI Types
export interface AISuggestion {
  home_score: number
  away_score: number
  advance_team?: string
  confidence: number
  reasoning: string
}

// API Response Types
export interface ApiResponse<T> {
  success?: boolean
  data?: T
  error?: string
  detail?: string
  message?: string
}
