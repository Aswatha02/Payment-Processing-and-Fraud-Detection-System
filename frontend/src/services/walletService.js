import axios from 'axios';

const WALLET_API_URL = process.env.REACT_APP_WALLET_API_URL || 'http://localhost:8002';

const walletAPI = axios.create({
  baseURL: WALLET_API_URL,
});

const TRANSACTION_API_URL = process.env.REACT_APP_TRANSACTION_API_URL || 'http://localhost:8003';
const transactionAPI = axios.create({
  baseURL: TRANSACTION_API_URL,
});

// Add token to requests
const authInterceptor = (config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

walletAPI.interceptors.request.use(authInterceptor, (error) => Promise.reject(error));
transactionAPI.interceptors.request.use(authInterceptor, (error) => Promise.reject(error));

const walletService = {
  // Get wallet balance
  getBalance: async (userId) => {
    try {
      const response = await walletAPI.get(`/wallet/${userId}/balance`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to fetch balance' };
    }
  },

  // Get transaction history
  getTransactions: async (userId, skip = 0, limit = 50) => {
    try {
      const response = await transactionAPI.get(`/transactions/${userId}/history?skip=${skip}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to fetch transactions' };
    }
  },

  // Deposit funds
  deposit: async (userId, amount) => {
    try {
      const response = await walletAPI.post('/wallet/deposit', {
        user_id: userId,
        amount: parseFloat(amount)
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Deposit failed' };
    }
  },

  // Withdraw funds
  withdraw: async (userId, amount) => {
    try {
      const response = await walletAPI.post('/wallet/withdraw', {
        user_id: userId,
        amount: parseFloat(amount)
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Withdrawal failed' };
    }
  },

  // Transfer funds (P2P)
  transfer: async (userId, recipientId, amount) => {
    try {
      const response = await transactionAPI.post('/transactions/transfer', {
        sender_id: userId,
        receiver_id: parseInt(recipientId),
        amount: parseFloat(amount)
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Transfer failed' };
    }
  },

  // Get dashboard stats
  getDashboardStats: async (userId) => {
    try {
      const response = await transactionAPI.get(`/transactions/${userId}/dashboard`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to fetch dashboard stats' };
    }
  },

  // Get admin flagged transactions
  getAdminFlaggedTransactions: async () => {
    try {
      const response = await transactionAPI.get('/transactions/admin/flagged');
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Failed to fetch flagged transactions' };
    }
  }
};

export default walletService;
