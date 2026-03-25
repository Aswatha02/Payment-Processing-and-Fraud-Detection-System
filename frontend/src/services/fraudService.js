import axios from 'axios';

const FRAUD_API_URL = process.env.REACT_APP_FRAUD_API_URL || 'http://localhost:8004';

const fraudAPI = axios.create({
  baseURL: FRAUD_API_URL,
});

// Optional: Add request interceptor if fraud service ever needs auth tokens
// fraudAPI.interceptors.request.use((config) => {
//   const token = localStorage.getItem('access_token');
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

const fraudService = {
  getUserStats: async (userId) => {
    try {
      const response = await fraudAPI.get(`/fraud/stats/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching fraud stats:', error);
      return { flagged_transactions: 0, current_risk_score: 0 };
    }
  },
  
  getAdminStats: async () => {
    try {
      const response = await fraudAPI.get(`/fraud/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching admin fraud stats:', error);
      return { total_records: 0, flagged_count: 0, records: [] };
    }
  }
};

export default fraudService;
