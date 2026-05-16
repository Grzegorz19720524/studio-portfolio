import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AdminRoute from '../components/AdminRoute'

vi.mock('../store/authStore', () => ({ useAuthStore: vi.fn() }))

import { useAuthStore } from '../store/authStore'

const mockUser      = { id: 1, username: 'jan',   is_staff: false }
const mockStaffUser = { id: 2, username: 'admin', is_staff: true  }

function renderAdminRoute() {
  return render(
    <MemoryRouter>
      <AdminRoute>
        <p>Admin treść</p>
      </AdminRoute>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('AdminRoute', () => {
  it('renders nothing while auth state is loading', () => {
    useAuthStore.mockReturnValue({ user: null, loading: true })
    const { container } = renderAdminRoute()
    expect(container.firstChild).toBeNull()
  })

  it('does not render children while loading', () => {
    useAuthStore.mockReturnValue({ user: null, loading: true })
    renderAdminRoute()
    expect(screen.queryByText('Admin treść')).not.toBeInTheDocument()
  })

  it('does not render children when user is not logged in', () => {
    useAuthStore.mockReturnValue({ user: null, loading: false })
    renderAdminRoute()
    expect(screen.queryByText('Admin treść')).not.toBeInTheDocument()
  })

  it('does not render children when user is not staff', () => {
    useAuthStore.mockReturnValue({ user: mockUser, loading: false })
    renderAdminRoute()
    expect(screen.queryByText('Admin treść')).not.toBeInTheDocument()
  })

  it('renders children when user is staff', () => {
    useAuthStore.mockReturnValue({ user: mockStaffUser, loading: false })
    renderAdminRoute()
    expect(screen.getByText('Admin treść')).toBeInTheDocument()
  })
})
