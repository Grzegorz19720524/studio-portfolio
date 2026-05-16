import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/client', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import api from '../api/client'
import {
  getAdminUsers, updateAdminUser,
  getAdminOrders, setOrderStatus,
  getContactMessages, markMessageRead, deleteMessage,
  getAdminStats,
  getAdminProducts, getAdminCategories,
  createProduct, updateProduct, deleteProduct,
} from '../api/admin'

const mockResponse = { data: {} }

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockResolvedValue(mockResponse)
  api.post.mockResolvedValue(mockResponse)
  api.patch.mockResolvedValue(mockResponse)
  api.delete.mockResolvedValue(mockResponse)
})

describe('admin — users', () => {
  it('getAdminUsers calls GET /admin/users/', async () => {
    await getAdminUsers()
    expect(api.get).toHaveBeenCalledWith('/admin/users/')
  })

  it('updateAdminUser calls PATCH /admin/users/:id/ with data', async () => {
    const data = { is_active: false }
    await updateAdminUser(5, data)
    expect(api.patch).toHaveBeenCalledWith('/admin/users/5/', data)
  })

  it('updateAdminUser interpolates id correctly', async () => {
    await updateAdminUser(99, { is_staff: true })
    expect(api.patch).toHaveBeenCalledWith('/admin/users/99/', { is_staff: true })
  })
})

describe('admin — orders', () => {
  it('getAdminOrders calls GET /orders/', async () => {
    await getAdminOrders()
    expect(api.get).toHaveBeenCalledWith('/orders/')
  })

  it('setOrderStatus calls PATCH /orders/:id/status/ with status', async () => {
    await setOrderStatus(3, 'confirmed')
    expect(api.patch).toHaveBeenCalledWith('/orders/3/status/', { status: 'confirmed' })
  })

  it('setOrderStatus interpolates id and passes status', async () => {
    await setOrderStatus(12, 'completed')
    expect(api.patch).toHaveBeenCalledWith('/orders/12/status/', { status: 'completed' })
  })
})

describe('admin — messages', () => {
  it('getContactMessages calls GET /contact/', async () => {
    await getContactMessages()
    expect(api.get).toHaveBeenCalledWith('/contact/')
  })

  it('markMessageRead calls PATCH /contact/:id/mark-read/ with is_read true', async () => {
    await markMessageRead(7, true)
    expect(api.patch).toHaveBeenCalledWith('/contact/7/mark-read/', { is_read: true })
  })

  it('markMessageRead passes is_read false', async () => {
    await markMessageRead(7, false)
    expect(api.patch).toHaveBeenCalledWith('/contact/7/mark-read/', { is_read: false })
  })

  it('deleteMessage calls DELETE /contact/:id/', async () => {
    await deleteMessage(4)
    expect(api.delete).toHaveBeenCalledWith('/contact/4/')
  })

  it('deleteMessage interpolates id', async () => {
    await deleteMessage(99)
    expect(api.delete).toHaveBeenCalledWith('/contact/99/')
  })
})

describe('admin — stats', () => {
  it('getAdminStats calls GET /admin/stats/', async () => {
    await getAdminStats()
    expect(api.get).toHaveBeenCalledWith('/admin/stats/')
  })

  it('returns the api response', async () => {
    const result = await getAdminStats()
    expect(result).toEqual(mockResponse)
  })
})

describe('admin — products', () => {
  it('getAdminProducts calls GET /products/ with ordering and page_size params', async () => {
    await getAdminProducts()
    expect(api.get).toHaveBeenCalledWith('/products/', {
      params: { ordering: '-created_at', page_size: 100 },
    })
  })

  it('getAdminCategories calls GET /categories/', async () => {
    await getAdminCategories()
    expect(api.get).toHaveBeenCalledWith('/categories/')
  })

  it('createProduct calls POST /products/ with data', async () => {
    const data = { name: 'Logo', slug: 'logo', price: '500.00', category: 1 }
    await createProduct(data)
    expect(api.post).toHaveBeenCalledWith('/products/', data)
  })

  it('updateProduct calls PATCH /products/:slug/ with data', async () => {
    const data = { price: '800.00' }
    await updateProduct('logo', data)
    expect(api.patch).toHaveBeenCalledWith('/products/logo/', data)
  })

  it('updateProduct interpolates slug correctly', async () => {
    await updateProduct('strona-www', { is_active: false })
    expect(api.patch).toHaveBeenCalledWith('/products/strona-www/', { is_active: false })
  })

  it('deleteProduct calls DELETE /products/:slug/', async () => {
    await deleteProduct('logo')
    expect(api.delete).toHaveBeenCalledWith('/products/logo/')
  })

  it('deleteProduct interpolates slug', async () => {
    await deleteProduct('strona-www')
    expect(api.delete).toHaveBeenCalledWith('/products/strona-www/')
  })
})
