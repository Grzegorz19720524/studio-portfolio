import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/client', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import api from '../api/client'
import { register, login, logout, getMe, updateMe, changePassword } from '../api/auth'

const mockResponse = { data: { id: 1, username: 'jan' } }

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockResolvedValue(mockResponse)
  api.post.mockResolvedValue(mockResponse)
  api.patch.mockResolvedValue(mockResponse)
})

describe('auth.register', () => {
  it('calls POST /auth/register/ with data', async () => {
    const data = { username: 'jan', password: 'Pass1!', password2: 'Pass1!' }
    await register(data)
    expect(api.post).toHaveBeenCalledWith('/auth/register/', data)
  })

  it('returns the api response', async () => {
    api.post.mockResolvedValue(mockResponse)
    const result = await register({})
    expect(result).toEqual(mockResponse)
  })
})

describe('auth.login', () => {
  it('calls POST /auth/login/ with credentials', async () => {
    const data = { username: 'jan', password: 'Pass1!' }
    await login(data)
    expect(api.post).toHaveBeenCalledWith('/auth/login/', data)
  })

  it('propagates rejection on failed login', async () => {
    api.post.mockRejectedValue(new Error('401'))
    await expect(login({})).rejects.toThrow('401')
  })
})

describe('auth.logout', () => {
  it('calls POST /auth/logout/ with no body', async () => {
    await logout()
    expect(api.post).toHaveBeenCalledWith('/auth/logout/')
  })

  it('calls post exactly once', async () => {
    await logout()
    expect(api.post).toHaveBeenCalledOnce()
  })
})

describe('auth.getMe', () => {
  it('calls GET /auth/me/', async () => {
    await getMe()
    expect(api.get).toHaveBeenCalledWith('/auth/me/')
  })

  it('returns the api response', async () => {
    const result = await getMe()
    expect(result).toEqual(mockResponse)
  })
})

describe('auth.updateMe', () => {
  it('calls PATCH /auth/me/ with data', async () => {
    const data = { phone: '123456789' }
    await updateMe(data)
    expect(api.patch).toHaveBeenCalledWith('/auth/me/', data)
  })

  it('passes full update payload', async () => {
    const data = { first_name: 'Jan', last_name: 'Kowalski', email: 'jan@test.pl' }
    await updateMe(data)
    expect(api.patch).toHaveBeenCalledWith('/auth/me/', data)
  })
})

describe('auth.changePassword', () => {
  it('calls POST /auth/change-password/ with data', async () => {
    const data = { old_password: 'old', new_password: 'New1!', new_password2: 'New1!' }
    await changePassword(data)
    expect(api.post).toHaveBeenCalledWith('/auth/change-password/', data)
  })

  it('propagates rejection on error', async () => {
    api.post.mockRejectedValue(new Error('400'))
    await expect(changePassword({})).rejects.toThrow('400')
  })
})
