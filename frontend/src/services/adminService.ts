import axios from 'axios';
import { API_BASE_URL } from '../config';

// Kullanıcı yönetimi
export const getUsers = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/admin/users/`);
  return response.data;
};

export const createUser = async (userData: any) => {
  const response = await axios.post(`${API_BASE_URL}/api/admin/users/`, userData);
  return response.data;
};

export const updateUser = async (userId: number, userData: any) => {
  const response = await axios.put(`${API_BASE_URL}/api/admin/users/${userId}/`, userData);
  return response.data;
};

export const deleteUser = async (userId: number) => {
  const response = await axios.delete(`${API_BASE_URL}/api/admin/users/${userId}/`);
  return response.data;
};

// Sistem ayarları
export const getSystemSettings = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/admin/settings/`);
  return response.data;
};

export const updateSystemSettings = async (settings: any) => {
  const response = await axios.put(`${API_BASE_URL}/api/admin/settings/`, settings);
  return response.data;
};

// Bakım işlemleri
export const backupDatabase = async () => {
  const response = await axios.post(`${API_BASE_URL}/api/admin/backup/`);
  return response.data;
};

export const clearCache = async () => {
  const response = await axios.post(`${API_BASE_URL}/api/admin/clear-cache/`);
  return response.data;
};

// E-posta ayarları
export const getEmailSettings = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/admin/email-settings/`);
  return response.data;
};

export const updateEmailSettings = async (settings: any) => {
  const response = await axios.put(`${API_BASE_URL}/api/admin/email-settings/`, settings);
  return response.data;
};

// İstatistikler
export const getSystemStats = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/admin/stats/`);
  return response.data;
};

// Yedekleme işlemleri
export const getBackups = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/admin/backups/`);
  return response.data;
};

export const restoreBackup = async (backupId: number) => {
  const response = await axios.post(`${API_BASE_URL}/api/admin/backups/${backupId}/restore/`);
  return response.data;
};

// API anahtarları
export const getApiKeys = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/admin/api-keys/`);
  return response.data;
};

export const createApiKey = async (keyData: any) => {
  const response = await axios.post(`${API_BASE_URL}/api/admin/api-keys/`, keyData);
  return response.data;
};

export const revokeApiKey = async (keyId: number) => {
  const response = await axios.delete(`${API_BASE_URL}/api/admin/api-keys/${keyId}/`);
  return response.data;
}; 