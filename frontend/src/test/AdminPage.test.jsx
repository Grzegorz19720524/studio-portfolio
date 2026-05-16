import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import AdminPage from '../pages/AdminPage'

vi.mock('../api/admin', () => ({
  getAdminStats: vi.fn(),
  getAdminUsers: vi.fn(),
  updateAdminUser: vi.fn(),
  getAdminOrders: vi.fn(),
  setOrderStatus: vi.fn(),
  getContactMessages: vi.fn(),
  markMessageRead: vi.fn(),
  deleteMessage: vi.fn(),
  getAdminProducts: vi.fn(),
  getAdminCategories: vi.fn(),
  createProduct: vi.fn(),
  updateProduct: vi.fn(),
  deleteProduct: vi.fn(),
}))

import {
  getAdminStats, getAdminUsers, updateAdminUser,
  getAdminOrders, setOrderStatus,
  getContactMessages, markMessageRead, deleteMessage,
  getAdminProducts, getAdminCategories, createProduct, updateProduct, deleteProduct,
} from '../api/admin'

const mockStats = {
  users:    { total: 5, active: 4, staff: 1, new_30d: 2 },
  orders:   { total: 3, new_30d: 1, by_status: { pending: 1, in_progress: 2 }, revenue_completed: '4500.00' },
  products: { total: 6, active: 5, inactive: 1 },
  messages: { total: 4, unread: 2 },
}

const mockOrders = [
  { id: 1, status: 'pending',    status_display: 'Oczekuje',   total: '2300.00', items: [{}, {}], created_at: '2026-05-01T10:00:00Z', user_username: 'jan' },
  { id: 2, status: 'completed',  status_display: 'Zakończone', total: '3600.00', items: [{}],     created_at: '2026-05-10T12:00:00Z', user_username: 'anna' },
]

const mockUsers = [
  { id: 1, username: 'jan',   email: 'jan@test.pl',   first_name: 'Jan', last_name: 'Kowalski', company: '', is_staff: false, is_active: true },
  { id: 2, username: 'admin', email: 'admin@test.pl', first_name: '',    last_name: '',         company: '', is_staff: true,  is_active: true },
]

const mockMessages = [
  { id: 1, name: 'Piotr', email: 'piotr@test.pl', subject: 'Zapytanie', message: 'Treść wiadomości.', is_read: false, created_at: '2026-05-12T10:00:00Z' },
  { id: 2, name: 'Anna',  email: 'anna@test.pl',  subject: 'Oferta',    message: 'Inna wiadomość.',   is_read: true,  created_at: '2026-05-13T09:00:00Z' },
]

const mockProducts = [
  { slug: 'strona-www', name: 'Strona WWW', category_name: 'Strony WWW', category: 1, price: '1500.00', is_active: true,  description: 'Opis strony' },
  { slug: 'logo',       name: 'Logo',       category_name: 'Grafika',    category: 2, price: '800.00',  is_active: false, description: 'Opis logo' },
]

const mockCategories = [
  { id: 1, name: 'Strony WWW', slug: 'strony-www' },
  { id: 2, name: 'Grafika',    slug: 'grafika' },
]

function renderAdmin() {
  return render(<MemoryRouter><AdminPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  getAdminStats.mockResolvedValue({ data: mockStats })
  getAdminOrders.mockResolvedValue({ data: { results: mockOrders } })
  getAdminUsers.mockResolvedValue({ data: { results: mockUsers } })
  getContactMessages.mockResolvedValue({ data: { results: mockMessages } })
  getAdminProducts.mockResolvedValue({ data: { results: mockProducts } })
  getAdminCategories.mockResolvedValue({ data: { results: mockCategories } })
  updateAdminUser.mockResolvedValue({ data: {} })
  setOrderStatus.mockResolvedValue({ data: {} })
  markMessageRead.mockResolvedValue({ data: {} })
  deleteMessage.mockResolvedValue({ data: {} })
  createProduct.mockResolvedValue({ data: { ...mockProducts[0], slug: 'nowy', name: 'Nowy Produkt' } })
  updateProduct.mockResolvedValue({ data: mockProducts[0] })
  deleteProduct.mockResolvedValue({ data: {} })
  vi.spyOn(window, 'confirm').mockReturnValue(true)
})

