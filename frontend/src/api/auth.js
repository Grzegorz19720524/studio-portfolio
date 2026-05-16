import api from './client'

export const register = (data) => api.post('/auth/register/', data)
export const login = (data) => api.post('/auth/login/', data)
export const logout = () => api.post('/auth/logout/')
export const getMe = () => api.get('/auth/me/')
export const updateMe = (data) => api.patch('/auth/me/', data)
export const changePassword = (data) => api.post('/auth/change-password/', data)
