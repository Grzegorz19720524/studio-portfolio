import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getOrder } from '../api/orders'

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

export default function OrderDetailPage() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOrder(id)
      .then(({ data }) => setOrder(data))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="text-center py-20 text-gray-400">Ładowanie...</p>
  if (!order) return <p className="text-center py-20 text-gray-400">Nie znaleziono zamówienia.</p>

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Zamówienie #{order.id}</h1>
        <span className={`text-sm font-medium px-3 py-1 rounded-full ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-600'}`}>
          {order.status_display}
        </span>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100 mb-6">
        {order.items.map((item) => (
          <div key={item.id} className="flex justify-between items-center px-6 py-4">
            <div>
              <p className="font-medium text-gray-900">{item.product_name}</p>
              <p className="text-sm text-gray-500">{item.unit_price} zł × {item.quantity}</p>
            </div>
            <p className="font-bold text-gray-900">{item.subtotal} zł</p>
          </div>
        ))}
        <div className="flex justify-between items-center px-6 py-4 bg-gray-50 rounded-b-xl">
          <span className="font-semibold text-gray-700">Łącznie</span>
          <span className="text-xl font-bold text-indigo-600">{order.total} zł</span>
        </div>
      </div>

      {order.notes && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-gray-500 font-medium mb-1">Uwagi</p>
          <p className="text-gray-700">{order.notes}</p>
        </div>
      )}

      <p className="text-sm text-gray-400 mb-6">
        Złożono: {new Date(order.created_at).toLocaleDateString('pl-PL', {
          day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit',
        })}
      </p>

      <Link to="/orders" className="text-indigo-600 hover:underline text-sm">← Wróć do zamówień</Link>
    </div>
  )
}
