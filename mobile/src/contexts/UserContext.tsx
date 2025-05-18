import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type UserRole = 'student' | 'teacher' | 'accountant' | 'hr' | 'crm' | 'admin' | 'employee' | 'customer';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  permissions?: string[];
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType>({
  user: null,
  setUser: () => {},
  logout: () => {},
});

export const UserProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // AsyncStorage'dan kullanıcıyı yükle
    AsyncStorage.getItem('user').then(data => {
      if (data) setUser(JSON.parse(data));
    });
  }, []);

  const logout = () => {
    setUser(null);
    AsyncStorage.removeItem('user');
    AsyncStorage.removeItem('access_token');
    AsyncStorage.removeItem('refresh_token');
  };

  return (
    <UserContext.Provider value={{ user, setUser, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext); 