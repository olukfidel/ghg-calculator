import axios from 'axios';

/**
 * Create a global Axios instance.
 */
const api = axios.create({
  // The base URL will be handled by the proxy in development
  // and will be relative in production (Nginx proxy)
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor to add the auth token to every request
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Interceptor to handle 401 (Unauthorized) errors.
 * This can be used to auto-logout the user if their token expires.
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token is invalid or expired
      localStorage.removeItem('authToken');
      // Reload the page to reset app state (or call logout)
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// --- Export API functions ---

// Auth
export const login = (email, password) => api.post('/auth/login', { email, password });
export const register = (data) => api.post('/auth/register', data);

// Factors
export const getFactors = () => api.get('/api/factors');

// Inputs
export const postInput = (data) => api.post('/api/inputs', data);
export const getInputs = (page = 1, per_page = 20) =>
  api.get(`/api/inputs?page=${page}&per_page=${per_page}`);

// Dashboard
export const getDashboardSummary = () => api.get('/api/dashboard/summary');

// Reports
export const getReports = () => api.get('/api/reports');
export const postReport = (data) => api.post('/api/reports', data);
export const getReportDetails = (id) => api.get(`/api/reports/${id}`);

export default api;