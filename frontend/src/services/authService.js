import axios from 'axios';
import userService from './userService';

const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8000';

const authAPI = axios.create({
  baseURL: AUTH_API_URL,
});

const authService = {
  // Register user
  register: async (userData) => {
    try {
      const response = await authAPI.post('/auth/register', userData);
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Try to create profile (if profile creation is separate)
        // You might want to redirect to profile completion page instead
      }
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Registration failed' };
    }
  },

  // Login user
  login: async (credentials) => {
    try {
      const response = await authAPI.post('/auth/login', credentials);
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Fetch user profile after login
        try {
          const profile = await userService.getCurrentProfile();
          localStorage.setItem('user_profile', JSON.stringify(profile));
        } catch (profileError) {
          // Profile doesn't exist yet, that's ok
          console.log('Profile not found, user needs to complete profile');
        }
      }
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Login failed' };
    }
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_profile');
    window.location.href = '/login';
  },

  // Get current user from auth
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },

  // Get current user profile
  getCurrentProfile: () => {
    const profileStr = localStorage.getItem('user_profile');
    if (profileStr) {
      return JSON.parse(profileStr);
    }
    return null;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Check if user has profile
  hasProfile: () => {
    return !!localStorage.getItem('user_profile');
  },

  // Get user role
  getUserRole: () => {
    const user = authService.getCurrentUser();
    return user?.role || 'USER';
  },

  // Check if user is admin
  isAdmin: () => {
    return authService.getUserRole() === 'ADMIN';
  }
};

export default authService;