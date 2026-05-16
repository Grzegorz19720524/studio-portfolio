import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import HomePage from '../pages/HomePage'

const mockProducts = [
  {
    slug: 'strona-wizytowka',
    name: 'Strona wizytówka',
    category_name: 'Strony WWW',
    description: 'Prosta, elegancka strona prezentująca Twoją firmę.',
    price: '1500.00',
    is_active: true,
  },
  {
    slug: 'logo-firmowe',
    name: 'Logo firmowe',
    category_name: 'Grafika',
    description: 'Profesjonalne logo w 3 wariantach.',
    price: '800.00',
    is_active: true,
  },
  {
    slug: 'kampania-google-ads',
    name: 'Kampania Google Ads',
    category_name: 'Marketing',
    description: 'Konfiguracja i prowadzenie kampanii.',
    price: '1200.00',
    is_active: true,
  },
]

const mockCategories = [
  { id: 1, name: 'Strony WWW', slug: 'strony-www' },
  { id: 2, name: 'Grafika', slug: 'grafika' },
  { id: 3, name: 'Marketing', slug: 'marketing' },
]

vi.mock('../api/products', () => ({
  getProducts: vi.fn(),
  getCategories: vi.fn(),
}))

import { getProducts, getCategories } from '../api/products'

function renderHomePage() {
  return render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  getProducts.mockResolvedValue({ data: { count: 6, results: mockProducts } })
  getCategories.mockResolvedValue({ data: { count: 3, results: mockCategories } })
})

describe('HomePage — hero', () => {
  it('renders main heading', async () => {
    renderHomePage()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  it('renders "Zobacz ofertę" link to /products', async () => {
    renderHomePage()
    const link = screen.getByRole('link', { name: /zobacz ofertę/i })
    expect(link).toHaveAttribute('href', '/products')
  })

  it('renders "Skontaktuj się" link to /contact', async () => {
    renderHomePage()
    const link = screen.getByRole('link', { name: /skontaktuj się/i })
    expect(link).toHaveAttribute('href', '/contact')
  })

  it('renders agency badge', () => {
    renderHomePage()
    expect(screen.getByText(/agencja kreatywna/i)).toBeInTheDocument()
  })
})

describe('HomePage — stats', () => {
  it('shows loading placeholders initially', () => {
    getProducts.mockReturnValue(new Promise(() => {}))
    getCategories.mockReturnValue(new Promise(() => {}))
    renderHomePage()
    expect(screen.getAllByText('…').length).toBeGreaterThanOrEqual(2)
  })

  it('shows product count from API after loading', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(screen.getByText('6')).toBeInTheDocument()
    })
  })

  it('shows category count from API after loading', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  it('shows static stat "5+"', async () => {
    renderHomePage()
    expect(screen.getByText('5+')).toBeInTheDocument()
  })

  it('shows static stat "100%"', async () => {
    renderHomePage()
    expect(screen.getByText('100%')).toBeInTheDocument()
  })
})

describe('HomePage — products section', () => {
  it('renders section heading "Nasze usługi"', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /nasze usługi/i })).toBeInTheDocument()
    })
  })

  it('renders up to 3 product cards', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(screen.getByText('Strona wizytówka')).toBeInTheDocument()
      expect(screen.getByText('Logo firmowe')).toBeInTheDocument()
      expect(screen.getByText('Kampania Google Ads')).toBeInTheDocument()
    })
  })

  it('product card shows category name', async () => {
    renderHomePage()
    await waitFor(() => {
      // 'Strony WWW' appears in both product badge and category link
      expect(screen.getAllByText('Strony WWW').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('product card shows price', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(screen.getByText(/1\s*500/)).toBeInTheDocument()
    })
  })

  it('product card links to correct URL', async () => {
    renderHomePage()
    await waitFor(() => {
      const link = screen.getByRole('link', { name: /strona wizytówka/i })
      expect(link).toHaveAttribute('href', '/products/strona-wizytowka')
    })
  })

  it('renders "Cała oferta" link to /products', async () => {
    renderHomePage()
    const link = screen.getByRole('link', { name: /cała oferta/i })
    expect(link).toHaveAttribute('href', '/products')
  })
})

describe('HomePage — categories section', () => {
  it('renders category links after loading', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(screen.getByRole('link', { name: 'Strony WWW' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Grafika' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Marketing' })).toBeInTheDocument()
    })
  })

  it('category link has correct href with slug', async () => {
    renderHomePage()
    await waitFor(() => {
      const link = screen.getByRole('link', { name: 'Grafika' })
      expect(link).toHaveAttribute('href', '/products?category=grafika')
    })
  })

  it('does not render categories section while loading', () => {
    getProducts.mockReturnValue(new Promise(() => {}))
    getCategories.mockReturnValue(new Promise(() => {}))
    renderHomePage()
    expect(screen.queryByRole('link', { name: 'Grafika' })).not.toBeInTheDocument()
  })
})

describe('HomePage — "Dlaczego Studio?" section', () => {
  it('renders why-us heading', async () => {
    renderHomePage()
    expect(screen.getByRole('heading', { name: /dlaczego studio/i })).toBeInTheDocument()
  })

  it('renders "Szybka realizacja" card', async () => {
    renderHomePage()
    expect(screen.getByText('Szybka realizacja')).toBeInTheDocument()
  })

  it('renders "Responsywność" card', async () => {
    renderHomePage()
    expect(screen.getByText('Responsywność')).toBeInTheDocument()
  })

  it('renders all 6 why-us cards', async () => {
    renderHomePage()
    const titles = [
      'Szybka realizacja', 'Nowoczesny design', 'Responsywność',
      'Bezpieczeństwo', 'SEO i wydajność', 'Wsparcie po wdrożeniu',
    ]
    titles.forEach((title) => {
      expect(screen.getByText(title)).toBeInTheDocument()
    })
  })
})

describe('HomePage — CTA section', () => {
  it('renders CTA heading', async () => {
    renderHomePage()
    expect(screen.getByRole('heading', { name: /gotowy na współpracę/i })).toBeInTheDocument()
  })

  it('CTA "Napisz do nas" links to /contact', async () => {
    renderHomePage()
    const links = screen.getAllByRole('link', { name: /napisz do nas/i })
    expect(links[0]).toHaveAttribute('href', '/contact')
  })

  it('CTA "Przeglądaj ofertę" links to /products', async () => {
    renderHomePage()
    const links = screen.getAllByRole('link', { name: /przeglądaj ofertę/i })
    expect(links[links.length - 1]).toHaveAttribute('href', '/products')
  })
})

describe('HomePage — API calls', () => {
  it('calls getProducts on mount', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(getProducts).toHaveBeenCalled()
    })
  })

  it('calls getCategories on mount', async () => {
    renderHomePage()
    await waitFor(() => {
      expect(getCategories).toHaveBeenCalled()
    })
  })

  it('handles empty products gracefully', async () => {
    getProducts.mockResolvedValue({ data: { count: 0, results: [] } })
    renderHomePage()
    await waitFor(() => {
      expect(screen.queryByText('Strona wizytówka')).not.toBeInTheDocument()
    })
    expect(screen.getByRole('heading', { name: /nasze usługi/i })).toBeInTheDocument()
  })

  it('handles empty categories gracefully', async () => {
    getCategories.mockResolvedValue({ data: { count: 0, results: [] } })
    renderHomePage()
    await waitFor(() => {
      expect(screen.queryByRole('link', { name: 'Grafika' })).not.toBeInTheDocument()
    })
  })
})
