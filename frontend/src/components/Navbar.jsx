import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link to="/" className="text-xl font-bold text-indigo-600">Studio</Link>

      <div className="flex items-center gap-6 text-sm">
        <Link to="/products" className="text-gray-600 hover:text-indigo-600 transition-colors">
          Produkty
        </Link>
        <Link to="/contact" className="text-gray-600 hover:text-indigo-600 transition-colors">
          Kontakt
        </Link>

        {user ? (
          <>
            <Link to="/dashboard" className="text-gray-600 hover:text-indigo-600 transition-colors">
              Dashboard
            </Link>
            <Link to="/orders" className="text-gray-600 hover:text-indigo-600 transition-colors">
              Zamówienia
            </Link>
            <Link to="/profile" className="text-gray-600 hover:text-indigo-600 transition-colors">
              {user.username}
            </Link>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-red-600 transition-colors"
            >
              Wyloguj
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="text-gray-600 hover:text-indigo-600 transition-colors">
              Logowanie
            </Link>
            <Link
              to="/register"
              className="bg-indigo-600 text-white px-4 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Rejestracja
            </Link>
          </>
        )}
      </div>
    </nav>
  )
}
