import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-20 text-center">
      <h1 className="text-5xl font-bold text-gray-900 mb-6">
        Studio — agencja kreatywna
      </h1>
      <p className="text-xl text-gray-500 mb-10 max-w-xl mx-auto">
        Tworzymy strony internetowe, aplikacje i identyfikacje wizualne dla firm każdej wielkości.
      </p>
      <div className="flex justify-center gap-4">
        <Link
          to="/products"
          className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-indigo-700 transition-colors"
        >
          Zobacz ofertę
        </Link>
        <Link
          to="/contact"
          className="border border-gray-300 text-gray-700 px-6 py-3 rounded-xl font-medium hover:border-indigo-400 hover:text-indigo-600 transition-colors"
        >
          Skontaktuj się
        </Link>
      </div>
    </div>
  )
}
