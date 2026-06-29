import axios from '../index'

export const getInvoices = (params) => axios.get('/invoices', { params })
export const getInvoice = (id) => axios.get(`/invoices/${id}`)
export const createInvoice = (data) => axios.post('/invoices', data)
export const updateInvoice = (id, data) => axios.put(`/invoices/${id}`, data)
export const deleteInvoice = (id) => axios.delete(`/invoices/${id}`)
