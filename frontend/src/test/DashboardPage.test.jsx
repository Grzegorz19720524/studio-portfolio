import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DashboardPage from '../pages/DashboardPage'

vi.mock('../api/orders', () => ({
  getOrders: vi.fn(),
}))

vi.mock('../store/authStore', () => ({
  useAuthStore: vi.fn(),
}))

import { getOrders } from '../api/orders'
import { useAuthStore } from '../store/authStore'

const mockUser = { username: 'jan', first_name: 'Jan', last_name: 'Kowalski', email: 'jan@test.pl', is_staff: false }

const mockOrders = [
  { id: 1, status: 'completed', status_display: 'Zakończone', total: '2300.00', items: [{}], created_at: '2026-05-01T10:00:00Z' },
  { id: 2, status: 'in_progress', status_display: 'W realizacji', total: '3600.00', items: [{}], created_at: '2026-05-10T12:00:00Z' },
  { id: 3, status: 'pending', status_display: 'Oczekuje', total: '1500.00', items: [{}], created_at: '2026-05-12T08:00:00Z' },
]

function renderDashboard() {
  return render(<MemoryRouter><DashboardPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  useAuthStore.mockReturnValue({ user: mockUser })
  getOrders.mockResolvedValue({ data: { results: mockOrders } })
})

describe('DashboardPage — greeting', () => {
  it('renders welcome with first name', async () => {
    renderDashboard()
    expect(screen.getByText(/witaj, jan kowalski/i)).toBeInTheDocument()
  })

  it('renders welcome with username when no first name', async () => {
    useAuthStore.mockReturnValue({ user: { ...mockUser, first_name: '', last_name: '' } })
    renderDashboard()
    expect(screen.getByText(/witaj, jan/i)).toBeInTheDocument()
  })
})

describe('DashboardPage — stats', () => {
  it('shows "—" while loading', () => {
    getOrders.mockReturnValue(new Promise(() => {}))
    renderDashboard()
    expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(3)
  })

  it('shows total order count after loading', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  it('shows active orders count (pending + confirmed + in_progress)', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })

  it('shows completed orders count', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })
})

describe('DashboardPage — recent orders', () => {
  it('renders "Ostatnie zamówienia" section', () => {
    renderDashboard()
    expect(screen.getByRole('heading', { name: /ostatnie zamówienia/i })).toBeInTheDocument()
  })

  it('renders order cards after loading', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Zamówienie #1')).toBeInTheDocument()
    })
  })

  it('order card links to detail page', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /zamówienie #1/i })).toHaveAttribute('href', '/orders/1')
    })
  })

  it('renders "Zobacz wszystkie" link', () => {
    renderDashboard()
    expect(screen.getByRole('link', { name: /zobacz wszystkie/i })).toHaveAttribute('href', '/orders')
  })

  it('shows empty state with link to products when no orders', async () => {
    getOrders.mockResolvedValue({ data: { results: [] } })
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText(/nie masz jeszcze żadnych zamówień/i)).toBeInTheDocument()
      const links = screen.getAllByRole('link', { name: /przeglądaj ofertę/i })
      expect(links.every(l => l.getAttribute('href') === '/products')).toBe(true)
    })
  })
})

describe('DashboardPage — quick actions', () => {
  it('renders quick action links', () => {
    renderDashboard()
    expect(screen.getByRole('link', { name: /przeglądaj ofertę/i })).toHaveAttribute('href', '/products')
    expect(screen.getByRole('link', { name: /moje zamówienia/i })).toHaveAttribute('href', '/orders')
    expect(screen.getByRole('link', { name: /edytuj profil/i })).toHaveAttribute('href', '/profile')
    expect(screen.getByRole('link', { name: /napisz do nas/i })).toHaveAttribute('href', '/contact')
  })
})

describe('DashboardPage — account info', () => {
  it('shows username', () => {
    renderDashboard()
    expect(screen.getByText('jan')).toBeInTheDocument()
  })

  it('shows email', () => {
    renderDashboard()
    expect(screen.getByText('jan@test.pl')).toBeInTheDocument()
  })

  it('renders link to profile page', () => {
    renderDashboard()
    expect(screen.getByRole('link', { name: /edytuj dane/i })).toHaveAttribute('href', '/profile')
  })
})
