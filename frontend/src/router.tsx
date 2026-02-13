import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute'

// Pages
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Matches from './pages/Matches'
import MatchDetail from './pages/MatchDetail'
import Picks from './pages/Picks'
import Groups from './pages/Groups'
import GroupDetail from './pages/GroupDetail'
import Rankings from './pages/Rankings'
import Profile from './pages/Profile'
import Admin from './pages/Admin'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Landing />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/app',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'matches',
        element: <Matches />,
      },
      {
        path: 'matches/:id',
        element: <MatchDetail />,
      },
      {
        path: 'picks',
        element: <Picks />,
      },
      {
        path: 'groups',
        element: <Groups />,
      },
      {
        path: 'groups/:id',
        element: <GroupDetail />,
      },
      {
        path: 'rankings',
        element: <Rankings />,
      },
      {
        path: 'profile',
        element: <Profile />,
      },
      {
        path: 'admin',
        element: (
          <AdminRoute>
            <Admin />
          </AdminRoute>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <div className="flex items-center justify-center h-screen">Página não encontrada</div>,
  },
])
