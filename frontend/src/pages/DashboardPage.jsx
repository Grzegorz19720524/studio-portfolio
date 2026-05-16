import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { getOrders } from '../api/orders'

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const STATUS_LABELS = {
  pending: 'Oczekuje',
  confirmed: 'Potwierdzone',
  in_progress: 'W realizacji',
  completed: 'Zakończone',
  cancelled: 'Anulowane',
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOrders()
      .then(({ data }) => setOrders(data.results || []))
      .finally(() => setLoading(false))
  }, [])

  const stats = {
    total: orders.length,
    active: orders.filter((o) => ['pending', 'confirmed', 'in_progress'].includes(o.status)).length,
    completed: orders.filter((o) => o.status === 'completed').length,
  }

  const recentOrders = orders.slice(0, 3)

  const displayName = user?.first_name
    ? `${user.first_name}${user.last_name ? ' ' + user.last_name : ''}`
    : user?.username

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-10">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Witaj, {displayName}!
        </h1>
        <p className="text-gray-500 mt-1">
          Oto przegląd Twojego konta w Studio.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Wszystkie zamówienia"
          value={loading ? '—' : stats.total}
          color="indigo"
        />
        <StatCard
          label="W toku"
          value={loading ? '—' : stats.active}
          color="purple"
        />
        <StatCard
          label="Zakończone"
          value={loading ? '—' : stats.completed}
          color="green"
        />
      </div>

      {/* Recent orders */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Ostatnie zamówienia</h2>
          <Link to="/orders" className="text-sm text-indigo-600 hover:underline">
            Zobacz wszystkie →
          </Link>
        </div>

        {loading ? (
          <p className="text-gray-400 py-8 text-center">Ładowanie...</p>
        ) : recentOrders.length === 0 ? (
          <div className="bg-gray-50 border border-dashed border-gray-200 rounded-xl p-8 text-center">
            <p className="text-gray-400 mb-3">Nie masz jeszcze żadnych zamówień.</p>
            <Link
              to="/products"
              className="inline-block bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              Przeglądaj ofertę
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {recentOrders.map((order) => (
              <Link
                key={order.id}
                to={`/orders/${order.id}`}
                className="flex items-center justify-between bg-white border border-gray-200 rounded-xl px-6 py-4 hover:shadow-md hover:border-indigo-300 transition-all"
              >
                <div>
                  <p className="font-semibold text-gray-900">Zamówienie #{order.id}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(order.created_at).toLocaleDateString('pl-PL', {
                      day: 'numeric', month: 'long', year: 'numeric',
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <span
                    className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-600'}`}
                  >
                    {order.status_display || STATUS_LABELS[order.status] || order.status}
                  </span>
                  <span className="font-bold text-gray-900 whitespace-nowrap">
                    {order.total} zł
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Quick actions */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Szybkie akcje</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <QuickLink to="/products" label="Przeglądaj ofertę" emoji="🛍️" />
          <QuickLink to="/orders" label="Moje zamówienia" emoji="📦" />
          <QuickLink to="/profile" label="Edytuj profil" emoji="👤" />
          <QuickLink to="/contact" label="Napisz do nas" emoji="✉️" />
        </div>
      </section>

      {/* Account info */}
      <section className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Dane konta</h2>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <InfoRow label="Login" value={user?.username} />
          <InfoRow label="Email" value={user?.email} />
          {user?.first_name && <InfoRow label="Imię" value={user.first_name} />}
          {user?.last_name && <InfoRow label="Nazwisko" value={user.last_name} />}
          {user?.phone && <InfoRow label="Telefon" value={user.phone} />}
          {user?.company && <InfoRow label="Firma" value={user.company} />}
        </dl>
        <Link
          to="/profile"
          className="inline-block mt-4 text-sm text-indigo-600 hover:underline"
        >
          Edytuj dane →
        </Link>
      </section>
    </div>
  )
}

function StatCard({ label, value, color }) {
  const colors = {
    indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    green: 'bg-green-50 border-green-200 text-green-700',
  }
  return (
    <div className={`border rounded-xl p-6 ${colors[color]}`}>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-sm mt-1 opacity-80">{label}</p>
    </div>
  )
}

function QuickLink({ to, label, emoji }) {
  return (
    <Link
      to={to}
      className="flex flex-col items-center gap-2 bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md hover:border-indigo-300 transition-all text-center"
    >
      <span className="text-2xl">{emoji}</span>
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </Link>
  )
}

function InfoRow({ label, value }) {
  return (
    <div>
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900">{value}</dd>
    </div>
  )
}
