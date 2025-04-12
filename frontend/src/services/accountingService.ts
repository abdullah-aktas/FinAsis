import axios from 'axios';
import { API_BASE_URL } from '../config';

// Muhasebe modülü API servisleri
const accountingService = {
  // Faturalar
  getInvoices: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/invoices/`);
    return response.data;
  },
  getInvoice: async (invoiceId: number) => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/invoices/${invoiceId}/`);
    return response.data;
  },
  createInvoice: async (invoiceData: any) => {
    const response = await axios.post(`${API_BASE_URL}/api/accounting/invoices/`, invoiceData);
    return response.data;
  },
  updateInvoice: async (invoiceId: number, invoiceData: any) => {
    const response = await axios.put(`${API_BASE_URL}/api/accounting/invoices/${invoiceId}/`, invoiceData);
    return response.data;
  },
  deleteInvoice: async (invoiceId: number) => {
    const response = await axios.delete(`${API_BASE_URL}/api/accounting/invoices/${invoiceId}/`);
    return response.data;
  },
  
  // Hesap planı
  getChartOfAccounts: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/chart-of-accounts/`);
    return response.data;
  },
  getAccount: (id: number) => axios.get(`${API_BASE_URL}/api/accounting/chart-of-accounts/${id}/`),
  createAccount: async (accountData: any) => {
    const response = await axios.post(`${API_BASE_URL}/api/accounting/accounts/`, accountData);
    return response.data;
  },
  updateAccount: async (accountId: number, accountData: any) => {
    const response = await axios.put(`${API_BASE_URL}/api/accounting/accounts/${accountId}/`, accountData);
    return response.data;
  },
  deleteAccount: async (accountId: number) => {
    const response = await axios.delete(`${API_BASE_URL}/api/accounting/accounts/${accountId}/`);
    return response.data;
  },
  
  // İşlemler
  getTransactions: () => axios.get(`${API_BASE_URL}/api/accounting/transactions/`),
  getTransaction: (id: number) => axios.get(`${API_BASE_URL}/api/accounting/transactions/${id}/`),
  createTransaction: (data: any) => axios.post(`${API_BASE_URL}/api/accounting/transactions/`, data),
  updateTransaction: (id: number, data: any) => axios.put(`${API_BASE_URL}/api/accounting/transactions/${id}/`, data),
  deleteTransaction: (id: number) => axios.delete(`${API_BASE_URL}/api/accounting/transactions/${id}/`),
  
  // Kasa
  getCashBoxes: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/cash-boxes/`);
    return response.data;
  },
  getCashBox: async (cashBoxId: number) => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/cash-boxes/${cashBoxId}/`);
    return response.data;
  },
  createCashBox: async (cashBoxData: any) => {
    const response = await axios.post(`${API_BASE_URL}/api/accounting/cash-boxes/`, cashBoxData);
    return response.data;
  },
  updateCashBox: async (cashBoxId: number, cashBoxData: any) => {
    const response = await axios.put(`${API_BASE_URL}/api/accounting/cash-boxes/${cashBoxId}/`, cashBoxData);
    return response.data;
  },
  deleteCashBox: async (cashBoxId: number) => {
    const response = await axios.delete(`${API_BASE_URL}/api/accounting/cash-boxes/${cashBoxId}/`);
    return response.data;
  },
  
  // Raporlar
  getFinancialReports: () => axios.get(`${API_BASE_URL}/api/accounting/reports/financial/`),
  getTaxReports: () => axios.get(`${API_BASE_URL}/api/accounting/reports/tax/`),
  getBalanceSheet: async (date: string) => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/reports/balance-sheet/?date=${date}`);
    return response.data;
  },
  getIncomeStatement: async (startDate: string, endDate: string) => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/reports/income-statement/?start_date=${startDate}&end_date=${endDate}`);
    return response.data;
  },
  getTrialBalance: async (date: string) => {
    const response = await axios.get(`${API_BASE_URL}/api/accounting/reports/trial-balance/?date=${date}`);
    return response.data;
  },
};

export default accountingService; 