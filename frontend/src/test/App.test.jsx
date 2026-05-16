import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('../store/authStore', () => ({ useAuthStore: vi.fn() }))
vi.mock('../components/Navbar', () => ({ default: () => <nav data-testid="navbar" /> }))
vi.mock('../components/ProtectedRoute', () => ({ default: ({ children }) => <>{children}</> }))
vi.mock('../components/AdminRoute',     () => ({ default: ({ children }) => <>{children}</> }))

vi.mock('../pages/HomePage',         () => ({ default: () => <p>mock-home</p> }))
vi.mock('../pages/LoginPage',        () => ({ default: () => <p>mock-login</p> }))
vi.mock('../pages/RegisterPage',     () => ({ default: () => <p>mock-register</p> }))
vi.mock('../pages/ProductsPage',     () => ({ default: () => <p>mock-products</p> }))
vi.mock('../pages/ProductDetailPage',() => ({ default: () => <p>mock-product-detail</p> }))
vi.mock('../pages/OrdersPage',       () => ({ default: () => <p>mock-orders</p> }))
vi.mock('../pages/OrderDetailPage',  () => ({ default: () => <p>mock-order-detail</p> }))
vi.mock('../pages/ContactPage',      () => ({ default: () => <p>mock-contact</p> }))
vi.mock('../pages/ProfilePage',      () => ({ default: () => <p>mock-profile</p> }))
vi.mock('../pages/DashboardPage',    () => ({ default: () => <p>mock-dashboard</p> }))
vi.mock('../pages/AdminPage',        () => ({ default: () => <p>mock-admin</p> }))

import { useAuthStore } from '../store/authStore'
import App from '../App'

const mockInit = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  mockInit.mockResolvedValue()
  useAuthStore.mockReturnValue({ init: mockInit })
})

afterEach(() => {
  window.history.pushState(null, '', '/')
})

function navigate(path) {
  window.history.pushState(null, '', path)
}

describe('App — inicjalizacja', () => {
  it('wywołuje init() przy montowaniu', () => {
    render(<App />)
    expect(mockInit).toHaveBeenCalledOnce()
  })

  it('wywołuje init() dokładnie raz', () => {
    render(<App />)
    expect(mockInit).toHaveBeenCalledTimes(1)
  })
})

describe('App — stały layout', () => {
  it('renderuje Navbar', () => {
    render(<App />)
    expect(screen.getByTestId('navbar')).toBeInTheDocument()
  })

  it('renderuje footer z aktualnym rokiem', () => {
    render(<App />)
    const year = new Date().getFullYear().toString()
    expect(screen.getByText(new RegExp(year))).toBeInTheDocument()
  })

  it('footer zawiera tekst o prawach autorskich', () => {
    render(<App />)
    expect(screen.getByText(/Wszelkie prawa zastrzeżone/)).toBeInTheDocument()
  })

  it('footer zawiera nazwę Studio', () => {
    render(<App />)
    expect(screen.getByText(/Studio/)).toBeInTheDocument()
  })
})

describe('App — routing — strony publiczne', () => {
  it('renderuje HomePage na /', () => {
    navigate('/')
    render(<App />)
    expect(screen.getByText('mock-home')).toBeInTheDocument()
  })

  it('renderuje LoginPage na /login', () => {
    navigate('/login')
    render(<App />)
    expect(screen.getByText('mock-login')).toBeInTheDocument()
  })

  it('renderuje RegisterPage na /register', () => {
    navigate('/register')
    render(<App />)
    expect(screen.getByText('mock-register')).toBeInTheDocument()
  })

  it('renderuje ProductsPage na /products', () => {
    navigate('/products')
    render(<App />)
    expect(screen.getByText('mock-products')).toBeInTheDocument()
  })

  it('renderuje ProductDetailPage na /products/:slug', () => {
    navigate('/products/strona-www')
    render(<App />)
    expect(screen.getByText('mock-product-detail')).toBeInTheDocument()
  })

  it('renderuje ContactPage na /contact', () => {
    navigate('/contact')
    render(<App />)
    expect(screen.getByText('mock-contact')).toBeInTheDocument()
  })
})

describe('App — routing — strony chronione (ProtectedRoute)', () => {
  it('renderuje OrdersPage na /orders', () => {
    navigate('/orders')
    render(<App />)
    expect(screen.getByText('mock-orders')).toBeInTheDocument()
  })

  it('renderuje OrderDetailPage na /orders/:id', () => {
    navigate('/orders/1')
    render(<App />)
    expect(screen.getByText('mock-order-detail')).toBeInTheDocument()
  })

  it('renderuje DashboardPage na /dashboard', () => {
    navigate('/dashboard')
    render(<App />)
    expect(screen.getByText('mock-dashboard')).toBeInTheDocument()
  })

  it('renderuje ProfilePage na /profile', () => {
    navigate('/profile')
    render(<App />)
    expect(screen.getByText('mock-profile')).toBeInTheDocument()
  })
})

describe('App — routing — panel admina (AdminRoute)', () => {
  it('renderuje AdminPage na /admin', () => {
    navigate('/admin')
    render(<App />)
    expect(screen.getByText('mock-admin')).toBeInTheDocument()
  })
})

describe('App — routing — izolacja tras', () => {
  it('nie renderuje LoginPage na /', () => {
    navigate('/')
    render(<App />)
    expect(screen.queryByText('mock-login')).not.toBeInTheDocument()
  })

  it('nie renderuje HomePage na /login', () => {
    navigate('/login')
    render(<App />)
    expect(screen.queryByText('mock-home')).not.toBeInTheDocument()
  })

  it('nie renderuje AdminPage na /products', () => {
    navigate('/products')
    render(<App />)
    expect(screen.queryByText('mock-admin')).not.toBeInTheDocument()
  })
})
