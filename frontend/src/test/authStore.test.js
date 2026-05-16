import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/auth', () => ({
  getMe: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
}))

import { useAuthStore } from '../store/authStore'
import { getMe, login, logout } from '../api/auth'

const mockUser = { id: 1, username: 'jan', email: 'jan@test.pl' }

beforeEach(() => {
  vi.clearAllMocks()
  useAuthStore.setState({ user: null, loading: true })
})

describe('authStore — initial state', () => {
  it('user is null by default', () => {
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('loading is true by default', () => {
    expect(useAuthStore.getState().loading).toBe(true)
  })
})

describe('authStore — init()', () => {
  it('calls getMe', async () => {
    getMe.mockResolvedValue({ data: mockUser })
    await useAuthStore.getState().init()
    expect(getMe).toHaveBeenCalledOnce()
  })

  it('sets user and loading=false on success', async () => {
    getMe.mockResolvedValue({ data: mockUser })
    await useAuthStore.getState().init()
    expect(useAuthStore.getState().user).toEqual(mockUser)
    expect(useAuthStore.getState().loading).toBe(false)
  })

  it('sets user=null and loading=false on failure', async () => {
    getMe.mockRejectedValue(new Error('Unauthorized'))
    await useAuthStore.getState().init()
    expect(useAuthStore.getState().user).toBeNull()
    expect(useAuthStore.getState().loading).toBe(false)
  })
})

describe('authStore — login()', () => {
  it('calls apiLogin with provided credentials', async () => {
    login.mockResolvedValue({ data: mockUser })
    await useAuthStore.getState().login({ username: 'jan', password: 'Pass1!' })
    expect(login).toHaveBeenCalledWith({ username: 'jan', password: 'Pass1!' })
  })

  it('sets user after successful login', async () => {
    login.mockResolvedValue({ data: mockUser })
    await useAuthStore.getState().login({ username: 'jan', password: 'Pass1!' })
    expect(useAuthStore.getState().user).toEqual(mockUser)
  })

  it('does not change loading flag on login', async () => {
    login.mockResolvedValue({ data: mockUser })
    useAuthStore.setState({ loading: false })
    await useAuthStore.getState().login({ username: 'jan', password: 'Pass1!' })
    expect(useAuthStore.getState().loading).toBe(false)
  })

  it('propagates error on failed login', async () => {
    login.mockRejectedValue(new Error('Invalid credentials'))
    await expect(
      useAuthStore.getState().login({ username: 'jan', password: 'wrong' })
    ).rejects.toThrow('Invalid credentials')
  })

  it('does not set user on failed login', async () => {
    login.mockRejectedValue(new Error('Invalid credentials'))
    try { await useAuthStore.getState().login({ username: 'jan', password: 'wrong' }) } catch {}
    expect(useAuthStore.getState().user).toBeNull()
  })
})

describe('authStore — logout()', () => {
  it('calls apiLogout', async () => {
    logout.mockResolvedValue()
    await useAuthStore.getState().logout()
    expect(logout).toHaveBeenCalledOnce()
  })

  it('sets user to null after logout', async () => {
    logout.mockResolvedValue()
    useAuthStore.setState({ user: mockUser })
    await useAuthStore.getState().logout()
    expect(useAuthStore.getState().user).toBeNull()
  })
})

describe('authStore — setUser()', () => {
  it('sets user directly', () => {
    useAuthStore.getState().setUser(mockUser)
    expect(useAuthStore.getState().user).toEqual(mockUser)
  })

  it('can clear user by setting null', () => {
    useAuthStore.setState({ user: mockUser })
    useAuthStore.getState().setUser(null)
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('replaces user with updated data', () => {
    useAuthStore.setState({ user: mockUser })
    const updated = { ...mockUser, email: 'nowy@test.pl' }
    useAuthStore.getState().setUser(updated)
    expect(useAuthStore.getState().user).toEqual(updated)
  })
})