describe('AdminPage — navigation', () => {
  it('renders page heading', () => {
    renderAdmin()
    expect(screen.getByRole('heading', { name: /panel administracyjny/i })).toBeInTheDocument()
  })

  it('renders all 5 tab buttons', () => {
    renderAdmin()
    expect(screen.getByRole('button', { name: 'Statystyki' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Zamówienia' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Użytkownicy' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Wiadomości' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Produkty' })).toBeInTheDocument()
  })

  it('loads StatsTab by default', () => {
    getAdminStats.mockReturnValue(new Promise(() => {}))
    renderAdmin()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
    expect(getAdminStats).toHaveBeenCalled()
  })

  it('switches to OrdersTab on click', async () => {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Zamówienia' }))
    await waitFor(() => {
      expect(screen.getByText('Zamówienie #1')).toBeInTheDocument()
    })
  })

  it('switches to UsersTab on click', async () => {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Użytkownicy' }))
    await waitFor(() => {
      expect(screen.getByText('jan@test.pl')).toBeInTheDocument()
    })
  })

  it('switches to MessagesTab on click', async () => {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Wiadomości' }))
    await waitFor(() => {
      expect(screen.getByText('Zapytanie')).toBeInTheDocument()
    })
  })

  it('switches to ProductsTab on click', async () => {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Produkty' }))
    await waitFor(() => {
      expect(screen.getByText('Strona WWW')).toBeInTheDocument()
    })
  })
})

describe('AdminPage — StatsTab', () => {
  it('shows loading spinner initially', () => {
    getAdminStats.mockReturnValue(new Promise(() => {}))
    renderAdmin()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
  })

  it('renders order status chart section', async () => {
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText('Zamówienia według statusu')).toBeInTheDocument()
    })
  })

  it('shows users new_30d sub-text', async () => {
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText(/2 nowych w ciągu 30 dni/i)).toBeInTheDocument()
    })
  })

  it('shows products active/inactive sub-text', async () => {
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText(/5 aktywnych · 1 nieaktywnych/i)).toBeInTheDocument()
    })
  })

  it('shows revenue BigStat label', async () => {
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText(/przychód/i)).toBeInTheDocument()
    })
  })

  it('shows unread messages count in stats', async () => {
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText('Wiadomości kontaktowe')).toBeInTheDocument()
    })
  })
})

describe('AdminPage — OrdersTab', () => {
  async function openOrdersTab() {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Zamówienia' }))
    await waitFor(() => screen.getByText('Zamówienie #1'))
  }

  it('shows order count summary', async () => {
    await openOrdersTab()
    expect(screen.getByText(/2 zamówień/i)).toBeInTheDocument()
  })

  it('renders both order cards', async () => {
    await openOrdersTab()
    expect(screen.getByText('Zamówienie #1')).toBeInTheDocument()
    expect(screen.getByText('Zamówienie #2')).toBeInTheDocument()
  })

  it('shows order username', async () => {
    await openOrdersTab()
    expect(screen.getByText('jan')).toBeInTheDocument()
  })

  it('shows order total', async () => {
    await openOrdersTab()
    expect(screen.getByText('2300.00 zł')).toBeInTheDocument()
  })

  it('renders status dropdowns for each order', async () => {
    await openOrdersTab()
    expect(screen.getAllByRole('combobox').length).toBe(2)
  })

  it('changing status dropdown calls setOrderStatus', async () => {
    await openOrdersTab()
    const selects = screen.getAllByRole('combobox')
    await userEvent.selectOptions(selects[0], 'completed')
    await waitFor(() => {
      expect(setOrderStatus).toHaveBeenCalledWith(1, 'completed')
    })
  })

  it('shows empty state when no orders', async () => {
    getAdminOrders.mockResolvedValue({ data: { results: [] } })
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Zamówienia' }))
    await waitFor(() => {
      expect(screen.getByText(/brak zamówień/i)).toBeInTheDocument()
    })
  })
})

