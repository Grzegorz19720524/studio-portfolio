import api from './client'

export const sendMessage = (data) => api.post('/contact/', data)
