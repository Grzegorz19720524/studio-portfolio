import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import OrdersPage from '../pages/OrdersPage'

vi.mock('../api/orders', () => ({
  getOrders: vi.fn(),
}))

import { getOrders } from '../api/orders'

const mockOrders = [
  {
    id: 1,
    status: 'completed',
    status_display: 'Zakończone',
    total: '2300.00',
    items: [{ id: 1 }, { id: 2 }],
    created_at: '2026-05-01T10:00:00Z',
  },
  {
    id: 2,
    status: 'in_progress',
    status_display: 'W realizacji',
    total: '3600.00',
    items: [{ id: 3 }],
    created_at: '2026-05-10T12:00:00Z',
  },
]

function renderOrders() {
  return render(<MemoryRouter><OrdersPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  getOrders.mockResolvedValue({ data: { results: mockOrders } })
})

describe('OrdersPage — rendering', () => {
  it('shows loading state initially', () => {
    getOrders.mockReturnValue(new Promise(() => {}))
    renderOrders()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
  })

  it('renders heading after loading', async () => {
    renderOrders()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /moje zamówienia/i })).toBeInTheDocument()
    })
  })

  it('renders order cards', async () => {
    renderOrders()
    await waitFor(() => {
      expect(screen.getByText('Zamówienie #1')).toBeInTheDocument()
      expect(screen.getByText('Zamówienie #2')).toBeInTheDocument()
    })
  })

  it('renders order status badge', async () => {
    renderOrders()
    await waitFor(() => {
      expect(screen.getByText('Zakończone')).toBeInTheDocument()
      expect(screen.getByText('W realizacji')).toBeInTheDocument()
    })
  })

  it('renders order total', async () => {
    renderOrders()
    await waitFor(() => {
      expect(screen.getByText('2300.00 zł')).toBeInTheDocument()
    })
  })

  it('order card links to detail page', async () => {
    renderOrders()
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /zamówienie #1/i })).toHaveAttribute('href', '/orders/1')
    })
  })

  it('renders item count', async () => {
    renderOrders()
    await waitFor(() => {
      expect(screen.getByText('2 pozycji')).toBeInTheDocument()
    })
  })
})

describe('OrdersPage — empty state', () => {
  it('shows empty state when no orders', async () => {
    getOrders.mockResolvedValue({ data: { results: [] } })
    renderOrders()
    await waitFor(() => {
      expect(screen.getByText(/brak zamówień/i)).toBeInTheDocument()
    })
  })

  it('shows link to products in empty state', async () => {
    getOrders.mockResolvedValue({ data: { results: [] } })
    renderOrders()
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /przeglądaj ofertę/i })).toHaveAttribute('href', '/products')
    })
  })
})
