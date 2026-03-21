import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import userService from '../../services/userService';
import './Auth.css';

const Profile = () => {
  const navigate = useNavigate();
  const [authUser, setAuthUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      // Get auth user data from localStorage
      const authData = authService.getCurrentUser();
      setAuthUser(authData);
      
      // Get user profile from user service
      const profile = await userService.getCurrentProfile();
      setUserProfile(profile);
      localStorage.setItem('user_profile', JSON.stringify(profile));
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
  };

  const getKYCStatusText = (status) => {
    switch(status) {
      case 'VERIFIED': return '✓ Verified';
      case 'PENDING': return '⏳ Pending';
      case 'SUBMITTED': return '📤 Submitted';
      case 'REJECTED': return '✗ Rejected';
      default: return 'Not Started';
    }
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-card fade-in">
        <div className="profile-header">
          <div className="profile-avatar">
            {authUser?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <h2>{userProfile?.full_name || authUser?.username}</h2>
          <p>Member since {new Date(authUser?.created_at).toLocaleDateString()}</p>
        </div>
        
        <div className="profile-content">
          {error && <div className="error-message">{error}</div>}
          
          <div className="profile-section">
            <h3>Account Information</h3>
            <div className="info-grid">
              <div className="info-row">
                <span className="info-label">📧 Email</span>
                <span className="info-value">{authUser?.email}</span>
              </div>
              <div className="info-row">
                <span className="info-label">👤 Username</span>
                <span className="info-value">{authUser?.username}</span>
              </div>
              <div className="info-row">
                <span className="info-label">🆔 User ID</span>
                <span className="info-value">{authUser?.id}</span>
              </div>
              <div className="info-row">
                <span className="info-label">⭐ Role</span>
                <span className="info-value">{authUser?.role || 'USER'}</span>
              </div>
            </div>
          </div>
          
          {userProfile && (
            <div className="profile-section">
              <h3>Profile Information</h3>
              <div className="info-grid">
                <div className="info-row">
                  <span className="info-label">📝 Full Name</span>
                  <span className="info-value">{userProfile.full_name || 'Not set'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">📞 Phone</span>
                  <span className="info-value">{userProfile.phone || 'Not set'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">📍 Address</span>
                  <span className="info-value">{userProfile.address || 'Not set'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">🎂 Date of Birth</span>
                  <span className="info-value">{userProfile.dob || 'Not set'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">🔒 KYC Status</span>
                  <span className={`kyc-status-badge ${userProfile.kyc_status?.toLowerCase()}`}>
                    {getKYCStatusText(userProfile.kyc_status)}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <div className="profile-actions">
            <button onClick={() => navigate('/')} className="profile-btn secondary">
              ← Back to Home
            </button>
            <button onClick={handleLogout} className="profile-btn danger">
              🚪 Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;