import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import auditService from '../../services/auditService';
import authService from '../../services/authService';
import './Admin.css';

const AdminAudits = () => {
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authService.isAdmin()) {
      navigate('/');
      return;
    }
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const data = await auditService.getLogs();
      setLogs(data);
    } catch (err) {
      setError('Failed to load audit logs');
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
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
    <div className="admin-container" style={{maxWidth: '1200px'}}>
      <div className="admin-card">
        <div className="admin-header">
          <h2>Admin Dashboard</h2>
          <button onClick={() => navigate('/')} className="back-btn">
            Back to Home
          </button>
        </div>
        <div className="admin-tabs">
          <button className="tab-btn" onClick={() => navigate('/admin/users')}>Manage Users</button>
          <button className="tab-btn" onClick={() => navigate('/admin/kyc')}>Review KYC</button>
          <button className="tab-btn active" onClick={() => navigate('/admin/audits')}>View Audits</button>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Service</th>
                <th>Action</th>
                <th>User ID</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                    <td colSpan="6" style={{textAlign: 'center'}}>No audit logs found.</td>
                </tr>
              ) : logs.map(log => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                  <td><span className="kyc-badge verified">{log.service_name}</span></td>
                  <td style={{fontWeight: 'bold'}}>{log.action}</td>
                  <td>{log.user_id || 'System'}</td>
                  <td>{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminAudits;
