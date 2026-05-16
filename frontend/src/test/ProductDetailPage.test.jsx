import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import ProductDetailPage from '../pages/ProductDetailPage'

vi.mock('../api/products', () => ({ getProduct: vi.fn() }))
vi.mock('../api/orders',   () => ({ createOrder: vi.fn() }))
vi.mock('../store/authStore', () => ({ useAuthStore: vi.fn() }))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useParams: () => ({ slug: 'strona-www' }), useNavigate: () => mockNavigate }
})

import { getProduct } from '../api/products'
import { createOrder } from '../api/orders'
import { useAuthStore } from '../store/authStore'

const mockProduct = {
  id: 1,
  slug: 'strona-www',
  name: 'Strona WWW',
  category_name: 'Strony WWW',
  description: 'Profesjonalna strona internetowa.',
  price: '1500.00',
}

const mockUser = { id: 1, username: 'jan' }

function renderProduct() {
  return render(<MemoryRouter><ProductDetailPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  getProduct.mockResolvedValue({ data: mockProduct })
  useAuthStore.mockReturnValue({ user: mockUser })
})

describe('ProductDetailPage — rendering', () => {
  it('shows loading state initially', () => {
    getProduct.mockReturnValue(new Promise(() => {}))
    renderProduct()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
  })

  it('renders product name after loading', async () => {
    renderProduct()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Strona WWW' })).toBeInTheDocument()
    })
  })

  it('renders product category', async () => {
    renderProduct()
    await waitFor(() => {
      expect(screen.getByText('Strony WWW')).toBeInTheDocument()
    })
  })

  it('renders product description', async () => {
    renderProduct()
    await waitFor(() => {
      expect(screen.getByText('Profesjonalna strona internetowa.')).toBeInTheDocument()
    })
  })

  it('renders product price', async () => {
    renderProduct()
    await waitFor(() => {
      expect(screen.getByText('1500.00 zł')).toBeInTheDocument()
    })
  })

  it('renders "Brak opisu." when description is empty', async () => {
    getProduct.mockResolvedValue({ data: { ...mockProduct, description: '' } })
    renderProduct()
    await waitFor(() => {
      expect(screen.getByText('Brak opisu.')).toBeInTheDocument()
    })
  })

  it('renders "Zamów" button', async () => {
    renderProduct()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /zamów/i })).toBeInTheDocument()
    })
  })

  it('renders quantity controls', async () => {
    renderProduct()
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: '+' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: '−' })).toBeInTheDocument()
    })
  })

  it('navigates to /products when product fetch fails', async () => {
    getProduct.mockRejectedValue(new Error('Not found'))
    renderProduct()
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/products')
    })
  })
})

describe('ProductDetailPage — quantity controls', () => {
  it('increases quantity on + click', async () => {
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: '+' }))
    await userEvent.click(screen.getByRole('button', { name: '+' }))
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('decreases quantity on − click', async () => {
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: '+' }))
    await userEvent.click(screen.getByRole('button', { name: '+' }))
    await userEvent.click(screen.getByRole('button', { name: '+' }))
    await userEvent.click(screen.getByRole('button', { name: '−' }))
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('does not decrease quantity below 1', async () => {
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: '−' }))
    await userEvent.click(screen.getByRole('button', { name: '−' }))
    expect(screen.getByText('1')).toBeInTheDocument()
  })
})

describe('ProductDetailPage — ordering', () => {
  it('redirects to /login when not logged in', async () => {
    useAuthStore.mockReturnValue({ user: null })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  it('calls createOrder with product id and quantity', async () => {
    createOrder.mockResolvedValue({ data: {} })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    await waitFor(() => {
      expect(createOrder).toHaveBeenCalledWith({ items: [{ product: 1, quantity: 1 }] })
    })
  })

  it('shows success state after ordering', async () => {
    createOrder.mockResolvedValue({ data: {} })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    await waitFor(() => {
      expect(screen.getByText(/zamówienie zostało złożone/i)).toBeInTheDocument()
    })
  })

  it('hides order button after success', async () => {
    createOrder.mockResolvedValue({ data: {} })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: 'Zamów' }))
    await userEvent.click(screen.getByRole('button', { name: 'Zamów' }))
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: 'Zamów' })).not.toBeInTheDocument()
    })
  })

  it('shows "Zobacz swoje zamówienia" button after success', async () => {
    createOrder.mockResolvedValue({ data: {} })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /zobacz swoje zamówienia/i })).toBeInTheDocument()
    })
  })

  it('"Zobacz swoje zamówienia" navigates to /orders', async () => {
    createOrder.mockResolvedValue({ data: {} })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    await waitFor(() => screen.getByRole('button', { name: /zobacz swoje zamówienia/i }))
    await userEvent.click(screen.getByRole('button', { name: /zobacz swoje zamówienia/i }))
    expect(mockNavigate).toHaveBeenCalledWith('/orders')
  })

  it('shows error message on API failure', async () => {
    createOrder.mockRejectedValue({ response: { data: { detail: 'Błąd serwera.' } } })
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    await waitFor(() => {
      expect(screen.getByText('Błąd serwera.')).toBeInTheDocument()
    })
  })

  it('disables button while ordering', async () => {
    createOrder.mockReturnValue(new Promise(() => {}))
    renderProduct()
    await waitFor(() => screen.getByRole('button', { name: /zamów/i }))
    await userEvent.click(screen.getByRole('button', { name: /zamów/i }))
    expect(screen.getByRole('button', { name: /składanie/i })).toBeDisabled()
  })
})
