import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuthStore()
  if (loading) return <div className="flex justify-center p-20 text-gray-400">Ładowanie...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}
