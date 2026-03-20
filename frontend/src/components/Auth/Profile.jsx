import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const API_URL = process.env.REACT_APP_API_URL;

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (err) {
      setError('Failed to load profile');
      if (err.response?.status === 401) {
        localStorage.clear();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="auth-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card fade-in">
        <div className="auth-header">
          <h2>Profile</h2>
          <p>Your account information</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        {user && (
          <div className="profile-info">
            <div className="info-row">
              <strong>Username:</strong>
              <span>{user.username}</span>
            </div>
            
            <div className="info-row">
              <strong>Email:</strong>
              <span>{user.email}</span>
            </div>
            
            <div className="info-row">
              <strong>User ID:</strong>
              <span>{user.id}</span>
            </div>
            
            <div className="info-row">
              <strong>Joined:</strong>
              <span>{new Date(user.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        )}
        
        <div className="button-group">
          <button onClick={() => navigate('/')} className="auth-btn secondary">
            Back to Home
          </button>
          <button onClick={handleLogout} className="auth-btn logout">
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;