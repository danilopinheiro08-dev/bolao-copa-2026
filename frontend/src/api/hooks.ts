import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import type { User, Match, Prediction, Group, RankingEntry, AISuggestion } from '../types'

// Auth Hooks
export const useMe = () => {
  return useQuery<User>({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const { data } = await apiClient.get('/auth/me')
      return data
    },
    retry: 1,
  })
}

export const useLogin = () => {
  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const { data } = await apiClient.post('/auth/login', { email, password })
      return data
    },
  })
}

export const useRegister = () => {
  return useMutation({
    mutationFn: async (payload: { email: string; name: string; password: string }) => {
      const { data } = await apiClient.post('/auth/register', payload)
      return data
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await apiClient.post('/auth/logout')
    },
    onSuccess: () => {
      queryClient.setQueryData(['auth', 'me'], null)
      queryClient.clear()
    },
  })
}

// Matches Hooks
export const useMatches = (filters?: { date?: string; stage?: string; status?: string }) => {
  return useQuery<Match[]>({
    queryKey: ['matches', filters],
    queryFn: async () => {
      const { data } = await apiClient.get('/matches', { params: filters })
      return data
    },
  })
}

export const useMatch = (id: number) => {
  return useQuery<Match>({
    queryKey: ['matches', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/matches/${id}`)
      return data
    },
    enabled: !!id,
  })
}

// Predictions Hooks
export const useMyPredictions = (scope?: 'global' | 'group', groupId?: number) => {
  return useQuery<Prediction[]>({
    queryKey: ['predictions', 'me', scope, groupId],
    queryFn: async () => {
      const { data } = await apiClient.get('/predictions/me', {
        params: { scope, group_id: groupId }
      })
      return data
    },
  })
}

export const useCreatePrediction = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<Prediction>) => {
      const { data } = await apiClient.post('/predictions', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] })
    },
  })
}

export const useUpdatePrediction = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Prediction> & { id: number }) => {
      const { data } = await apiClient.put(`/predictions/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] })
    },
  })
}

// Groups Hooks
export const useGroups = () => {
  return useQuery<Group[]>({
    queryKey: ['groups'],
    queryFn: async () => {
      const { data } = await apiClient.get('/groups')
      return data
    },
  })
}

export const useGroup = (id: number) => {
  return useQuery<Group>({
    queryKey: ['groups', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/groups/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export const useCreateGroup = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { name: string; is_public?: boolean }) => {
      const { data } = await apiClient.post('/groups', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

export const useJoinGroup = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, joinCode }: { id: number; joinCode: string }) => {
      const { data } = await apiClient.post(`/groups/${id}/join`, { join_code: joinCode })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

export const useGroupMembers = (groupId: number) => {
  return useQuery({
    queryKey: ['groups', groupId, 'members'],
    queryFn: async () => {
      const { data } = await apiClient.get(`/groups/${groupId}/members`)
      return data
    },
    enabled: !!groupId,
  })
}

// Rankings Hooks
export const useGlobalRanking = () => {
  return useQuery<RankingEntry[]>({
    queryKey: ['rankings', 'global'],
    queryFn: async () => {
      const { data } = await apiClient.get('/rankings/global')
      return data
    },
  })
}

export const useGroupRanking = (groupId: number) => {
  return useQuery<RankingEntry[]>({
    queryKey: ['rankings', 'group', groupId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/rankings/group/${groupId}`)
      return data
    },
    enabled: !!groupId,
  })
}

// AI Hooks
export const useAISuggestion = () => {
  return useMutation({
    mutationFn: async ({ matchId, style }: { matchId: number; style: 'conservative' | 'balanced' | 'aggressive' }) => {
      const { data } = await apiClient.post('/ai/suggest', { match_id: matchId, style })
      return data as AISuggestion
    },
  })
}

export const useAISuggestionBulk = () => {
  return useMutation({
    mutationFn: async ({ matchIds, style }: { matchIds: number[]; style: 'conservative' | 'balanced' | 'aggressive' }) => {
      const { data } = await apiClient.post('/ai/suggest/bulk', { match_ids: matchIds, style })
      return data as AISuggestion[]
    },
  })
}

// Admin Hooks
export const useImportFixtures = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await apiClient.post('/admin/fixtures/import-json', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] })
    },
  })
}

export const useRefreshMatches = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post('/admin/matches/refresh')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] })
    },
  })
}
