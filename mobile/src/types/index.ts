export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  permissions: string[];
}

export interface AuthResponse {
  status: 'success' | 'error' | 'two_factor_required';
  message?: string;
  access_token?: string;
  refresh_token?: string;
  user?: User;
  expires_in?: number;
}

export interface DeviceInfo {
  platform: string;
  version: string;
  model?: string;
  manufacturer?: string;
}

export interface SyncData {
  device_id: string;
  data: any;
  type: 'full' | 'partial';
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  created_at: string;
}

export interface ApiError {
  status: 'error';
  message: string;
  code?: string;
  details?: any;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  category: string;
  level: string;
  duration: number;
  image?: string;
  is_active: boolean;
}

export interface Lesson {
  id: number;
  course: number;
  title: string;
  content: string;
  order: number;
  video_url?: string;
} 