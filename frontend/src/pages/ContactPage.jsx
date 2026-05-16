import { useState } from 'react'
import { sendMessage } from '../api/contact'

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
  const [success, setSuccess] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      await sendMessage(form)
      setSuccess(true)
    } catch (err) {
      setErrors(err.response?.data || {})
    } finally {
      setLoading(false)
    }
  }

  const field = (name, label, type = 'text') => (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        id={name}
        type={type}
        value={form[name]}
        onChange={(e) => setForm({ ...form, [name]: e.target.value })}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        required
      />
      {errors[name] && <p className="text-red-600 text-xs mt-1">{errors[name]}</p>}
    </div>
  )

  if (success) {
    return (
      <div className="max-w-lg mx-auto px-6 py-20 text-center">
        <div className="text-5xl mb-4">✓</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Wiadomość wysłana!</h2>
        <p className="text-gray-500">Odpowiemy najszybciej jak to możliwe.</p>
      </div>
    )
  }

  return (
    <div className="max-w-lg mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Kontakt</h1>
      <p className="text-gray-500 mb-8">Napisz do nas — odpiszemy w ciągu 24 godzin.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {field('name', 'Imię i nazwisko')}
        {field('email', 'Email', 'email')}
        {field('subject', 'Temat')}
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">Wiadomość</label>
          <textarea
            id="message"
            value={form.message}
            onChange={(e) => setForm({ ...form, message: e.target.value })}
            rows={5}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            required
          />
          {errors.message && <p className="text-red-600 text-xs mt-1">{errors.message}</p>}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Wysyłanie...' : 'Wyślij wiadomość'}
        </button>
      </form>
    </div>
  )
}
