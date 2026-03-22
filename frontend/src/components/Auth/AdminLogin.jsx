import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8000';

const AdminLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${AUTH_API_URL}/auth/admin/login`, formData);
      
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({ ...response.data.user, role: 'ADMIN' }));
        // Redirect to admin dashboard
        navigate('/admin/users');
      }
    } catch (err) {
      console.error('Admin Login error:', err);
      setError(err.response?.data?.detail || 'Admin Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card fade-in" style={{ borderTop: '5px solid #003366' }}>
        <div className="auth-header">
          <h2>Admin Portal</h2>
          <p>Login to the administrator dashboard</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Admin Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter admin email"
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter admin password"
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? 'Authenticating...' : 'Secure Login'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            New administrator? <Link to="/admin/register">Register Core Admin</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
