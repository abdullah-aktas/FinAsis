import api from './api';

// Kimlik doğrulama servisi
const authService = {
  // Giriş
  login: (username: string, password: string) => 
    api.post('/auth/login/', { username, password })
      .then(response => {
        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response.data;
      }),
  
  // Kayıt
  register: (userData: any) => 
    api.post('/auth/register/', userData)
      .then(response => {
        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response.data;
      }),
  
  // Çıkış
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return Promise.resolve();
  },
  
  // Kullanıcı bilgilerini getir
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },
  
  // Token'ı getir
  getToken: () => {
    return localStorage.getItem('token');
  },
  
  // Kullanıcı güncelleme
  updateProfile: (userData: any) => 
    api.put('/auth/profile/', userData)
      .then(response => {
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
      }),
  
  // Şifre değiştirme
  changePassword: (oldPassword: string, newPassword: string) => 
    api.post('/auth/change-password/', { oldPassword, newPassword }),
  
  // Şifre sıfırlama isteği
  requestPasswordReset: (email: string) => 
    api.post('/auth/password-reset/', { email }),
  
  // Şifre sıfırlama
  resetPassword: (token: string, newPassword: string) => 
    api.post('/auth/password-reset/confirm/', { token, newPassword }),
  
  // E-posta doğrulama
  verifyEmail: (token: string) => 
    api.post('/auth/verify-email/', { token }),
  
  // E-posta doğrulama isteği
  requestEmailVerification: () => 
    api.post('/auth/verify-email/request/'),
};

export default authService; 