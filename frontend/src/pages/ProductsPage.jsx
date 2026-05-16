import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProducts, getCategories } from '../api/products'

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [ordering, setOrdering] = useState('-created_at')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCategories().then(({ data }) => setCategories(data.results || []))
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = { search, ordering }
    if (category) params.category = category
    getProducts(params)
      .then(({ data }) => setProducts(data.results || []))
      .finally(() => setLoading(false))
  }, [search, category, ordering])

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Oferta</h1>

      <div className="flex flex-wrap gap-4 mb-8">
        <input
          type="text"
          placeholder="Szukaj..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Wszystkie kategorie</option>
          {categories.map((c) => (
            <option key={c.id} value={c.slug}>{c.name}</option>
          ))}
        </select>
        <select
          value={ordering}
          onChange={(e) => setOrdering(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="-created_at">Najnowsze</option>
          <option value="price">Cena rosnąco</option>
          <option value="-price">Cena malejąco</option>
          <option value="name">Nazwa A–Z</option>
        </select>
      </div>

      {loading ? (
        <p className="text-gray-400 text-center py-20">Ładowanie...</p>
      ) : products.length === 0 ? (
        <p className="text-gray-400 text-center py-20">Brak produktów.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((p) => (
            <Link
              key={p.id}
              to={`/products/${p.slug}`}
              className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md hover:border-indigo-300 transition-all"
            >
              <span className="text-xs text-indigo-500 font-medium">{p.category_name}</span>
              <h2 className="text-lg font-semibold text-gray-900 mt-1 mb-2">{p.name}</h2>
              <p className="text-gray-500 text-sm line-clamp-2 mb-4">{p.description || '—'}</p>
              <p className="text-2xl font-bold text-indigo-600">{p.price} zł</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
