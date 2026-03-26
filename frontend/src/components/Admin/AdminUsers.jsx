import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/userService';
import authService from '../../services/authService';
import fraudService from '../../services/fraudService';
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

  const handleSuspend = async (userId, suspend) => {
    try {
      if (window.confirm(`Are you sure you want to ${suspend ? 'suspend' : 'unsuspend'} this user?`)) {
        await userService.toggleSuspend(userId, suspend);
        fetchUsers();
      }
    } catch (err) {
      alert('Failed to update suspension status: ' + (err.detail || err.message));
    }
  };

  const handleViewFraud = async (userId) => {
    try {
      const stats = await fraudService.getUserStats(userId);
      alert(`Fraud Stats for User ${userId}:\nFlagged Transactions: ${stats.flagged_transactions}\nCurrent Risk Score: ${stats.current_risk_score}`);
    } catch (err) {
      alert('Failed to fetch fraud stats: ' + (err.detail || err.message));
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
          <h2>Admin Dashboard</h2>
          <button onClick={() => navigate('/')} className="back-btn">
            Back to Home
          </button>
        </div>
        <div className="admin-tabs">
          <button className="tab-btn active" onClick={() => navigate('/admin/users')}>Manage Users</button>
          <button className="tab-btn" onClick={() => navigate('/admin/kyc')}>Review KYC</button>
          <button className="tab-btn" onClick={() => navigate('/admin/audits')}>View Audits</button>
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
                <th>Account Status</th>
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
                    <span className={`kyc-badge ${user.kyc_status?.toLowerCase() || 'not_submitted'}`}>
                      {user.kyc_status || 'NOT_SUBMITTED'}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      padding: '4px 8px', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 'bold',
                      backgroundColor: user.is_suspended ? '#ffebee' : '#e8f5e9',
                      color: user.is_suspended ? '#c62828' : '#2e7d32'
                    }}>
                      {user.is_suspended ? 'Suspended' : 'Active'}
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
                    <button 
                      onClick={() => handleSuspend(user.user_id, !user.is_suspended)}
                      className={`action-btn ${user.is_suspended ? 'approve' : 'reject'}`}
                      style={{marginLeft: '0.5rem'}}
                    >
                      {user.is_suspended ? 'Unsuspend' : 'Suspend'}
                    </button>
                    <button 
                      onClick={() => handleViewFraud(user.user_id)}
                      className="action-btn"
                      style={{marginLeft: '0.5rem', backgroundColor: '#f39c12', color: 'white'}}
                    >
                      Fraud Stats
                    </button>
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