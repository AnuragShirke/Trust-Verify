import axios from 'axios';

// Use environment variable for API URL with fallback
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// User profile functions
export const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/me/profile');
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw new Error('Failed to fetch user profile');
  }
};

export const fetchUserAnalyses = async () => {
  try {
    const response = await api.get('/users/me/analyses');
    return response.data;
  } catch (error) {
    console.error('Error fetching user analyses:', error);
    throw new Error('Failed to fetch user analyses');
  }
};

// Password reset functions
export const requestPasswordReset = async (email) => {
  try {
    const response = await api.post('/forgot-password', { email });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to request password reset');
    }
    throw new Error('Failed to request password reset. Please try again.');
  }
};

export const resetPassword = async (token, new_password) => {
  try {
    const response = await api.post('/reset-password', { token, new_password });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to reset password');
    }
    throw new Error('Failed to reset password. Please try again.');
  }
};

export default api;
