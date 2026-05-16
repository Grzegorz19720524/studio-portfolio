import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import LoginPage from '../pages/LoginPage'

vi.mock('../store/authStore', () => ({
  useAuthStore: vi.fn(),
}))

import { useAuthStore } from '../store/authStore'

const mockLogin = vi.fn()
const mockNavigate = vi.fn()

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

function renderLogin() {
  return render(<MemoryRouter><LoginPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  useAuthStore.mockReturnValue({ login: mockLogin })
})

describe('LoginPage — rendering', () => {
  it('renders heading', () => {
    renderLogin()
    expect(screen.getByRole('heading', { name: /logowanie/i })).toBeInTheDocument()
  })

  it('renders username input', () => {
    renderLogin()
    expect(screen.getByLabelText(/nazwa użytkownika/i)).toBeInTheDocument()
  })

  it('renders password input', () => {
    renderLogin()
    expect(screen.getByLabelText(/hasło/i)).toBeInTheDocument()
  })

  it('renders submit button', () => {
    renderLogin()
    expect(screen.getByRole('button', { name: /zaloguj się/i })).toBeInTheDocument()
  })

  it('renders link to register page', () => {
    renderLogin()
    expect(screen.getByRole('link', { name: /zarejestruj się/i })).toHaveAttribute('href', '/register')
  })
})

describe('LoginPage — interactions', () => {
  it('calls login with entered credentials', async () => {
    mockLogin.mockResolvedValue()
    renderLogin()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'jan')
    await userEvent.type(screen.getByLabelText(/hasło/i), 'User123!')
    await userEvent.click(screen.getByRole('button', { name: /zaloguj się/i }))
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({ username: 'jan', password: 'User123!' })
    })
  })

  it('navigates to / after successful login', async () => {
    mockLogin.mockResolvedValue()
    renderLogin()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'jan')
    await userEvent.type(screen.getByLabelText(/hasło/i), 'User123!')
    await userEvent.click(screen.getByRole('button', { name: /zaloguj się/i }))
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('shows error message on failed login', async () => {
    mockLogin.mockRejectedValue({ response: { data: { detail: 'Nieprawidłowe dane logowania.' } } })
    renderLogin()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'jan')
    await userEvent.type(screen.getByLabelText(/hasło/i), 'wrong')
    await userEvent.click(screen.getByRole('button', { name: /zaloguj się/i }))
    await waitFor(() => {
      expect(screen.getByText('Nieprawidłowe dane logowania.')).toBeInTheDocument()
    })
  })

  it('shows fallback error message when detail missing', async () => {
    mockLogin.mockRejectedValue({ response: { data: {} } })
    renderLogin()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'jan')
    await userEvent.type(screen.getByLabelText(/hasło/i), 'wrong')
    await userEvent.click(screen.getByRole('button', { name: /zaloguj się/i }))
    await waitFor(() => {
      expect(screen.getByText(/błąd logowania/i)).toBeInTheDocument()
    })
  })

  it('disables button while loading', async () => {
    mockLogin.mockReturnValue(new Promise(() => {}))
    renderLogin()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'jan')
    await userEvent.type(screen.getByLabelText(/hasło/i), 'User123!')
    await userEvent.click(screen.getByRole('button', { name: /zaloguj się/i }))
    expect(screen.getByRole('button', { name: /logowanie/i })).toBeDisabled()
  })
})
