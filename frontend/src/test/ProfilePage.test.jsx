import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import ProfilePage from '../pages/ProfilePage'

vi.mock('../api/auth', () => ({
  updateMe: vi.fn(),
  changePassword: vi.fn(),
}))

vi.mock('../store/authStore', () => ({
  useAuthStore: vi.fn(),
}))

import { updateMe, changePassword } from '../api/auth'
import { useAuthStore } from '../store/authStore'

const mockUser = {
  id: 1,
  username: 'jan',
  email: 'jan@test.pl',
  first_name: 'Jan',
  last_name: 'Kowalski',
  phone: '123456789',
  company: 'Firma X',
}

const mockSetUser = vi.fn()

function renderProfile() {
  return render(<MemoryRouter><ProfilePage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
  useAuthStore.mockReturnValue({ user: mockUser, setUser: mockSetUser })
})

describe('ProfilePage — rendering', () => {
  it('renders "Profil" heading', () => {
    renderProfile()
    expect(screen.getByRole('heading', { name: /profil/i })).toBeInTheDocument()
  })

  it('shows current username', () => {
    renderProfile()
    expect(screen.getByText('jan')).toBeInTheDocument()
  })

  it('renders all profile form fields', () => {
    renderProfile()
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^imię$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^nazwisko$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^telefon$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^firma$/i)).toBeInTheDocument()
  })

  it('pre-fills profile fields with user data', () => {
    renderProfile()
    expect(screen.getByLabelText(/^email$/i)).toHaveValue('jan@test.pl')
    expect(screen.getByLabelText(/^imię$/i)).toHaveValue('Jan')
    expect(screen.getByLabelText(/^nazwisko$/i)).toHaveValue('Kowalski')
  })

  it('renders "Zapisz" button', () => {
    renderProfile()
    expect(screen.getByRole('button', { name: /zapisz/i })).toBeInTheDocument()
  })

  it('renders "Zmiana hasła" section heading', () => {
    renderProfile()
    expect(screen.getByRole('heading', { name: /zmiana hasła/i })).toBeInTheDocument()
  })

  it('renders all password form fields', () => {
    renderProfile()
    expect(screen.getByLabelText(/stare hasło/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^nowe hasło$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/powtórz nowe hasło/i)).toBeInTheDocument()
  })

  it('renders "Zmień hasło" button', () => {
    renderProfile()
    expect(screen.getByRole('button', { name: /zmień hasło/i })).toBeInTheDocument()
  })
})

describe('ProfilePage — profile form', () => {
  it('calls updateMe with updated form data on submit', async () => {
    updateMe.mockResolvedValue({ data: mockUser })
    renderProfile()
    await userEvent.clear(screen.getByLabelText(/^email$/i))
    await userEvent.type(screen.getByLabelText(/^email$/i), 'nowy@test.pl')
    await userEvent.click(screen.getByRole('button', { name: /zapisz/i }))
    await waitFor(() => {
      expect(updateMe).toHaveBeenCalledWith(
        expect.objectContaining({ email: 'nowy@test.pl' })
      )
    })
  })

  it('calls setUser with response data on success', async () => {
    const updated = { ...mockUser, email: 'nowy@test.pl' }
    updateMe.mockResolvedValue({ data: updated })
    renderProfile()
    await userEvent.click(screen.getByRole('button', { name: /zapisz/i }))
    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalledWith(updated)
    })
  })

  it('shows success message after saving profile', async () => {
    updateMe.mockResolvedValue({ data: mockUser })
    renderProfile()
    await userEvent.click(screen.getByRole('button', { name: /zapisz/i }))
    await waitFor(() => {
      expect(screen.getByText(/profil zaktualizowany/i)).toBeInTheDocument()
    })
  })

  it('shows field error from API on failure', async () => {
    updateMe.mockRejectedValue({ response: { data: { email: ['Ten adres email jest już zajęty.'] } } })
    renderProfile()
    await userEvent.click(screen.getByRole('button', { name: /zapisz/i }))
    await waitFor(() => {
      expect(screen.getByText(/ten adres email jest już zajęty/i)).toBeInTheDocument()
    })
  })
})

describe('ProfilePage — password form', () => {
  async function fillPasswordForm() {
    await userEvent.type(screen.getByLabelText(/stare hasło/i), 'OldPass1!')
    await userEvent.type(screen.getByLabelText(/^nowe hasło$/i), 'NewPass1!')
    await userEvent.type(screen.getByLabelText(/powtórz nowe hasło/i), 'NewPass1!')
  }

  it('calls changePassword with form data on submit', async () => {
    changePassword.mockResolvedValue({ data: {} })
    renderProfile()
    await fillPasswordForm()
    await userEvent.click(screen.getByRole('button', { name: /zmień hasło/i }))
    await waitFor(() => {
      expect(changePassword).toHaveBeenCalledWith({
        old_password: 'OldPass1!',
        new_password: 'NewPass1!',
        new_password2: 'NewPass1!',
      })
    })
  })

  it('shows success message after changing password', async () => {
    changePassword.mockResolvedValue({ data: {} })
    renderProfile()
    await fillPasswordForm()
    await userEvent.click(screen.getByRole('button', { name: /zmień hasło/i }))
    await waitFor(() => {
      expect(screen.getByText(/hasło zostało zmienione/i)).toBeInTheDocument()
    })
  })

  it('clears password fields after success', async () => {
    changePassword.mockResolvedValue({ data: {} })
    renderProfile()
    await fillPasswordForm()
    await userEvent.click(screen.getByRole('button', { name: /zmień hasło/i }))
    await waitFor(() => {
      expect(screen.getByLabelText(/stare hasło/i)).toHaveValue('')
      expect(screen.getByLabelText(/^nowe hasło$/i)).toHaveValue('')
    })
  })

  it('shows field error from API on failure', async () => {
    changePassword.mockRejectedValue({
      response: { data: { old_password: ['Nieprawidłowe hasło.'] } },
    })
    renderProfile()
    await fillPasswordForm()
    await userEvent.click(screen.getByRole('button', { name: /zmień hasło/i }))
    await waitFor(() => {
      expect(screen.getByText(/nieprawidłowe hasło/i)).toBeInTheDocument()
    })
  })
})
