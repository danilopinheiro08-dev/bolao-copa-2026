import { useMatches } from '../api/hooks'
import { MatchCard, MatchCardSkeleton } from '../components/MatchCard'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

export default function Matches() {
  const [status, setStatus] = useState('scheduled')
  const { data: matches, isLoading } = useMatches({ status: status as any })
  const navigate = useNavigate()

  const groupedMatches = (matches || []).reduce((acc, match) => {
    const date = new Date(match.kickoff_at_utc).toLocaleDateString('pt-BR')
    if (!acc[date]) acc[date] = []
    acc[date].push(match)
    return acc
  }, {} as Record<string, typeof matches>)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Jogos</h1>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="scheduled">Agendados</option>
          <option value="live">Ao Vivo</option>
          <option value="finished">Finalizados</option>
        </select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <MatchCardSkeleton key={i} />)}
        </div>
      ) : Object.keys(groupedMatches).length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhum jogo encontrado</p>
      ) : (
        Object.entries(groupedMatches).map(([date, matchesForDate]) => (
          <div key={date}>
            <h2 className="text-xl font-bold text-gray-900 mb-4">{date}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {matchesForDate?.map((match) => (
                <MatchCard
                  key={match.id}
                  match={match}
                  onPick={() => navigate(`/app/matches/${match.id}`)}
                />
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
