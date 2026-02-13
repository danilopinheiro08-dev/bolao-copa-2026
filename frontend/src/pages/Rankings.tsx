import { useGlobalRanking } from '../api/hooks'

export default function Rankings() {
  const { data: rankings, isLoading } = useGlobalRanking()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Ranking Global</h1>

      {isLoading ? (
        <p className="text-gray-500">Carregando...</p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-brand-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">#</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Jogador</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Pontos</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Acertos</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Palpites</th>
              </tr>
            </thead>
            <tbody>
              {rankings?.map((entry) => (
                <tr key={entry.id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm font-bold text-brand-600">{entry.rank}</td>
                  <td className="px-6 py-3 text-sm font-medium text-gray-900">{entry.user.name}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{entry.total_points}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{entry.correct_predictions}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{entry.total_predictions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
