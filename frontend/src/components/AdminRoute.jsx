import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function AdminRoute({ children }) {
  const { user, loading } = useAuthStore()

  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (!user.is_staff) return <Navigate to="/" replace />

  return children
}
