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

export default api;
