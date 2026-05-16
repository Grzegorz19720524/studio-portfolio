import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import RegisterPage from '../pages/RegisterPage'

vi.mock('../api/auth', () => ({
  register: vi.fn(),
}))

vi.mock('../store/authStore', () => ({
  useAuthStore: vi.fn(),
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

import { register } from '../api/auth'
import { useAuthStore } from '../store/authStore'

const mockLogin = vi.fn()

function renderRegister() {
  return render(<MemoryRouter><RegisterPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  useAuthStore.mockReturnValue({ login: mockLogin })
})

describe('RegisterPage — rendering', () => {
  it('renders heading', () => {
    renderRegister()
    expect(screen.getByRole('heading', { name: /rejestracja/i })).toBeInTheDocument()
  })

  it('renders all required fields', () => {
    renderRegister()
    expect(screen.getByLabelText(/nazwa użytkownika/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^hasło$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/powtórz hasło/i)).toBeInTheDocument()
  })

  it('renders optional fields', () => {
    renderRegister()
    expect(screen.getByLabelText(/telefon/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/firma/i)).toBeInTheDocument()
  })

  it('renders submit button', () => {
    renderRegister()
    expect(screen.getByRole('button', { name: /zarejestruj się/i })).toBeInTheDocument()
  })

  it('renders link to login page', () => {
    renderRegister()
    expect(screen.getByRole('link', { name: /zaloguj się/i })).toHaveAttribute('href', '/login')
  })
})

describe('RegisterPage — interactions', () => {
  it('calls register with form data', async () => {
    register.mockResolvedValue({ data: {} })
    mockLogin.mockResolvedValue()
    renderRegister()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'newuser')
    await userEvent.type(screen.getByLabelText(/^email$/i), 'new@test.pl')
    await userEvent.type(screen.getByLabelText(/^hasło$/i), 'Pass123!')
    await userEvent.type(screen.getByLabelText(/powtórz hasło/i), 'Pass123!')
    await userEvent.click(screen.getByRole('button', { name: /zarejestruj się/i }))
    await waitFor(() => {
      expect(register).toHaveBeenCalledWith(
        expect.objectContaining({ username: 'newuser', email: 'new@test.pl' })
      )
    })
  })

  it('logs in and navigates after successful registration', async () => {
    register.mockResolvedValue({ data: {} })
    mockLogin.mockResolvedValue()
    renderRegister()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'newuser')
    await userEvent.type(screen.getByLabelText(/^email$/i), 'new@test.pl')
    await userEvent.type(screen.getByLabelText(/^hasło$/i), 'Pass123!')
    await userEvent.type(screen.getByLabelText(/powtórz hasło/i), 'Pass123!')
    await userEvent.click(screen.getByRole('button', { name: /zarejestruj się/i }))
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled()
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('shows field error from API', async () => {
    register.mockRejectedValue({ response: { data: { username: ['Użytkownik o tej nazwie już istnieje.'] } } })
    renderRegister()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'existing')
    await userEvent.type(screen.getByLabelText(/^email$/i), 'x@x.pl')
    await userEvent.type(screen.getByLabelText(/^hasło$/i), 'Pass123!')
    await userEvent.type(screen.getByLabelText(/powtórz hasło/i), 'Pass123!')
    await userEvent.click(screen.getByRole('button', { name: /zarejestruj się/i }))
    await waitFor(() => {
      expect(screen.getByText(/użytkownik o tej nazwie już istnieje/i)).toBeInTheDocument()
    })
  })

  it('disables button while loading', async () => {
    register.mockReturnValue(new Promise(() => {}))
    renderRegister()
    await userEvent.type(screen.getByLabelText(/nazwa użytkownika/i), 'u')
    await userEvent.type(screen.getByLabelText(/^email$/i), 'u@u.pl')
    await userEvent.type(screen.getByLabelText(/^hasło$/i), 'P123!')
    await userEvent.type(screen.getByLabelText(/powtórz hasło/i), 'P123!')
    await userEvent.click(screen.getByRole('button', { name: /zarejestruj się/i }))
    expect(screen.getByRole('button', { name: /rejestracja/i })).toBeDisabled()
  })
})