describe('AdminPage — UsersTab', () => {
  async function openUsersTab() {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Użytkownicy' }))
    await waitFor(() => screen.getByText('jan@test.pl'))
  }

  it('shows user count summary', async () => {
    await openUsersTab()
    expect(screen.getByText(/2 użytkowników/i)).toBeInTheDocument()
  })

  it('renders username and email', async () => {
    await openUsersTab()
    expect(screen.getByText('jan')).toBeInTheDocument()
    expect(screen.getByText('jan@test.pl')).toBeInTheDocument()
  })

  it('shows Admin badge for staff user', async () => {
    await openUsersTab()
    expect(screen.getByText('Admin')).toBeInTheDocument()
  })

  it('shows Dezaktywuj button for active non-staff user', async () => {
    await openUsersTab()
    expect(screen.getByRole('button', { name: /dezaktywuj/i })).toBeInTheDocument()
  })

  it('shows no toggle button for staff user', async () => {
    await openUsersTab()
    const toggles = screen.queryAllByRole('button', { name: /dezaktywuj|aktywuj/i })
    expect(toggles.length).toBe(1)
  })

  it('clicking Dezaktywuj calls updateAdminUser with is_active false', async () => {
    await openUsersTab()
    await userEvent.click(screen.getByRole('button', { name: /dezaktywuj/i }))
    await waitFor(() => {
      expect(updateAdminUser).toHaveBeenCalledWith(1, { is_active: false })
    })
  })

  it('toggle updates user status in UI', async () => {
    await openUsersTab()
    await userEvent.click(screen.getByRole('button', { name: /dezaktywuj/i }))
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /aktywuj/i })).toBeInTheDocument()
    })
  })
})

describe('AdminPage — MessagesTab', () => {
  async function openMessagesTab() {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Wiadomości' }))
    await waitFor(() => screen.getByText('Zapytanie'))
  }

  it('shows message count and unread', async () => {
    await openMessagesTab()
    expect(screen.getByText(/1 nieprzeczytanych/i)).toBeInTheDocument()
  })

  it('renders message subjects', async () => {
    await openMessagesTab()
    expect(screen.getByText('Zapytanie')).toBeInTheDocument()
    expect(screen.getByText('Oferta')).toBeInTheDocument()
  })

  it('expands message and shows content on click', async () => {
    await openMessagesTab()
    await userEvent.click(screen.getByText('Zapytanie'))
    await waitFor(() => {
      expect(screen.getByText('Treść wiadomości.')).toBeInTheDocument()
    })
  })

  it('clicking "Oznacz jako przeczytane" calls markMessageRead', async () => {
    await openMessagesTab()
    await userEvent.click(screen.getByText('Zapytanie'))
    await waitFor(() => screen.getByRole('button', { name: /oznacz jako przeczytane/i }))
    await userEvent.click(screen.getByRole('button', { name: /oznacz jako przeczytane/i }))
    await waitFor(() => {
      expect(markMessageRead).toHaveBeenCalledWith(1, true)
    })
  })

  it('clicking Usuń calls deleteMessage', async () => {
    await openMessagesTab()
    await userEvent.click(screen.getByText('Zapytanie'))
    await waitFor(() => screen.getByRole('button', { name: /usuń/i }))
    await userEvent.click(screen.getByRole('button', { name: /usuń/i }))
    await waitFor(() => {
      expect(deleteMessage).toHaveBeenCalledWith(1)
    })
  })

  it('deleted message disappears from list', async () => {
    await openMessagesTab()
    await userEvent.click(screen.getByText('Zapytanie'))
    await waitFor(() => screen.getByRole('button', { name: /usuń/i }))
    await userEvent.click(screen.getByRole('button', { name: /usuń/i }))
    await waitFor(() => {
      expect(screen.queryByText('Zapytanie')).not.toBeInTheDocument()
    })
  })
})

