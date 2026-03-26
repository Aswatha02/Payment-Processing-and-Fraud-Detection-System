import axios from 'axios';

const API_URL = 'http://localhost:8006/notifications';

const getNotifications = async (userId) => {
    if (!userId) return [];
    try {
        const response = await axios.get(`${API_URL}/${userId}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching notifications", error);
        return [];
    }
};

const notificationService = {
    getNotifications
};

export default notificationService;
