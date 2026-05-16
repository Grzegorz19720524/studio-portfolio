import { useState, useEffect, useCallback } from 'react'
import {
  getAdminUsers, updateAdminUser,
  getAdminOrders, setOrderStatus,
  getContactMessages, markMessageRead, deleteMessage,
} from '../api/admin'

const TABS = ['Zamówienia', 'Użytkownicy', 'Wiadomości']

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

/* ─── Helpers ─── */

function Spinner() {
  return <p className="text-center py-20 text-gray-400">Ładowanie...</p>
}

function Empty({ text }) {
  return <p className="text-center py-12 text-gray-400">{text}</p>
}
