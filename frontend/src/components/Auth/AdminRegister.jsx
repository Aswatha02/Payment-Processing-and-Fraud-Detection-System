import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8000';

const AdminRegister = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    admin_secret: ''
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
      await axios.post(`${AUTH_API_URL}/auth/admin/register`, formData);
      // Automatically navigate to login after successful register
      navigate('/admin/login');
    } catch (err) {
      console.error('Admin Register error:', err);
      setError(err.response?.data?.detail || 'Admin Registration failed. Check your secret key.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card fade-in" style={{ borderTop: '5px solid #00509e' }}>
        <div className="auth-header">
          <h2>Core Administrator</h2>
          <p>Register a new system admin</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Admin username"
            />
          </div>

          <div className="form-group">
            <label>Admin Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Admin email"
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
              placeholder="Strong password required"
            />
          </div>

          <div className="form-group">
            <label>System Admin Secret</label>
            <input
              type="password"
              name="admin_secret"
              value={formData.admin_secret}
              onChange={handleChange}
              required
              placeholder="Enter the secure ADMIN_SECRET key"
            />
            <span className="hint">Required for authorization</span>
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? 'Registering...' : 'Register Target Admin'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            Already an administrator? <Link to="/admin/login">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminRegister;
