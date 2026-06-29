import api from '../index'

export const getDashboardStats = (params) => api.get('/dashboard/stats', { params })
