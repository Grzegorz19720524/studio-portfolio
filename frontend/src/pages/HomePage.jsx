import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProducts, getCategories } from '../api/products'

export default function HomePage() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [stats, setStats] = useState({ products: 0, categories: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getProducts({ ordering: '-created_at', page_size: 3 }),
      getCategories(),
    ]).then(([p, c]) => {
      const prods = p.data.results || []
      const cats = c.data.results || []
      setProducts(prods)
      setCategories(cats)
      setStats({
        products: p.data.count || prods.length,
        categories: cats.length,
      })
    }).finally(() => setLoading(false))
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-24 px-6 text-center">
        <div className="max-w-3xl mx-auto">
          <span className="inline-block bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full mb-6 tracking-wide uppercase">
            Agencja kreatywna
          </span>
          <h1 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
            Tworzymy cyfrowe<br />
            <span className="text-indigo-600">rozwiązania dla biznesu</span>
          </h1>
          <p className="text-xl text-gray-500 mb-10 max-w-xl mx-auto">
            Strony internetowe, aplikacje webowe i identyfikacje wizualne.
            Projekty szyte na miarę, gotowe na czas.
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <Link
              to="/products"
              className="bg-indigo-600 text-white px-7 py-3.5 rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-sm"
            >
              Zobacz ofertę
            </Link>
            <Link
              to="/contact"
              className="border border-gray-300 text-gray-700 px-7 py-3.5 rounded-xl font-medium hover:border-indigo-400 hover:text-indigo-600 transition-colors"
            >
              Skontaktuj się
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-gray-100 bg-white py-12 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
          <StatCounter value={loading ? '…' : stats.products} label="Usług w ofercie" />
          <StatCounter value={loading ? '…' : stats.categories} label="Kategorii" />
          <StatCounter value="5+" label="Lat doświadczenia" />
          <StatCounter value="100%" label="Zadowolonych klientów" />
        </div>
      </section>

      {/* Featured products */}
      <section className="py-20 px-6 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Nasze usługi</h2>
              <p className="text-gray-500 mt-2">Wybrane pozycje z oferty</p>
            </div>
            <Link to="/products" className="text-sm text-indigo-600 hover:underline font-medium">
              Cała oferta →
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-2xl h-48 animate-pulse border border-gray-100" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {products.map((product) => (
                <Link
                  key={product.slug}
                  to={`/products/${product.slug}`}
                  className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg hover:border-indigo-300 transition-all group"
                >
                  <span className="inline-block text-xs font-medium text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full mb-4">
                    {product.category_name}
                  </span>
                  <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
                    {product.name}
                  </h3>
                  <p className="text-sm text-gray-500 line-clamp-2 mb-4">{product.description}</p>
                  <p className="text-xl font-bold text-gray-900">
                    {Number(product.price).toLocaleString('pl-PL')} zł
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Categories */}
      {!loading && categories.length > 0 && (
        <section className="py-16 px-6 bg-white">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Kategorie usług</h2>
            <div className="flex flex-wrap justify-center gap-3">
              {categories.map((cat) => (
                <Link
                  key={cat.slug}
                  to={`/products?category=${cat.slug}`}
                  className="px-5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-indigo-50 hover:border-indigo-300 hover:text-indigo-700 transition-all"
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Why us */}
      <section className="py-20 px-6 bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-4">Dlaczego Studio?</h2>
          <p className="text-gray-500 text-center mb-12 max-w-xl mx-auto">
            Łączymy design z technologią — każdy projekt realizujemy z dbałością o szczegóły.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {WHY_US.map((item) => (
              <div key={item.title} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <div className="text-3xl mb-4">{item.icon}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-500">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-indigo-600 text-white text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Gotowy na współpracę?</h2>
          <p className="text-indigo-200 mb-8">
            Opisz nam swój projekt — wrócimy z wyceną w ciągu 24 godzin.
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <Link
              to="/contact"
              className="bg-white text-indigo-600 px-7 py-3.5 rounded-xl font-semibold hover:bg-indigo-50 transition-colors"
            >
              Napisz do nas
            </Link>
            <Link
              to="/products"
              className="border border-indigo-400 text-white px-7 py-3.5 rounded-xl font-medium hover:bg-indigo-700 transition-colors"
            >
              Przeglądaj ofertę
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

const WHY_US = [
  {
    icon: '⚡',
    title: 'Szybka realizacja',
    description: 'Proste projekty gotowe w 7 dni. Zawsze dotrzymujemy ustalonych terminów.',
  },
  {
    icon: '🎨',
    title: 'Nowoczesny design',
    description: 'Projekty tworzone zgodnie z aktualnymi trendami UX/UI i wytycznymi dostępności.',
  },
  {
    icon: '📱',
    title: 'Responsywność',
    description: 'Każda strona działa perfekcyjnie na telefonach, tabletach i komputerach.',
  },
  {
    icon: '🔒',
    title: 'Bezpieczeństwo',
    description: 'Stosujemy najlepsze praktyki zabezpieczenia aplikacji webowych.',
  },
  {
    icon: '📈',
    title: 'SEO i wydajność',
    description: 'Optymalizacja pod wyszukiwarki i szybkość ładowania strony w standardzie.',
  },
  {
    icon: '🤝',
    title: 'Wsparcie po wdrożeniu',
    description: 'Nie zostawiamy Cię samego — oferujemy opiekę techniczną po oddaniu projektu.',
  },
]

function StatCounter({ value, label }) {
  return (
    <div>
      <p className="text-4xl font-bold text-indigo-600">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  )
}
