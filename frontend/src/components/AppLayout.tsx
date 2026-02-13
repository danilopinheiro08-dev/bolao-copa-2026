import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../providers/AuthProvider'
import { Menu, LogOut, Trophy, Calendar, Target, Users, User, Settings } from 'lucide-react'
import { useState } from 'react'

export function AppLayout() {
  const { user, signOut } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const menuItems = [
    { href: '/app/dashboard', label: 'Dashboard', icon: Trophy },
    { href: '/app/matches', label: 'Jogos', icon: Calendar },
    { href: '/app/picks', label: 'Palpites', icon: Target },
    { href: '/app/groups', label: 'Grupos', icon: Users },
    { href: '/app/rankings', label: 'Ranking', icon: Trophy },
    { href: '/app/profile', label: 'Perfil', icon: User },
    ...(user?.is_admin ? [{ href: '/app/admin', label: 'Admin', icon: Settings }] : []),
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform
        md:relative md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6">
          <h1 className="text-2xl font-bold text-brand-700">⚽ Bolão Copa 2026</h1>
        </div>

        <nav className="mt-8 space-y-2 px-4">
          {menuItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              to={href}
              onClick={() => setSidebarOpen(false)}
              className={`
                flex items-center gap-3 px-4 py-2 rounded-lg transition-colors
                ${isActive(href)
                  ? 'bg-brand-100 text-brand-700 font-semibold'
                  : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <Icon size={20} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <button
            onClick={() => signOut()}
            className="flex items-center gap-2 w-full px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            <LogOut size={20} />
            <span>Sair</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="flex items-center justify-between h-16 px-4 md:px-8">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <Menu size={24} />
            </button>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-semibold text-gray-900">{user?.name}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 md:px-8 py-8">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}
