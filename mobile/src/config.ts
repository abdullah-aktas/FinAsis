export const API_URL = 'http://localhost:8000/api'; // Backend API URL'si
export const APP_VERSION = '1.0.0';

// AsyncStorage anahtarları
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  DEVICE_ID: 'device_id',
};

// API timeout süreleri (ms)
export const API_TIMEOUTS = {
  DEFAULT: 10000,
  UPLOAD: 30000,
};

// Hata mesajları
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'İnternet bağlantısı hatası. Lütfen bağlantınızı kontrol edin.',
  SERVER_ERROR: 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.',
  AUTH_ERROR: 'Oturum süreniz doldu. Lütfen tekrar giriş yapın.',
  VALIDATION_ERROR: 'Lütfen tüm alanları doğru şekilde doldurun.',
}; 