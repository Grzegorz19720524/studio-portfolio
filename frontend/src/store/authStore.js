import { create } from 'zustand'
import { getMe, login as apiLogin, logout as apiLogout } from '../api/auth'

export const useAuthStore = create((set) => ({
  user: null,
  loading: true,

  init: async () => {
    try {
      const { data } = await getMe()
      set({ user: data, loading: false })
    } catch {
      set({ user: null, loading: false })
    }
  },

  login: async (credentials) => {
    const { data } = await apiLogin(credentials)
    set({ user: data })
  },

  logout: async () => {
    await apiLogout()
    set({ user: null })
  },

  setUser: (user) => set({ user }),
}))
