import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getOrders } from '../api/orders'

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOrders()
      .then(({ data }) => setOrders(data.results || []))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-center py-20 text-gray-400">Ładowanie...</p>

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Moje zamówienia</h1>

      {orders.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400 mb-4">Brak zamówień.</p>
          <Link to="/products" className="text-indigo-600 hover:underline">Przeglądaj ofertę →</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Link
              key={order.id}
              to={`/orders/${order.id}`}
              className="block bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md hover:border-indigo-300 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-gray-900">Zamówienie #{order.id}</span>
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-600'}`}>
                  {order.status_display}
                </span>
              </div>
              <div className="flex justify-between text-sm text-gray-500">
                <span>{order.items?.length || 0} pozycji</span>
                <span className="font-bold text-gray-900">{order.total} zł</span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {new Date(order.created_at).toLocaleDateString('pl-PL', {
                  day: 'numeric', month: 'long', year: 'numeric',
                })}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
