import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/client', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import api from '../api/client'
import { sendMessage } from '../api/contact'

const mockResponse = { data: { detail: 'Wiadomość została wysłana.' } }

beforeEach(() => {
  vi.clearAllMocks()
  api.post.mockResolvedValue(mockResponse)
})

describe('contact.sendMessage', () => {
  it('calls POST /contact/ with data', async () => {
    const data = { name: 'Jan', email: 'jan@test.pl', subject: 'Zapytanie', message: 'Treść.' }
    await sendMessage(data)
    expect(api.post).toHaveBeenCalledWith('/contact/', data)
  })

  it('returns the api response', async () => {
    const result = await sendMessage({})
    expect(result).toEqual(mockResponse)
  })

  it('propagates rejection on validation error', async () => {
    api.post.mockRejectedValue(new Error('400'))
    await expect(sendMessage({})).rejects.toThrow('400')
  })

  it('calls post exactly once per call', async () => {
    await sendMessage({ name: 'A', email: 'a@a.pl', subject: 'S', message: 'M' })
    expect(api.post).toHaveBeenCalledOnce()
  })
})
