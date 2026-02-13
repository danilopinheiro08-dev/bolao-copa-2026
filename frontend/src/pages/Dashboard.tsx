import { useMatches, useGlobalRanking, useMyPredictions } from '../api/hooks'
import { MatchCard, MatchCardSkeleton } from '../components/MatchCard'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

export default function Dashboard() {
  const { data: matches, isLoading: matchesLoading } = useMatches({ status: 'scheduled' })
  const { data: rankings } = useGlobalRanking()
  const { data: myPredictions } = useMyPredictions('global')

  const nextMatches = (matches || []).slice(0, 3)

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 mb-2">Próximos Jogos</p>
          <p className="text-3xl font-bold text-brand-600">{matches?.length || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 mb-2">Meus Palpites</p>
          <p className="text-3xl font-bold text-brand-600">{myPredictions?.length || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 mb-2">Sua Posição</p>
          <p className="text-3xl font-bold text-brand-600">#{rankings?.[0]?.rank || '—'}</p>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-4">Próximos Jogos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {matchesLoading ? (
            <>
              <MatchCardSkeleton />
              <MatchCardSkeleton />
              <MatchCardSkeleton />
            </>
          ) : nextMatches.length === 0 ? (
            <p className="text-gray-500">Nenhum jogo agendado</p>
          ) : (
            nextMatches.map((match) => (
              <MatchCard key={match.id} match={match} />
            ))
          )}
        </div>
      </div>

      {rankings && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Top 5 Ranking Global</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">#</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Jogador</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Pontos</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Acertos</th>
                </tr>
              </thead>
              <tbody>
                {rankings.slice(0, 5).map((entry) => (
                  <tr key={entry.id} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-3 text-sm font-bold text-brand-600">{entry.rank}</td>
                    <td className="px-6 py-3 text-sm font-medium text-gray-900">{entry.user.name}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{entry.total_points}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{entry.correct_predictions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
