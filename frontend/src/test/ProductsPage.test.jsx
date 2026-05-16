import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import ProductsPage from '../pages/ProductsPage'

vi.mock('../api/products', () => ({
  getProducts: vi.fn(),
  getCategories: vi.fn(),
}))

import { getProducts, getCategories } from '../api/products'

const mockProducts = [
  { id: 1, slug: 'strona-www', name: 'Strona WWW', category_name: 'Strony WWW', description: 'Opis strony.', price: '1500.00' },
  { id: 2, slug: 'logo', name: 'Logo firmowe', category_name: 'Grafika', description: 'Profesjonalne logo.', price: '800.00' },
]

const mockCategories = [
  { id: 1, name: 'Strony WWW', slug: 'strony-www' },
  { id: 2, name: 'Grafika', slug: 'grafika' },
]

function renderProducts() {
  return render(<MemoryRouter><ProductsPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  getProducts.mockResolvedValue({ data: { results: mockProducts } })
  getCategories.mockResolvedValue({ data: { results: mockCategories } })
})

describe('ProductsPage — rendering', () => {
  it('renders heading "Oferta"', async () => {
    renderProducts()
    expect(screen.getByRole('heading', { name: /oferta/i })).toBeInTheDocument()
  })

  it('renders search input', () => {
    renderProducts()
    expect(screen.getByPlaceholderText(/szukaj/i)).toBeInTheDocument()
  })

  it('renders ordering select', () => {
    renderProducts()
    expect(screen.getAllByRole('combobox').length).toBeGreaterThanOrEqual(2)
  })

  it('shows loading state initially', () => {
    getProducts.mockReturnValue(new Promise(() => {}))
    renderProducts()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
  })

  it('renders products after loading', async () => {
    renderProducts()
    await waitFor(() => {
      expect(screen.getByText('Strona WWW')).toBeInTheDocument()
      expect(screen.getByText('Logo firmowe')).toBeInTheDocument()
    })
  })

  it('shows empty state when no products', async () => {
    getProducts.mockResolvedValue({ data: { results: [] } })
    renderProducts()
    await waitFor(() => {
      expect(screen.getByText(/brak produktów/i)).toBeInTheDocument()
    })
  })

  it('product card links to correct URL', async () => {
    renderProducts()
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /strona www/i })).toHaveAttribute('href', '/products/strona-www')
    })
  })

  it('product card shows price', async () => {
    renderProducts()
    await waitFor(() => {
      expect(screen.getByText('1500.00 zł')).toBeInTheDocument()
    })
  })

  it('renders category options in select', async () => {
    renderProducts()
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'Strony WWW' })).toBeInTheDocument()
      expect(screen.getByRole('option', { name: 'Grafika' })).toBeInTheDocument()
    })
  })
})

describe('ProductsPage — filters', () => {
  it('calls getProducts with search param on input', async () => {
    renderProducts()
    await waitFor(() => screen.getByText('Strona WWW'))
    await userEvent.type(screen.getByPlaceholderText(/szukaj/i), 'logo')
    await waitFor(() => {
      expect(getProducts).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'logo' })
      )
    })
  })

  it('calls getProducts with category param on select change', async () => {
    renderProducts()
    await waitFor(() => screen.getByText('Strona WWW'))
    const selects = screen.getAllByRole('combobox')
    await userEvent.selectOptions(selects[0], 'strony-www')
    await waitFor(() => {
      expect(getProducts).toHaveBeenCalledWith(
        expect.objectContaining({ category: 'strony-www' })
      )
    })
  })
})
