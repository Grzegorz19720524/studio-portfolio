import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProduct } from '../api/products'
import { createOrder } from '../api/orders'
import { useAuthStore } from '../store/authStore'

export default function ProductDetailPage() {
  const { slug } = useParams()
  const [product, setProduct] = useState(null)
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(true)
  const [ordering, setOrdering] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const { user } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    getProduct(slug)
      .then(({ data }) => setProduct(data))
      .catch(() => navigate('/products'))
      .finally(() => setLoading(false))
  }, [slug])

  const handleOrder = async () => {
    if (!user) { navigate('/login'); return }
    setOrdering(true)
    setError('')
    try {
      await createOrder({ items: [{ product: product.id, quantity }] })
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Błąd podczas składania zamówienia.')
    } finally {
      setOrdering(false)
    }
  }

  if (loading) return <p className="text-center py-20 text-gray-400">Ładowanie...</p>
  if (!product) return null

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <span className="text-xs text-indigo-500 font-medium">{product.category_name}</span>
      <h1 className="text-4xl font-bold text-gray-900 mt-1 mb-4">{product.name}</h1>
      <p className="text-gray-500 mb-6">{product.description || 'Brak opisu.'}</p>
      <p className="text-3xl font-bold text-indigo-600 mb-8">{product.price} zł</p>

      {success ? (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
          <p className="text-green-700 font-medium mb-3">Zamówienie zostało złożone!</p>
          <button onClick={() => navigate('/orders')} className="text-indigo-600 hover:underline text-sm">
            Zobacz swoje zamówienia →
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-4">
          <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="px-3 py-2 hover:bg-gray-100 text-gray-600"
            >−</button>
            <span className="px-4 py-2 font-medium">{quantity}</span>
            <button
              onClick={() => setQuantity(quantity + 1)}
              className="px-3 py-2 hover:bg-gray-100 text-gray-600"
            >+</button>
          </div>
          <button
            onClick={handleOrder}
            disabled={ordering}
            className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {ordering ? 'Składanie...' : 'Zamów'}
          </button>
        </div>
      )}
      {error && <p className="text-red-600 text-sm mt-4">{error}</p>}
    </div>
  )
}
