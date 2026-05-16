import api from './client'

export const getAdminUsers = () => api.get('/admin/users/')
export const updateAdminUser = (id, data) => api.patch(`/admin/users/${id}/`, data)

export const getAdminOrders = () => api.get('/orders/')
export const setOrderStatus = (id, status) => api.patch(`/orders/${id}/status/`, { status })

export const getContactMessages = () => api.get('/contact/')
export const markMessageRead = (id, is_read) => api.patch(`/contact/${id}/mark-read/`, { is_read })
export const deleteMessage = (id) => api.delete(`/contact/${id}/`)
