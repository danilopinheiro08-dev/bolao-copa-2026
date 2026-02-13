import { Match } from '../types'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import { Users } from 'lucide-react'

dayjs.extend(utc)
dayjs.extend(timezone)

const TEAM_FLAGS: Record<string, string> = {
  'Argentina': '🇦🇷',
  'Brazil': '🇧🇷',
  'Colombia': '🇨🇴',
  'Costa Rica': '🇨🇷',
  'Ecuador': '🇪🇨',
  'El Salvador': '🇸🇻',
  'Honduras': '🇭🇳',
  'Jamaica': '🇯🇲',
  'Mexico': '🇲🇽',
  'Panama': '🇵🇦',
  'Paraguay': '🇵🇾',
  'Peru': '🇵🇪',
  'Trinidad And Tobago': '🇹🇹',
  'United States': '🇺🇸',
  'Uruguay': '🇺🇾',
  'Venezuela': '🇻🇪',
  'Canada': '🇨🇦',
  'Germany': '🇩🇪',
  'Spain': '🇪🇸',
  'Belgium': '🇧🇪',
  'Denmark': '🇩🇰',
  'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'France': '🇫🇷',
  'Netherlands': '🇳🇱',
  'Poland': '🇵🇱',
  'Portugal': '🇵🇹',
  'Italy': '🇮🇹',
  'Romania': '🇷🇴',
  'Serbia': '🇷🇸',
  'Greece': '🇬🇷',
  'Switzerland': '🇨🇭',
  'Austria': '🇦🇹',
  'Czech Republic': '🇨🇿',
  'Iceland': '🇮🇸',
  'Uzbekistan': '🇺🇿',
  'Tajikistan': '🇹🇯',
  'Japan': '🇯🇵',
  'Saudi Arabia': '🇸🇦',
  'South Korea': '🇰🇷',
  'Australia': '🇦🇺',
  'China': '🇨🇳',
  'Bahrain': '🇧🇭',
  'Iraq': '🇮🇶',
  'Iran': '🇮🇷',
  'Oman': '🇴🇲',
  'Palestine': '🇵🇸',
  'Lebanon': '🇱🇧',
  'Israel': '🇮🇱',
  'Thailand': '🇹🇭',
  'Vietnam': '🇻🇳',
  'Indonesia': '🇮🇩',
  'Malaysia': '🇲🇾',
  'Philippines': '🇵🇭',
  'Singapore': '🇸🇬',
  'New Zealand': '🇳🇿',
  'Morocco': '🇲🇦',
  'Egypt': '🇪🇬',
  'Nigeria': '🇳🇬',
  'Cameroon': '🇨🇲',
  'Ghana': '🇬🇭',
  'Senegal': '🇸🇳',
  'Tunisia': '🇹🇳',
  'Algeria': '🇩🇿',
  'South Africa': '🇿🇦',
  'Ivory Coast': '🇨🇮',
  'Mali': '🇲🇱',
  'Mali': '🇲🇱',
}

interface MatchCardProps {
  match: Match
  onPick?: () => void
  onAISuggest?: () => void
  isLoading?: boolean
}

export function MatchCard({ match, onPick, onAISuggest, isLoading }: MatchCardProps) {
  const kickoff = dayjs(match.kickoff_at_utc).tz('America/Sao_Paulo')
  const now = dayjs()
  const isLive = match.status === 'live'
  const isFinished = match.status === 'finished'
  const isPassed = now.isAfter(kickoff) && !isFinished
  const isLocked = now.isAfter(kickoff)

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <span className={`
          text-xs font-semibold px-2 py-1 rounded
          ${isLive ? 'bg-red-100 text-red-700' : isFinished ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}
        `}>
          {match.status === 'live' ? '🔴 AO VIVO' : match.status === 'finished' ? '✅ FINAL' : kickoff.format('DD/MM HH:mm')}
        </span>
        <span className="text-xs text-gray-500 uppercase font-semibold">{match.stage}</span>
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex flex-col items-center flex-1">
          <span className="text-3xl mb-2">{TEAM_FLAGS[match.home_team] || '⚽'}</span>
          <span className="font-semibold text-gray-900 text-center text-sm">{match.home_team}</span>
        </div>

        <div className="flex flex-col items-center px-4">
          {isFinished ? (
            <div className="text-2xl font-bold text-gray-900">
              {match.home_score} × {match.away_score}
            </div>
          ) : (
            <div className="text-lg text-gray-500">vs</div>
          )}
        </div>

        <div className="flex flex-col items-center flex-1">
          <span className="text-3xl mb-2">{TEAM_FLAGS[match.away_team] || '⚽'}</span>
          <span className="font-semibold text-gray-900 text-center text-sm">{match.away_team}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={onPick}
          disabled={isLocked || isLoading}
          className={`
            flex-1 px-4 py-2 rounded-lg font-semibold transition-colors
            ${isLocked
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-brand-600 text-white hover:bg-brand-700'
            }
          `}
        >
          {isFinished ? 'Ver' : isLocked ? 'Encerrado' : 'Palpitar'}
        </button>

        {!isFinished && (
          <button
            onClick={onAISuggest}
            disabled={isLoading}
            className="px-4 py-2 rounded-lg font-semibold border-2 border-brand-600 text-brand-600 hover:bg-brand-50 transition-colors disabled:opacity-50"
          >
            ✨ IA
          </button>
        )}
      </div>
    </div>
  )
}

export function MatchCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-20 mb-4"></div>
      <div className="flex justify-between items-center mb-6">
        <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
        <div className="h-6 bg-gray-200 rounded w-16"></div>
        <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
      </div>
      <div className="flex gap-2">
        <div className="flex-1 h-10 bg-gray-200 rounded"></div>
        <div className="flex-1 h-10 bg-gray-200 rounded"></div>
      </div>
    </div>
  )
}
