import api from './client'

export const getCategories = () => api.get('/categories/')
export const getProducts = (params) => api.get('/products/', { params })
export const getProduct = (slug) => api.get(`/products/${slug}/`)
