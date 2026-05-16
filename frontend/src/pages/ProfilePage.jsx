import { useState } from 'react'
import { updateMe, changePassword } from '../api/auth'
import { useAuthStore } from '../store/authStore'

export default function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const [form, setForm] = useState({
    email: user.email || '',
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    phone: user.phone || '',
    company: user.company || '',
  })
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', new_password2: '' })
  const [profileMsg, setProfileMsg] = useState('')
  const [pwMsg, setPwMsg] = useState('')
  const [profileErrors, setProfileErrors] = useState({})
  const [pwErrors, setPwErrors] = useState({})

  const handleProfile = async (e) => {
    e.preventDefault()
    setProfileErrors({})
    setProfileMsg('')
    try {
      const { data } = await updateMe(form)
      setUser(data)
      setProfileMsg('Profil zaktualizowany.')
    } catch (err) {
      setProfileErrors(err.response?.data || {})
    }
  }

  const handlePassword = async (e) => {
    e.preventDefault()
    setPwErrors({})
    setPwMsg('')
    try {
      await changePassword(pwForm)
      setPwMsg('Hasło zostało zmienione.')
      setPwForm({ old_password: '', new_password: '', new_password2: '' })
    } catch (err) {
      setPwErrors(err.response?.data || {})
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-12 space-y-12">
      <section>
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Profil</h1>
        <p className="text-gray-500 text-sm mb-6">Konto: <strong>{user.username}</strong></p>

        <form onSubmit={handleProfile} className="space-y-4">
          {profileMsg && <p className="text-green-600 text-sm bg-green-50 border border-green-200 rounded-lg p-3">{profileMsg}</p>}
          {[
            ['email', 'Email', 'email'],
            ['first_name', 'Imię', 'text'],
            ['last_name', 'Nazwisko', 'text'],
            ['phone', 'Telefon', 'text'],
            ['company', 'Firma', 'text'],
          ].map(([name, label, type]) => (
            <div key={name}>
              <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                id={name}
                type={type}
                value={form[name]}
                onChange={(e) => setForm({ ...form, [name]: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              {profileErrors[name] && <p className="text-red-600 text-xs mt-1">{profileErrors[name]}</p>}
            </div>
          ))}
          <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors">
            Zapisz
          </button>
        </form>
      </section>

      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-6">Zmiana hasła</h2>
        <form onSubmit={handlePassword} className="space-y-4">
          {pwMsg && <p className="text-green-600 text-sm bg-green-50 border border-green-200 rounded-lg p-3">{pwMsg}</p>}
          {[
            ['old_password', 'Stare hasło'],
            ['new_password', 'Nowe hasło'],
            ['new_password2', 'Powtórz nowe hasło'],
          ].map(([name, label]) => (
            <div key={name}>
              <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                id={name}
                type="password"
                value={pwForm[name]}
                onChange={(e) => setPwForm({ ...pwForm, [name]: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
              {pwErrors[name] && <p className="text-red-600 text-xs mt-1">{pwErrors[name]}</p>}
            </div>
          ))}
          <button type="submit" className="bg-gray-800 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-900 transition-colors">
            Zmień hasło
          </button>
        </form>
      </section>
    </div>
  )
}
