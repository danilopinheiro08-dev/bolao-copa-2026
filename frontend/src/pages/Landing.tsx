import { useAuth } from '../providers/AuthProvider'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'

export default function Landing() {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      navigate('/app/dashboard')
    }
  }, [user, navigate])

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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
            <button
              onClick={() => window.location.href = `${API_BASE_URL}/auth/google/login`}
              className="w-full px-6 py-3 bg-white text-gray-900 font-bold rounded-lg hover:bg-gray-100 transition flex items-center justify-center gap-2"
            >
              🔵 Google
            </button>
            <button
              onClick={() => window.location.href = `${API_BASE_URL}/auth/facebook/login`}
              className="w-full px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
            >
              📘 Facebook
            </button>
          </div>
        </div>

        <p className="text-sm opacity-75 mt-8">
          Feito com ❤️ para a Copa do Mundo 2026
        </p>
      </div>
    </div>
  )
}
