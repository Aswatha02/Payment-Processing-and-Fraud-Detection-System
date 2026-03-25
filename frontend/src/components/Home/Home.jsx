import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import userService from '../../services/userService';
import walletService from '../../services/walletService';
import fraudService from '../../services/fraudService';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [greeting, setGreeting] = useState('');
  
  // Stats state
  const [stats, setStats] = useState({
    totalTransactions: 0,
    successfulPayments: 0,
    walletBalance: 0
  });

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  useEffect(() => {
    setGreeting(getGreeting());
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const currentUser = authService.getCurrentUser();
      setUser(currentUser);
      
      // Fetch user profile
      try {
        const userProfile = await userService.getCurrentProfile();
        setProfile(userProfile);
        localStorage.setItem('user_profile', JSON.stringify(userProfile));
      } catch (err) {
        // No profile yet, redirect to profile completion
        if (err.detail === 'User profile not found') {
          navigate('/complete-profile');
          return;
        }
      }

      if (currentUser && currentUser.id) {
        // Fetch stats if user is not admin
        if (!authService.isAdmin()) {
          try {
            const dashboardData = await walletService.getDashboardStats(currentUser.id);
            setStats({
              totalTransactions: dashboardData.total_transactions || 0,
              successfulPayments: dashboardData.successful_transactions || 0,
              walletBalance: dashboardData.wallet_balance || 0
            });
          } catch (statsErr) {
            console.error('Error fetching dashboard stats:', statsErr);
          }
        }
      }

    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
  };

  const getKYCStatusColor = (status) => {
    switch(status) {
      case 'VERIFIED': return '#27ae60';
      case 'SUBMITTED': return '#3498db';
      case 'REJECTED': return '#e74c3c';
      case 'NOT_SUBMITTED':
      default: return '#95a5a6';
    }
  };

  const getKYCStatusText = (status) => {
    switch(status) {
      case 'VERIFIED': return '✓ Verified';
      case 'SUBMITTED': return '⏳ Under Review';
      case 'REJECTED': return '✗ Rejected';
      case 'NOT_SUBMITTED':
      default: return 'Not Submitted';
    }
  };

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="home-content fade-in">
        <div className="welcome-card">
          <h1 className="welcome-title">
            {greeting}, {profile?.full_name || user?.username || 'User'}! 👋
          </h1>
          <p className="welcome-subtitle">
            Welcome to Payment Processing & Fraud Detection System
          </p>
          
          {/* KYC Status Banner */}
          {profile && (
            <div className="kyc-banner" style={{ borderLeftColor: getKYCStatusColor(profile.kyc_status) }}>
              <span className="kyc-status">
                KYC Status: {getKYCStatusText(profile.kyc_status)}
              </span>
              {(!profile.kyc_status || profile.kyc_status === 'NOT_SUBMITTED' || profile.kyc_status === 'REJECTED') && (
                <button onClick={() => navigate('/kyc-submit')} className="kyc-btn">
                  Submit KYC
                </button>
              )}
            </div>
          )}
          
          {!authService.isAdmin() && (
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-info">
                  <h3>Total Transactions</h3>
                  <p>{stats.totalTransactions}</p>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-info">
                  <h3>Successful Payments</h3>
                  <p>{stats.successfulPayments}</p>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">📈</div>
                <div className="stat-info">
                  <h3>Wallet Balance</h3>
                  <p>${parseFloat(stats.walletBalance || 0).toFixed(2)}</p>
                </div>
              </div>
            </div>
          )}

          {authService.isAdmin() && (
            <div className="admin-dashboard-welcome" style={{margin: '2rem 0', padding: '1.5rem', backgroundColor: 'rgba(52, 152, 219, 0.1)', borderRadius: '10px', borderLeft: '4px solid #3498db'}}>
              <h3 style={{color: '#2980b9', marginBottom: '0.5rem'}}>System Administrator Dashboard</h3>
              <p style={{color: '#34495e'}}>You have full access to monitor fraud, manage given user roles, and oversee all system operations.</p>
            </div>
          )}
          
          <div className="action-buttons">
            {!authService.isAdmin() && (
              <>
                <button 
                  onClick={() => navigate('/profile')} 
                  className="home-btn primary"
                >
                  View Profile
                </button>
                <button 
                  onClick={() => navigate('/wallet')} 
                  className="home-btn primary"
                >
                  My Wallet
                </button>
              </>
            )}
            <button 
              onClick={handleLogout} 
              className="home-btn logout"
            >
              Logout
            </button>
          </div>
          
          {/* Admin Quick Actions */}
          {authService.isAdmin() && (
            <div className="admin-section">
              <h3>Admin Actions</h3>
              <div className="admin-buttons">
                <button onClick={() => navigate('/admin/users')} className="admin-btn">
                  Manage Users
                </button>
                <button onClick={() => navigate('/admin/kyc')} className="admin-btn">
                  Review KYC
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;