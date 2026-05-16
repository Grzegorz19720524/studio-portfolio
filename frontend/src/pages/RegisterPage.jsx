import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api/auth'
import { useAuthStore } from '../store/authStore'

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: '', email: '', password: '', password2: '', phone: '', company: '',
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      await register(form)
      await login({ username: form.username, password: form.password })
      navigate('/')
    } catch (err) {
      setErrors(err.response?.data || {})
    } finally {
      setLoading(false)
    }
  }

  const field = (name, label, type = 'text', required = true) => (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        id={name}
        type={type}
        value={form[name]}
        onChange={(e) => setForm({ ...form, [name]: e.target.value })}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        required={required}
      />
      {errors[name] && <p className="text-red-600 text-xs mt-1">{errors[name]}</p>}
    </div>
  )

  return (
    <div className="max-w-md mx-auto px-6 py-16">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Rejestracja</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {errors.non_field_errors && (
          <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {errors.non_field_errors}
          </p>
        )}
        {field('username', 'Nazwa użytkownika')}
        {field('email', 'Email', 'email')}
        {field('password', 'Hasło', 'password')}
        {field('password2', 'Powtórz hasło', 'password')}
        {field('phone', 'Telefon', 'text', false)}
        {field('company', 'Firma', 'text', false)}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Rejestracja...' : 'Zarejestruj się'}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-500 text-center">
        Masz już konto?{' '}
        <Link to="/login" className="text-indigo-600 hover:underline">Zaloguj się</Link>
      </p>
    </div>
  )
}
