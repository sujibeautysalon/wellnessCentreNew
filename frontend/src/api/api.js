import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add a response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const originalRequest = error.config;
    
    // Handle 401 - Unauthorized (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh the token
      const refreshToken = Cookies.get('refresh_token');
      if (refreshToken) {
        return apiClient.post('/auth/token/refresh/', { refresh: refreshToken })
          .then((res) => {
            if (res.status === 200) {
              Cookies.set('auth_token', res.data.access);
              
              // Retry the original request with new token
              originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
              return apiClient(originalRequest);
            }
          })
          .catch(() => {
            // If refresh token fails, logout user
            Cookies.remove('auth_token');
            Cookies.remove('refresh_token');
            window.location.href = '/login';
          });
      } else {
        // No refresh token, logout user
        Cookies.remove('auth_token');
        window.location.href = '/login';
      }
    }
    
    // Handle other errors
    return Promise.reject(error);
  }
);

// API service functions
export const authService = {
  login: (credentials) => apiClient.post('/auth/login/', credentials),
  register: (userData) => apiClient.post('/auth/register/', userData),
  logout: () => apiClient.post('/auth/logout/'),
  getProfile: () => apiClient.get('/auth/profile/'),
  updateProfile: (data) => apiClient.put('/auth/profile/', data),
};

export const financeService = {
  getBudgets: () => apiClient.get('/finance/budgets/'),
  getBudget: (id) => apiClient.get(`/finance/budgets/${id}/`),
  createBudget: (data) => apiClient.post('/finance/budgets/', data),
  updateBudget: (id, data) => apiClient.put(`/finance/budgets/${id}/`, data),
  deleteBudget: (id) => apiClient.delete(`/finance/budgets/${id}/`),
  
  getTransactions: (params) => apiClient.get('/finance/transactions/', { params }),
  getTransaction: (id) => apiClient.get(`/finance/transactions/${id}/`),
  createTransaction: (data) => apiClient.post('/finance/transactions/', data),
  updateTransaction: (id, data) => apiClient.put(`/finance/transactions/${id}/`, data),
  deleteTransaction: (id) => apiClient.delete(`/finance/transactions/${id}/`),
  
  getFinancialReports: () => apiClient.get('/finance/reports/'),
  getFinancialReport: (id) => apiClient.get(`/finance/reports/${id}/`),
  generateFinancialReport: (data) => apiClient.post('/finance/reports/generate/', data),
};

export const analyticsService = {
  getDashboards: () => apiClient.get('/analytics/dashboards/'),
  getDashboard: (id) => apiClient.get(`/analytics/dashboards/${id}/`),
  createDashboard: (data) => apiClient.post('/analytics/dashboards/', data),
  updateDashboard: (id, data) => apiClient.put(`/analytics/dashboards/${id}/`, data),
  deleteDashboard: (id) => apiClient.delete(`/analytics/dashboards/${id}/`),
  
  getMetrics: () => apiClient.get('/analytics/metrics/'),
  getMetric: (id) => apiClient.get(`/analytics/metrics/${id}/`),
  getMetricHistory: (id) => apiClient.get(`/analytics/metrics/${id}/history/`),
  
  getReports: () => apiClient.get('/analytics/reports/'),
  getReport: (id) => apiClient.get(`/analytics/reports/${id}/`),
  generateReport: (data) => apiClient.post('/analytics/reports/generate/', data),
  
  getCustomerJourney: (customerId) => apiClient.get(`/analytics/customer-journey/${customerId}/`),
};

export default apiClient;
