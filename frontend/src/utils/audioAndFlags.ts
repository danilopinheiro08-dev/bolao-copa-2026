import { useCallback } from 'react'

export interface SoundEffect {
  name: string
  url: string
  volume?: number
}

const SOUND_EFFECTS: Record<string, string> = {
  // Stadium ambience
  STADIUM_AMBIENT: 'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3',
  
  // Goal sounds
  GOAL_CHEER: 'https://assets.mixkit.co/active_storage/sfx/2895/2895-preview.mp3',
  CROWD_CHEER: 'https://assets.mixkit.co/active_storage/sfx/2896/2896-preview.mp3',
  
  // Game sounds
  WHISTLE: 'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3',
  
  // UI sounds
  SUCCESS: 'https://assets.mixkit.co/active_storage/sfx/3025/3025-preview.mp3',
  ERROR: 'https://assets.mixkit.co/active_storage/sfx/3027/3027-preview.mp3',
}

export const useSound = () => {
  const play = useCallback((soundKey: keyof typeof SOUND_EFFECTS, volume = 0.3) => {
    const url = SOUND_EFFECTS[soundKey]
    if (!url) {
      console.warn(`Sound effect ${soundKey} not found`)
      return
    }

    const audio = new Audio(url)
    audio.volume = Math.min(Math.max(volume, 0), 1)
    audio.play().catch(err => console.error('Audio play error:', err))
  }, [])

  return { play }
}

export const COUNTRY_FLAGS: Record<string, string> = {
  // Americas
  'ARG': '🇦🇷', 'BRA': '🇧🇷', 'MEX': '🇲🇽', 'USA': '🇺🇸', 'CAN': '🇨🇦', 'CHI': '🇨🇱', 'COL': '🇨🇴', 'ECU': '🇪🇨', 'PAR': '🇵🇾', 'PER': '🇵🇪', 'URU': '🇺🇾', 'VEN': '🇻🇪',
  // Europe
  'ALE': '🇩🇪', 'ESP': '🇪🇸', 'FRA': '🇫🇷', 'ITA': '🇮🇹', 'POR': '🇵🇹', 'ING': '🇬🇧', 'AUT': '🇦🇹', 'BEL': '🇧🇪', 'HOL': '🇳🇱', 'POL': '🇵🇱', 'SUI': '🇨🇭', 'TUR': '🇹🇷', 'UCR': '🇺🇦', 'ROM': '🇷🇴', 'SER': '🇷🇸', 'GRE': '🇬🇷', 'CRO': '🇭🇷', 'DIN': '🇩🇰', 'SWE': '🇸🇪', 'NOR': '🇳🇴',
  // Africa
  'EGI': '🇪🇬', 'MAR': '🇲🇦', 'NIG': '🇳🇬', 'SEN': '🇸🇳', 'GHA': '🇬🇭', 'CAM': '🇨🇲', 'COS': '🇨🇮', 'MLA': '🇲🇱', 'RSA': '🇿🇦', 'TUN': '🇹🇳',
  // Asia & Pacific
  'JAP': '🇯🇵', 'CHN': '🇨🇳', 'KOR': '🇰🇷', 'AUS_AP': '🇦🇺', 'THA': '🇹🇭', 'VIE': '🇻🇳', 'SIN': '🇸🇬', 'IND': '🇮🇳', 'PAK': '🇵🇰', 'BAN': '🇧🇩', 'IRN': '🇮🇷', 'SAU': '🇸🇦', 'CAT': '🇶🇦', 'EAU': '🇦🇪', 'ISR': '🇮🇱',
}

export const getFlagEmoji = (countryCode?: string): string => {
  if (!countryCode) return '⚽'
  return COUNTRY_FLAGS[countryCode.toUpperCase()] || '⚽'
}
