import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import OrderDetailPage from '../pages/OrderDetailPage'

vi.mock('../api/orders', () => ({ getOrder: vi.fn() }))

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useParams: () => ({ id: '1' }) }
})

import { getOrder } from '../api/orders'

const mockOrder = {
  id: 1,
  status: 'in_progress',
  status_display: 'W realizacji',
  total: '2300.00',
  created_at: '2026-05-01T10:00:00Z',
  notes: '',
  items: [
    { id: 1, product_name: 'Strona WWW', unit_price: '1500.00', quantity: 1, subtotal: '1500.00' },
    { id: 2, product_name: 'Logo firmowe', unit_price: '800.00',  quantity: 1, subtotal: '800.00' },
  ],
}

function renderOrder() {
  return render(<MemoryRouter><OrderDetailPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  getOrder.mockResolvedValue({ data: mockOrder })
})

describe('OrderDetailPage — rendering', () => {
  it('shows loading state initially', () => {
    getOrder.mockReturnValue(new Promise(() => {}))
    renderOrder()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
  })

  it('shows "Nie znaleziono zamówienia." when order is null', async () => {
    getOrder.mockResolvedValue({ data: null })
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText(/nie znaleziono zamówienia/i)).toBeInTheDocument()
    })
  })

  it('renders heading with order id', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /zamówienie #1/i })).toBeInTheDocument()
    })
  })

  it('renders status badge', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText('W realizacji')).toBeInTheDocument()
    })
  })

  it('renders order items with product names', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText('Strona WWW')).toBeInTheDocument()
      expect(screen.getByText('Logo firmowe')).toBeInTheDocument()
    })
  })

  it('renders item unit price and quantity', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText('1500.00 zł × 1')).toBeInTheDocument()
    })
  })

  it('renders item subtotal', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText('1500.00 zł')).toBeInTheDocument()
    })
  })

  it('renders order total', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText('2300.00 zł')).toBeInTheDocument()
    })
  })

  it('renders "Wróć do zamówień" link', async () => {
    renderOrder()
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /wróć do zamówień/i })).toHaveAttribute('href', '/orders')
    })
  })
})

describe('OrderDetailPage — notes', () => {
  it('renders notes when present', async () => {
    getOrder.mockResolvedValue({ data: { ...mockOrder, notes: 'Proszę o szybką realizację.' } })
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText('Proszę o szybką realizację.')).toBeInTheDocument()
    })
  })

  it('does not render notes section when notes is empty', async () => {
    renderOrder()
    await waitFor(() => screen.getByRole('heading', { name: /zamówienie #1/i }))
    expect(screen.queryByText('Uwagi')).not.toBeInTheDocument()
  })
})

describe('OrderDetailPage — status colors', () => {
  it.each([
    ['pending',     'Oczekuje'],
    ['confirmed',   'Potwierdzone'],
    ['completed',   'Zakończone'],
    ['cancelled',   'Anulowane'],
  ])('renders "%s" status badge', async (status, label) => {
    getOrder.mockResolvedValue({ data: { ...mockOrder, status, status_display: label } })
    renderOrder()
    await waitFor(() => {
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })
})
