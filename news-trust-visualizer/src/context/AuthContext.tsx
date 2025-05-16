import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, fetchCurrentUser } from '@/lib/api';

interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
  last_login: string | null;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          const userData = await fetchCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch user data:', error);
          localStorage.removeItem('token');
        }
      }
      
      setIsLoading(false);
    };
    
    checkAuthStatus();
  }, []);

  const login = async (email: string, password: string) => {
    const { access_token } = await loginUser(email, password);
    localStorage.setItem('token', access_token);
    
    // Fetch user data after successful login
    const userData = await fetchCurrentUser();
    setUser(userData);
  };

  const register = async (email: string, username: string, password: string) => {
    const userData = await registerUser(email, username, password);
    
    // Auto login after registration
    await login(email, password);
    
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