describe('AdminPage — ProductsTab', () => {
  async function openProductsTab() {
    renderAdmin()
    await userEvent.click(screen.getByRole('button', { name: 'Produkty' }))
    await waitFor(() => screen.getByText('Strona WWW'))
  }

  it('shows product count summary', async () => {
    await openProductsTab()
    expect(screen.getByText(/2 produktów/i)).toBeInTheDocument()
  })

  it('renders product names in table', async () => {
    await openProductsTab()
    expect(screen.getByText('Strona WWW')).toBeInTheDocument()
    expect(screen.getByText('Logo')).toBeInTheDocument()
  })

  it('shows product prices', async () => {
    await openProductsTab()
    expect(screen.getByText('1500.00 zł')).toBeInTheDocument()
  })

  it('shows Aktywny and Nieaktywny status buttons', async () => {
    await openProductsTab()
    expect(screen.getByRole('button', { name: 'Aktywny' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Nieaktywny' })).toBeInTheDocument()
  })

  it('clicking toggle active calls updateProduct', async () => {
    await openProductsTab()
    await userEvent.click(screen.getByRole('button', { name: 'Aktywny' }))
    await waitFor(() => {
      expect(updateProduct).toHaveBeenCalledWith('strona-www', { is_active: false })
    })
  })

  it('clicking Usuń calls deleteProduct', async () => {
    await openProductsTab()
    const deleteButtons = screen.getAllByRole('button', { name: 'Usuń' })
    await userEvent.click(deleteButtons[0])
    await waitFor(() => {
      expect(deleteProduct).toHaveBeenCalledWith('strona-www')
    })
  })

  it('clicking "+ Nowy produkt" opens modal', async () => {
    await openProductsTab()
    await userEvent.click(screen.getByRole('button', { name: /\+ nowy produkt/i }))
    expect(screen.getByRole('heading', { name: /nowy produkt/i })).toBeInTheDocument()
  })

  it('modal closes on Anuluj', async () => {
    await openProductsTab()
    await userEvent.click(screen.getByRole('button', { name: /\+ nowy produkt/i }))
    await userEvent.click(screen.getByRole('button', { name: /anuluj/i }))
    expect(screen.queryByRole('heading', { name: /nowy produkt/i })).not.toBeInTheDocument()
  })

  it('clicking Edytuj opens modal with "Edytuj produkt" heading', async () => {
    await openProductsTab()
    const editButtons = screen.getAllByRole('button', { name: 'Edytuj' })
    await userEvent.click(editButtons[0])
    expect(screen.getByRole('heading', { name: /edytuj produkt/i })).toBeInTheDocument()
  })

  it('submitting new product form calls createProduct', async () => {
    await openProductsTab()
    await userEvent.click(screen.getByRole('button', { name: /\+ nowy produkt/i }))
    await userEvent.selectOptions(screen.getByLabelText(/kategoria/i), '1')
    await userEvent.type(screen.getByLabelText(/^nazwa$/i), 'Nowy Produkt')
    await userEvent.type(screen.getByLabelText(/cena/i), '999')
    await userEvent.click(screen.getByRole('button', { name: /^zapisz$/i }))
    await waitFor(() => {
      expect(createProduct).toHaveBeenCalled()
    })
  })

  it('submitting edit form calls updateProduct', async () => {
    await openProductsTab()
    const editButtons = screen.getAllByRole('button', { name: 'Edytuj' })
    await userEvent.click(editButtons[0])
    await userEvent.click(screen.getByRole('button', { name: /^zapisz$/i }))
    await waitFor(() => {
      expect(updateProduct).toHaveBeenCalledWith('strona-www', expect.any(Object))
    })
  })
})
