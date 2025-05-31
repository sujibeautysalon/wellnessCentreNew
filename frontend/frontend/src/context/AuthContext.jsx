import { createContext, useState, useEffect, useContext } from 'react';
import Cookies from 'js-cookie';
import { authService } from '../api/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already logged in (has a token)
    const token = Cookies.get('auth_token');
    
    if (token) {
      // Fetch user profile data
      authService.getProfile()
        .then(response => {
          setCurrentUser(response.data);
        })
        .catch(error => {
          console.error('Failed to fetch user profile:', error);
          
          // If token is invalid, remove it
          if (error.response?.status === 401) {
            Cookies.remove('auth_token');
            Cookies.remove('refresh_token');
          }
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authService.login({ email, password });
      
      // Store tokens in cookies
      Cookies.set('auth_token', response.data.access);
      Cookies.set('refresh_token', response.data.refresh);
      
      // Fetch user profile data after login
      const userResponse = await authService.getProfile();
      setCurrentUser(userResponse.data);
      
      return userResponse.data;
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed. Please check your credentials.');
      throw error;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      const response = await authService.register(userData);
      return response.data;
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed. Please try again.');
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Call logout API if available
      await authService.logout();
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // Remove tokens regardless of API success
      Cookies.remove('auth_token');
      Cookies.remove('refresh_token');
      setCurrentUser(null);
    }
  };

  const updateProfile = async (profileData) => {
    setError(null);
    try {
      const response = await authService.updateProfile(profileData);
      setCurrentUser(response.data);
      return response.data;
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update profile.');
      throw error;
    }
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!currentUser,
    isAdmin: currentUser?.role === 'admin',
    isTherapist: currentUser?.role === 'therapist',
    isCustomer: currentUser?.role === 'customer',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
