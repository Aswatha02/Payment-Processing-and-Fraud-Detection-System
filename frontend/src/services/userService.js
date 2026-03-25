import axios from 'axios';

const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8000';
const USER_API_URL = process.env.REACT_APP_USER_API_URL || 'http://localhost:8001';

// Create axios instances
const authAPI = axios.create({
  baseURL: AUTH_API_URL,
});

const userAPI = axios.create({
  baseURL: USER_API_URL,
});

// Add token to requests
userAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

const userService = {
  // Create user profile (after registration)
  createProfile: async (userData) => {
    try {
      const response = await userAPI.post('/users/', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to create profile' };
    }
  },

  // Get current user profile
  getCurrentProfile: async () => {
    try {
      const response = await userAPI.get('/users/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to get profile' };
    }
  },

  // Get user by ID
  getUserById: async (userId) => {
    try {
      const response = await userAPI.get(`/users/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to get user' };
    }
  },

  // Update user profile
  updateProfile: async (userId, userData) => {
    try {
      const response = await userAPI.put(`/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to update profile' };
    }
  },

  // Get all users (admin only)
  getAllUsers: async (skip = 0, limit = 10, kycStatus = null) => {
    try {
      let url = `/users/?skip=${skip}&limit=${limit}`;
      if (kycStatus) {
        url += `&kyc_status=${kycStatus}`;
      }
      const response = await userAPI.get(url);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to get users' };
    }
  },

  // Submit KYC documents (user)
  submitKYC: async (documentUrl) => {
    try {
      const response = await userAPI.post('/users/kyc/submit', { kyc_document_url: documentUrl });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to submit KYC' };
    }
  },

  // Update KYC status (admin only)
  updateKYCStatus: async (userId, kycStatus, rejectionReason = null) => {
    try {
      const payload = { kyc_status: kycStatus };
      if (rejectionReason) payload.rejection_reason = rejectionReason;
      
      const response = await userAPI.patch(`/users/${userId}/kyc`, payload);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to update KYC status' };
    }
  },

  // Get full user info (profile + role)
  getFullUserInfo: async (userId) => {
    try {
      const response = await userAPI.get(`/users/${userId}/full`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to get full user info' };
    }
  },

  // Toggle user suspension
  toggleSuspend: async (userId, suspend) => {
    try {
      const response = await userAPI.patch(`/users/${userId}/suspend?suspend=${suspend}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to update suspension status' };
    }
  }
};

export default userService;