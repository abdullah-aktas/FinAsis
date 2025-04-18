import axios from 'axios';

// API temel URL'si
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Axios örneği oluşturma
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// İstek interceptor'ı - token ekleme
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Yanıt interceptor'ı - hata yönetimi
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 Unauthorized hatası - oturum sonlandırma
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api; 