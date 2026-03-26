import axios from 'axios';

const API_URL = 'http://localhost:8005/audit';

const getLogs = async (skip = 0, limit = 100) => {
  const response = await axios.get(`${API_URL}/?skip=${skip}&limit=${limit}`);
  return response.data;
};

const getUserLogs = async (userId, skip = 0, limit = 100) => {
  const response = await axios.get(`${API_URL}/${userId}?skip=${skip}&limit=${limit}`);
  return response.data;
};

const auditService = {
  getLogs,
  getUserLogs
};

export default auditService;
