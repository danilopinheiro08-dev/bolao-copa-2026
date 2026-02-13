import { useNavigate } from 'react-router-dom'
import { useAuth } from '../providers/AuthProvider'
import { useState } from 'react'
import { Loader2 } from 'lucide-react'

export default function Login() {
  const navigate = useNavigate()
  const { signInEmail } = useAuth()
  const [email, setEmail] = useState('test@bolao.com')
  const [password, setPassword] = useState('Test123456!')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await signInEmail(email, password)
      navigate('/app/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-600 to-brand-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">⚽ Entrar</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-2 bg-brand-600 text-white font-bold rounded-lg hover:bg-brand-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading && <Loader2 size={20} className="animate-spin" />}
            Entrar
          </button>
        </form>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Ou</span>
          </div>
        </div>

        <div className="space-y-2 mb-6">
          <button
            onClick={() => window.location.href = `${API_BASE_URL}/auth/google/login`}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-semibold flex items-center justify-center gap-2"
          >
            🔵 Google
          </button>
          <button
            onClick={() => window.location.href = `${API_BASE_URL}/auth/facebook/login`}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-semibold flex items-center justify-center gap-2"
          >
            📘 Facebook
          </button>
        </div>

        <p className="text-center text-gray-600">
          Não tem conta? <button onClick={() => navigate('/register')} className="text-brand-600 font-bold hover:underline">Criar conta</button>
        </p>
      </div>
    </div>
  )
}
