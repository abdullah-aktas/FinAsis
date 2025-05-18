import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token interceptor
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        await AsyncStorage.setItem('access_token', access_token);
        await AsyncStorage.setItem('refresh_token', refresh_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token başarısız oldu, kullanıcıyı çıkış yaptır
        await AsyncStorage.removeItem('access_token');
        await AsyncStorage.removeItem('refresh_token');
        // Navigate to login
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username: string, password: string, deviceId: string) => {
    const response = await api.post('/mobile/auth', {
      username,
      password,
      device_id: deviceId,
      device_info: {
        platform: 'react-native',
        version: '1.0.0',
      },
    });
    return response.data;
  },

  verifyTwoFactor: async (deviceId: string, verificationCode: string) => {
    const response = await api.post('/mobile/two-factor', {
      device_id: deviceId,
      verification_code: verificationCode,
    });
    return response.data;
  },
};

export const syncService = {
  syncData: async (deviceId: string, data: any, type: 'full' | 'partial' = 'full') => {
    const response = await api.post('/mobile/sync', {
      device_id: deviceId,
      data,
      type,
    });
    return response.data;
  },
};

export const notificationService = {
  getNotifications: async () => {
    const response = await api.get('/mobile/notifications');
    return response.data;
  },

  markAsRead: async (notificationId: string) => {
    const response = await api.post(`/mobile/notifications/${notificationId}/read`);
    return response.data;
  },
};

export const educationService = {
  getCourses: async (): Promise<Course[]> => {
    const response = await api.get('/api/education/courses/');
    return response.data;
  },
  getCourse: async (id: number): Promise<Course> => {
    const response = await api.get(`/api/education/courses/${id}/`);
    return response.data;
  },
  getLesson: async (id: number): Promise<Lesson> => {
    const response = await api.get(`/api/education/lessons/${id}/`);
    return response.data;
  },
};

export default api; 