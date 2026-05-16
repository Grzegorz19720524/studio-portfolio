import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/client', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import api from '../api/client'
import { getOrders, getOrder, createOrder } from '../api/orders'

const mockResponse = { data: {} }

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockResolvedValue(mockResponse)
  api.post.mockResolvedValue(mockResponse)
})

describe('orders.getOrders', () => {
  it('calls GET /orders/', async () => {
    await getOrders()
    expect(api.get).toHaveBeenCalledWith('/orders/')
  })

  it('returns the api response', async () => {
    const result = await getOrders()
    expect(result).toEqual(mockResponse)
  })
})

describe('orders.getOrder', () => {
  it('calls GET /orders/:id/', async () => {
    await getOrder(42)
    expect(api.get).toHaveBeenCalledWith('/orders/42/')
  })

  it('interpolates id correctly', async () => {
    await getOrder(7)
    expect(api.get).toHaveBeenCalledWith('/orders/7/')
  })

  it('returns the api response', async () => {
    const result = await getOrder(1)
    expect(result).toEqual(mockResponse)
  })

  it('propagates rejection for missing order', async () => {
    api.get.mockRejectedValue(new Error('404'))
    await expect(getOrder(99999)).rejects.toThrow('404')
  })
})

describe('orders.createOrder', () => {
  it('calls POST /orders/ with data', async () => {
    const data = { items: [{ product: 1, quantity: 2 }] }
    await createOrder(data)
    expect(api.post).toHaveBeenCalledWith('/orders/', data)
  })

  it('passes multi-item payload correctly', async () => {
    const data = { items: [{ product: 1, quantity: 1 }, { product: 2, quantity: 3 }] }
    await createOrder(data)
    expect(api.post).toHaveBeenCalledWith('/orders/', data)
  })

  it('returns the api response', async () => {
    const result = await createOrder({})
    expect(result).toEqual(mockResponse)
  })

  it('propagates rejection on validation error', async () => {
    api.post.mockRejectedValue(new Error('400'))
    await expect(createOrder({ items: [] })).rejects.toThrow('400')
  })
})
