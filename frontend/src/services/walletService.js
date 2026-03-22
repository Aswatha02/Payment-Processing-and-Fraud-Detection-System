import axios from 'axios';

const WALLET_API_URL = process.env.REACT_APP_WALLET_API_URL || 'http://localhost:8002';

const walletAPI = axios.create({
  baseURL: WALLET_API_URL,
});

// Add token to requests
walletAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

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
      const response = await walletAPI.get(`/wallet/${userId}/transactions?skip=${skip}&limit=${limit}`);
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
      const response = await walletAPI.post('/wallet/transfer', {
        user_id: userId,
        recipient_id: parseInt(recipientId),
        amount: parseFloat(amount)
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Transfer failed' };
    }
  }
};

export default walletService;
