import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/client', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import api from '../api/client'
import { getCategories, getProducts, getProduct } from '../api/products'

const mockResponse = { data: { results: [] } }

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockResolvedValue(mockResponse)
})

describe('products.getCategories', () => {
  it('calls GET /categories/', async () => {
    await getCategories()
    expect(api.get).toHaveBeenCalledWith('/categories/')
  })

  it('returns the api response', async () => {
    const result = await getCategories()
    expect(result).toEqual(mockResponse)
  })
})

describe('products.getProducts', () => {
  it('calls GET /products/ with no params when called without argument', async () => {
    await getProducts()
    expect(api.get).toHaveBeenCalledWith('/products/', { params: undefined })
  })

  it('passes params object to the request', async () => {
    const params = { category: 'uslugi', ordering: 'price' }
    await getProducts(params)
    expect(api.get).toHaveBeenCalledWith('/products/', { params })
  })

  it('passes search param', async () => {
    const params = { search: 'strona' }
    await getProducts(params)
    expect(api.get).toHaveBeenCalledWith('/products/', { params })
  })

  it('returns the api response', async () => {
    const result = await getProducts({})
    expect(result).toEqual(mockResponse)
  })
})

describe('products.getProduct', () => {
  it('calls GET /products/:slug/', async () => {
    await getProduct('strona-www')
    expect(api.get).toHaveBeenCalledWith('/products/strona-www/')
  })

  it('interpolates slug correctly', async () => {
    await getProduct('logo-firmowe')
    expect(api.get).toHaveBeenCalledWith('/products/logo-firmowe/')
  })

  it('returns the api response', async () => {
    const result = await getProduct('test')
    expect(result).toEqual(mockResponse)
  })

  it('propagates rejection for missing product', async () => {
    api.get.mockRejectedValue(new Error('404'))
    await expect(getProduct('nie-istnieje')).rejects.toThrow('404')
  })
})
