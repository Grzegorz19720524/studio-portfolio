import { useState, useEffect, useCallback } from 'react'
import {
  getAdminUsers, updateAdminUser,
  getAdminOrders, setOrderStatus,
  getContactMessages, markMessageRead, deleteMessage,
  getAdminProducts, getAdminCategories, createProduct, updateProduct, deleteProduct,
} from '../api/admin'

const TABS = ['Zamówienia', 'Użytkownicy', 'Wiadomości', 'Produkty']

const ORDER_STATUSES = [
  { value: 'pending',     label: 'Oczekuje' },
  { value: 'confirmed',   label: 'Potwierdzone' },
  { value: 'in_progress', label: 'W realizacji' },
  { value: 'completed',   label: 'Zakończone' },
  { value: 'cancelled',   label: 'Anulowane' },
]

const STATUS_COLORS = {
  pending:     'bg-yellow-100 text-yellow-800',
  confirmed:   'bg-blue-100 text-blue-800',
  in_progress: 'bg-purple-100 text-purple-800',
  completed:   'bg-green-100 text-green-800',
  cancelled:   'bg-red-100 text-red-800',
}

export default function AdminPage() {
  const [tab, setTab] = useState(0)

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Panel administracyjny</h1>

      <div className="flex border-b border-gray-200 mb-8 gap-1">
        {TABS.map((name, i) => (
          <button
            key={name}
            onClick={() => setTab(i)}
            className={`px-5 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
              tab === i
                ? 'bg-white border border-b-white border-gray-200 text-indigo-600 -mb-px'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {name}
          </button>
        ))}
      </div>

      {tab === 0 && <OrdersTab />}
      {tab === 1 && <UsersTab />}
      {tab === 2 && <MessagesTab />}
      {tab === 3 && <ProductsTab />}
    </div>
  )
}

/* ─── Orders ─── */

function OrdersTab() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(() => {
    setLoading(true)
    getAdminOrders()
      .then(({ data }) => setOrders(data.results || []))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const handleStatus = async (id, newStatus) => {
    await setOrderStatus(id, newStatus)
    setOrders((prev) =>
      prev.map((o) =>
        o.id === id
          ? { ...o, status: newStatus, status_display: ORDER_STATUSES.find((s) => s.value === newStatus)?.label }
          : o
      )
    )
  }

  if (loading) return <Spinner />

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-500 mb-4">Łącznie: {orders.length} zamówień</p>
      {orders.length === 0 && <Empty text="Brak zamówień." />}
      {orders.map((order) => (
        <div key={order.id} className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div>
              <span className="font-semibold text-gray-900">Zamówienie #{order.id}</span>
              <span className="text-sm text-gray-500 ml-3">
                {order.user_username || order.user}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-bold text-gray-900">{order.total} zł</span>
              <select
                value={order.status}
                onChange={(e) => handleStatus(order.id, e.target.value)}
                className="text-xs border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {ORDER_STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-gray-500">
            <span
              className={`px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-600'}`}
            >
              {order.status_display || order.status}
            </span>
            <span>{order.items?.length || 0} pozycji</span>
            <span>{new Date(order.created_at).toLocaleDateString('pl-PL')}</span>
            {order.notes && <span className="italic">„{order.notes}"</span>}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ─── Users ─── */

function UsersTab() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAdminUsers()
      .then(({ data }) => setUsers(data.results || data))
      .finally(() => setLoading(false))
  }, [])

  const toggleActive = async (user) => {
    const updated = { is_active: !user.is_active }
    await updateAdminUser(user.id, updated)
    setUsers((prev) =>
      prev.map((u) => (u.id === user.id ? { ...u, is_active: !u.is_active } : u))
    )
  }

  if (loading) return <Spinner />

  return (
    <div>
      <p className="text-sm text-gray-500 mb-4">Łącznie: {users.length} użytkowników</p>
      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
            <tr>
              {['#', 'Login', 'Email', 'Imię i nazwisko', 'Firma', 'Rola', 'Status', ''].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 text-gray-400">{user.id}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{user.username}</td>
                <td className="px-4 py-3 text-gray-600">{user.email}</td>
                <td className="px-4 py-3 text-gray-600">
                  {[user.first_name, user.last_name].filter(Boolean).join(' ') || '—'}
                </td>
                <td className="px-4 py-3 text-gray-500">{user.company || '—'}</td>
                <td className="px-4 py-3">
                  {user.is_staff ? (
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">
                      Admin
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                      Klient
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      user.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {user.is_active ? 'Aktywny' : 'Nieaktywny'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {!user.is_staff && (
                    <button
                      onClick={() => toggleActive(user)}
                      className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${
                        user.is_active
                          ? 'bg-red-50 text-red-600 hover:bg-red-100'
                          : 'bg-green-50 text-green-600 hover:bg-green-100'
                      }`}
                    >
                      {user.is_active ? 'Dezaktywuj' : 'Aktywuj'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

/* ─── Messages ─── */

function MessagesTab() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    getContactMessages()
      .then(({ data }) => setMessages(data.results || []))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const toggleRead = async (msg) => {
    await markMessageRead(msg.id, !msg.is_read)
    setMessages((prev) =>
      prev.map((m) => (m.id === msg.id ? { ...m, is_read: !m.is_read } : m))
    )
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Usunąć tę wiadomość?')) return
    await deleteMessage(id)
    setMessages((prev) => prev.filter((m) => m.id !== id))
    if (expanded === id) setExpanded(null)
  }

  const unread = messages.filter((m) => !m.is_read).length

  if (loading) return <Spinner />

  return (
    <div>
      <p className="text-sm text-gray-500 mb-4">
        {messages.length} wiadomości · <span className="text-indigo-600 font-medium">{unread} nieprzeczytanych</span>
      </p>
      {messages.length === 0 && <Empty text="Brak wiadomości." />}
      <div className="space-y-2">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`border rounded-xl overflow-hidden transition-all ${
              msg.is_read ? 'border-gray-200 bg-white' : 'border-indigo-200 bg-indigo-50'
            }`}
          >
            <button
              className="w-full text-left px-5 py-4 flex items-center justify-between gap-4"
              onClick={() => setExpanded(expanded === msg.id ? null : msg.id)}
            >
              <div className="flex items-center gap-3 min-w-0">
                {!msg.is_read && (
                  <span className="w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0" />
                )}
                <div className="min-w-0">
                  <p className="font-semibold text-gray-900 truncate">{msg.subject}</p>
                  <p className="text-xs text-gray-500">
                    {msg.name} &lt;{msg.email}&gt; · {new Date(msg.created_at).toLocaleDateString('pl-PL')}
                  </p>
                </div>
              </div>
              <span className="text-gray-400 text-sm flex-shrink-0">{expanded === msg.id ? '▲' : '▼'}</span>
            </button>

            {expanded === msg.id && (
              <div className="px-5 pb-5 border-t border-gray-100">
                <p className="text-sm text-gray-700 whitespace-pre-wrap mt-4 mb-5">{msg.message}</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => toggleRead(msg)}
                    className="text-xs px-3 py-1.5 rounded-lg border border-gray-300 text-gray-600 hover:border-indigo-400 hover:text-indigo-600 transition-colors"
                  >
                    {msg.is_read ? 'Oznacz jako nieprzeczytane' : 'Oznacz jako przeczytane'}
                  </button>
                  <button
                    onClick={() => handleDelete(msg.id)}
                    className="text-xs px-3 py-1.5 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors"
                  >
                    Usuń
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── Products ─── */

const EMPTY_FORM = { category: '', name: '', slug: '', description: '', price: '', is_active: true }

function toSlug(name) {
  return name
    .toLowerCase()
    .replace(/[ąà]/g, 'a').replace(/[ćč]/g, 'c').replace(/[ęè]/g, 'e')
    .replace(/[łl]/g, 'l').replace(/ń/g, 'n').replace(/[óò]/g, 'o')
    .replace(/[śš]/g, 's').replace(/[źżž]/g, 'z')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function ProductsTab() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null) // null | 'create' | product object

  const load = useCallback(() => {
    setLoading(true)
    Promise.all([getAdminProducts(), getAdminCategories()])
      .then(([p, c]) => {
        setProducts(p.data.results || [])
        setCategories(c.data.results || [])
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const handleToggleActive = async (product) => {
    await updateProduct(product.slug, { is_active: !product.is_active })
    setProducts((prev) =>
      prev.map((p) => p.slug === product.slug ? { ...p, is_active: !p.is_active } : p)
    )
  }

  const handleDelete = async (product) => {
    if (!window.confirm(`Usunąć produkt „${product.name}"?`)) return
    await deleteProduct(product.slug)
    setProducts((prev) => prev.filter((p) => p.slug !== product.slug))
  }

  const handleSave = async (formData, originalSlug) => {
    if (originalSlug) {
      const { data } = await updateProduct(originalSlug, formData)
      setProducts((prev) => prev.map((p) => p.slug === originalSlug ? data : p))
    } else {
      const { data } = await createProduct(formData)
      setProducts((prev) => [data, ...prev])
    }
    setModal(null)
  }

  if (loading) return <Spinner />

  const active = products.filter((p) => p.is_active).length
  const inactive = products.length - active

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          Łącznie: {products.length} produktów · <span className="text-green-600">{active} aktywnych</span>
          {inactive > 0 && <span className="text-gray-400"> · {inactive} nieaktywnych</span>}
        </p>
        <button
          onClick={() => setModal('create')}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          + Nowy produkt
        </button>
      </div>

      {products.length === 0 && <Empty text="Brak produktów." />}

      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
            <tr>
              {['Nazwa', 'Kategoria', 'Cena', 'Status', 'Slug', ''].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {products.map((product) => (
              <tr key={product.slug} className={`hover:bg-gray-50 transition-colors ${!product.is_active ? 'opacity-60' : ''}`}>
                <td className="px-4 py-3 font-medium text-gray-900">{product.name}</td>
                <td className="px-4 py-3 text-gray-500">{product.category_name || '—'}</td>
                <td className="px-4 py-3 text-gray-900 font-medium whitespace-nowrap">{product.price} zł</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleToggleActive(product)}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                      product.is_active
                        ? 'bg-green-100 text-green-700 hover:bg-green-200'
                        : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                    }`}
                  >
                    {product.is_active ? 'Aktywny' : 'Nieaktywny'}
                  </button>
                </td>
                <td className="px-4 py-3 text-gray-400 font-mono text-xs">{product.slug}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setModal(product)}
                      className="text-xs px-3 py-1 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors font-medium"
                    >
                      Edytuj
                    </button>
                    <button
                      onClick={() => handleDelete(product)}
                      className="text-xs px-3 py-1 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors font-medium"
                    >
                      Usuń
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <ProductModal
          product={modal === 'create' ? null : modal}
          categories={categories}
          onSave={handleSave}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  )
}

function ProductModal({ product, categories, onSave, onClose }) {
  const [form, setForm] = useState(
    product
      ? {
          category: product.category ?? '',
          name: product.name,
          slug: product.slug,
          description: product.description,
          price: product.price,
          is_active: product.is_active,
        }
      : { ...EMPTY_FORM }
  )
  const [errors, setErrors] = useState({})
  const [saving, setSaving] = useState(false)

  const set = (field, value) => {
    setForm((prev) => {
      const next = { ...prev, [field]: value }
      if (field === 'name' && !product) next.slug = toSlug(value)
      return next
    })
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setSaving(true)
    try {
      await onSave(form, product?.slug ?? null)
    } catch (err) {
      setErrors(err.response?.data || { detail: 'Błąd zapisu.' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">
            {product ? 'Edytuj produkt' : 'Nowy produkt'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <Field label="Kategoria" error={errors.category}>
            <select
              value={form.category}
              onChange={(e) => set('category', e.target.value)}
              className="input"
              required
            >
              <option value="">— wybierz —</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </Field>

          <Field label="Nazwa" error={errors.name}>
            <input
              type="text"
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              className="input"
              required
            />
          </Field>

          <Field label="Slug" error={errors.slug}>
            <input
              type="text"
              value={form.slug}
              onChange={(e) => set('slug', e.target.value)}
              className="input font-mono text-sm"
              required
            />
          </Field>

          <Field label="Opis" error={errors.description}>
            <textarea
              value={form.description}
              onChange={(e) => set('description', e.target.value)}
              rows={4}
              className="input resize-none"
            />
          </Field>

          <Field label="Cena (zł)" error={errors.price}>
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.price}
              onChange={(e) => set('price', e.target.value)}
              className="input"
              required
            />
          </Field>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => set('is_active', e.target.checked)}
              className="w-4 h-4 rounded accent-indigo-600"
            />
            <span className="text-sm font-medium text-gray-700">Aktywny</span>
          </label>

          {errors.detail && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">{errors.detail}</p>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={saving}
              className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {saving ? 'Zapisywanie…' : 'Zapisz'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 py-2.5 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Anuluj
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Field({ label, error, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {children}
      {error && <p className="text-red-600 text-xs mt-1">{Array.isArray(error) ? error[0] : error}</p>}
    </div>
  )
}

/* ─── Helpers ─── */

function Spinner() {
  return <p className="text-center py-20 text-gray-400">Ładowanie...</p>
}

function Empty({ text }) {
  return <p className="text-center py-12 text-gray-400">{text}</p>
}
