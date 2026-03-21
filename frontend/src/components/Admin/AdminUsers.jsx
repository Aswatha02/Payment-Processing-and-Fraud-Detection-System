import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/userService';
import authService from '../../services/authService';
import './Admin.css';

const AdminUsers = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is admin
    if (!authService.isAdmin()) {
      navigate('/');
      return;
    }
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await userService.getAllUsers();
      setUsers(response.users);
    } catch (err) {
      setError('Failed to load users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKYCUpdate = async (userId, status) => {
    try {
      await userService.updateKYCStatus(userId, status);
      // Refresh users list
      fetchUsers();
    } catch (err) {
      alert('Failed to update KYC status');
    }
  };

  if (loading) {
    return (
      <div className="admin-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-card">
        <div className="admin-header">
          <h2>User Management</h2>
          <button onClick={() => navigate('/')} className="back-btn">
            Back to Home
          </button>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Phone</th>
                <th>KYC Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.user_id}>
                  <td>{user.user_id}</td>
                  <td>{user.full_name}</td>
                  <td>{user.phone || '—'}</td>
                  <td>
                    <span className={`kyc-badge ${user.kyc_status.toLowerCase()}`}>
                      {user.kyc_status}
                    </span>
                  </td>
                  <td className="actions">
                    {user.kyc_status === 'SUBMITTED' && (
                      <>
                        <button 
                          onClick={() => handleKYCUpdate(user.user_id, 'VERIFIED')}
                          className="action-btn approve"
                        >
                          Approve
                        </button>
                        <button 
                          onClick={() => handleKYCUpdate(user.user_id, 'REJECTED')}
                          className="action-btn reject"
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminUsers;