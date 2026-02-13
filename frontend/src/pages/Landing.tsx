import { useAuth } from '../providers/AuthProvider'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'

export default function Landing() {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      navigate('/dashboard')
    }
  }, [user, navigate])

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-600 to-brand-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center text-white">
        <h1 className="text-5xl font-bold mb-4">⚽ Bolão Copa 2026</h1>
        <p className="text-xl mb-8 opacity-90">Palpite seus resultados da Copa do Mundo e compete com amigos!</p>

        <div className="space-y-4">
          {/* Email Login */}
          <div className="space-y-2">
            <button
              onClick={() => navigate('/login')}
              className="w-full px-6 py-3 bg-white text-brand-700 font-bold rounded-lg hover:bg-gray-100 transition"
            >
              Entrar com E-mail
            </button>
            <button
              onClick={() => navigate('/register')}
              className="w-full px-6 py-3 border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-brand-700 transition"
            >
              Criar Conta
            </button>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white opacity-30"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-brand-700">Ou</span>
            </div>
          </div>

          {/* Social Login */}
          <div className="space-y-2">
            <a
              href={`${apiBaseUrl}/auth/google/login`}
              className="block w-full px-6 py-3 bg-white text-gray-800 font-bold rounded-lg hover:bg-gray-100 transition"
            >
              🔵 Google
            </a>
            <a
              href={`${apiBaseUrl}/auth/facebook/login`}
              className="block w-full px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition"
            >
              f Facebook
            </a>
          </div>
        </div>

        <p className="text-sm opacity-75 mt-8">
          © 2026 Bolão Copa. Todos os direitos reservados.
        </p>
      </div>
    </div>
  )
}
