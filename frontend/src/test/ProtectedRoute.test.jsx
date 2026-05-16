import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ProtectedRoute from '../components/ProtectedRoute'

vi.mock('../store/authStore', () => ({ useAuthStore: vi.fn() }))

import { useAuthStore } from '../store/authStore'

const mockUser = { id: 1, username: 'jan' }

function renderProtected() {
  return render(
    <MemoryRouter>
      <ProtectedRoute>
        <p>Chroniona treść</p>
      </ProtectedRoute>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ProtectedRoute', () => {
  it('shows loading indicator while auth state is resolving', () => {
    useAuthStore.mockReturnValue({ user: null, loading: true })
    renderProtected()
    expect(screen.getByText(/ładowanie/i)).toBeInTheDocument()
  })

  it('does not render children while loading', () => {
    useAuthStore.mockReturnValue({ user: null, loading: true })
    renderProtected()
    expect(screen.queryByText('Chroniona treść')).not.toBeInTheDocument()
  })

  it('does not render children when user is not logged in', () => {
    useAuthStore.mockReturnValue({ user: null, loading: false })
    renderProtected()
    expect(screen.queryByText('Chroniona treść')).not.toBeInTheDocument()
  })

  it('renders children when user is logged in', () => {
    useAuthStore.mockReturnValue({ user: mockUser, loading: false })
    renderProtected()
    expect(screen.getByText('Chroniona treść')).toBeInTheDocument()
  })
})
