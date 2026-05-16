import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import Navbar from '../components/Navbar'

vi.mock('../store/authStore', () => ({ useAuthStore: vi.fn() }))

const mockNavigate = vi.fn()
const mockLogout = vi.fn()

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

import { useAuthStore } from '../store/authStore'

const mockUser        = { username: 'jan',   is_staff: false }
const mockStaffUser   = { username: 'admin', is_staff: true  }

function renderNavbar() {
  return render(<MemoryRouter><Navbar /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  mockLogout.mockResolvedValue()
})

describe('Navbar — logged out', () => {
  beforeEach(() => {
    useAuthStore.mockReturnValue({ user: null, logout: mockLogout })
  })

  it('renders Studio logo link', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: /studio/i })).toHaveAttribute('href', '/')
  })

  it('renders Produkty and Kontakt links', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: /produkty/i })).toHaveAttribute('href', '/products')
    expect(screen.getByRole('link', { name: /kontakt/i })).toHaveAttribute('href', '/contact')
  })

  it('renders Logowanie and Rejestracja links', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: /logowanie/i })).toHaveAttribute('href', '/login')
    expect(screen.getByRole('link', { name: /rejestracja/i })).toHaveAttribute('href', '/register')
  })

  it('does not show Dashboard or Zamówienia links', () => {
    renderNavbar()
    expect(screen.queryByRole('link', { name: /dashboard/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /zamówienia/i })).not.toBeInTheDocument()
  })

  it('does not show Wyloguj button', () => {
    renderNavbar()
    expect(screen.queryByRole('button', { name: /wyloguj/i })).not.toBeInTheDocument()
  })

  it('does not show Admin link', () => {
    renderNavbar()
    expect(screen.queryByRole('link', { name: /admin/i })).not.toBeInTheDocument()
  })
})

describe('Navbar — logged in (regular user)', () => {
  beforeEach(() => {
    useAuthStore.mockReturnValue({ user: mockUser, logout: mockLogout })
  })

  it('renders Dashboard link', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: /dashboard/i })).toHaveAttribute('href', '/dashboard')
  })

  it('renders Zamówienia link', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: /zamówienia/i })).toHaveAttribute('href', '/orders')
  })

  it('renders username as link to /profile', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: 'jan' })).toHaveAttribute('href', '/profile')
  })

  it('renders Wyloguj button', () => {
    renderNavbar()
    expect(screen.getByRole('button', { name: /wyloguj/i })).toBeInTheDocument()
  })

  it('does not show Admin link for non-staff', () => {
    renderNavbar()
    expect(screen.queryByRole('link', { name: /^admin$/i })).not.toBeInTheDocument()
  })

  it('does not show Logowanie or Rejestracja', () => {
    renderNavbar()
    expect(screen.queryByRole('link', { name: /logowanie/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /rejestracja/i })).not.toBeInTheDocument()
  })
})

describe('Navbar — logged in (staff)', () => {
  beforeEach(() => {
    useAuthStore.mockReturnValue({ user: mockStaffUser, logout: mockLogout })
  })

  it('shows Admin link for staff user', () => {
    renderNavbar()
    expect(screen.getByRole('link', { name: 'Admin' })).toHaveAttribute('href', '/admin')
  })
})

describe('Navbar — logout', () => {
  beforeEach(() => {
    useAuthStore.mockReturnValue({ user: mockUser, logout: mockLogout })
  })

  it('calls logout on Wyloguj click', async () => {
    renderNavbar()
    await userEvent.click(screen.getByRole('button', { name: /wyloguj/i }))
    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled()
    })
  })

  it('navigates to /login after logout', async () => {
    renderNavbar()
    await userEvent.click(screen.getByRole('button', { name: /wyloguj/i }))
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })
  })
})
