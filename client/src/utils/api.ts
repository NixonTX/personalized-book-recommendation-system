import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // Adjust if your backend URL differs
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include access token
api.interceptors.request.use((config) => {
  const authHeader = config.headers.Authorization;
  if (typeof authHeader === 'string' && authHeader.startsWith('Bearer ')) {
    const token = authHeader.replace('Bearer ', '');
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;