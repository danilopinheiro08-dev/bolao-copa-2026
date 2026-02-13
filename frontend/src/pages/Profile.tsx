import { useAuth } from '../providers/AuthProvider'

export default function Profile() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Perfil</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-600">Nome</label>
            <p className="text-lg font-semibold text-gray-900">{user?.name}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600">E-mail</label>
            <p className="text-lg font-semibold text-gray-900">{user?.email}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600">Verificado</label>
            <p className="text-lg font-semibold text-gray-900">{user?.email_verified ? '✅ Sim' : '❌ Não'}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
