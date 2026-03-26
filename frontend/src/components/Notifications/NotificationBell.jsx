import React, { useState, useEffect } from 'react';
import notificationService from '../../services/notificationService';
import authService from '../../services/authService';
import './NotificationBell.css';

const NotificationBell = () => {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    const user = authService.getCurrentUser();
    if (user && user.id) {
       const data = await notificationService.getNotifications(user.id);
       setNotifications(data);
    }
  };

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="notification-container">
      <button className="bell-button" onClick={toggleDropdown}>
        🔔 <span className="badge">{notifications.length}</span>
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="dropdown-header">
            <h4>Notifications ({notifications.length})</h4>
          </div>
          <div className="dropdown-list">
            {notifications.length === 0 ? (
              <div className="no-notifications">No new notifications</div>
            ) : (
              notifications.map((notif) => (
                <div key={notif.id} className={`notification-item ${notif.type}`}>
                  <p>{notif.message}</p>
                  <small>{new Date(notif.timestamp).toLocaleString()}</small>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
