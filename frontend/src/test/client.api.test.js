import { describe, it, expect, vi } from 'vitest'

const holder = vi.hoisted(() => ({ interceptorFn: null }))

vi.mock('axios', () => {
  const mockInstance = {
    interceptors: {
      request: {
        use: vi.fn((fn) => { holder.interceptorFn = fn }),
      },
    },
  }
  return { default: { create: vi.fn(() => mockInstance) } }
})

import axios from 'axios'
import client from '../api/client'

describe('api client — axios.create config', () => {
  it('creates instance with baseURL /api', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({ baseURL: '/api' })
    )
  })

  it('creates instance with withCredentials true', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({ withCredentials: true })
    )
  })

  it('creates instance with Content-Type application/json', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({ headers: { 'Content-Type': 'application/json' } })
    )
  })

  it('registers a request interceptor', () => {
    expect(client.interceptors.request.use).toHaveBeenCalledOnce()
  })
})

describe('api client — CSRF interceptor', () => {
  it('adds X-CSRFToken header when csrftoken cookie is present', () => {
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'sessionid=abc; csrftoken=tok123; other=val',
    })
    const config = { headers: {} }
    const result = holder.interceptorFn(config)
    expect(result.headers['X-CSRFToken']).toBe('tok123')
  })

  it('does not add X-CSRFToken when csrftoken cookie is absent', () => {
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'sessionid=abc',
    })
    const config = { headers: {} }
    const result = holder.interceptorFn(config)
    expect(result.headers['X-CSRFToken']).toBeUndefined()
  })

  it('does not add X-CSRFToken when cookie string is empty', () => {
    Object.defineProperty(document, 'cookie', { writable: true, value: '' })
    const config = { headers: {} }
    const result = holder.interceptorFn(config)
    expect(result.headers['X-CSRFToken']).toBeUndefined()
  })

  it('returns the config object unchanged (passthrough)', () => {
    Object.defineProperty(document, 'cookie', { writable: true, value: '' })
    const config = { headers: {}, url: '/test', method: 'get' }
    const result = holder.interceptorFn(config)
    expect(result.url).toBe('/test')
    expect(result.method).toBe('get')
  })
})
