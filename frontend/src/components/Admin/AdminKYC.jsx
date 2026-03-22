import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/userService';
import authService from '../../services/authService';
import './Admin.css';

const AdminKYC = () => {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    // Check if user is admin
    if (!authService.isAdmin()) {
      navigate('/');
      return;
    }
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      const response = await userService.getAllUsers(0, 50, 'SUBMITTED');
      setSubmissions(response.users);
    } catch (err) {
      console.error('Error fetching submissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (userId, action) => {
    try {
      let reason = null;
      if (action === 'REJECTED') {
        reason = window.prompt("Please provide a reason for rejecting this KYC application:");
        if (!reason) return; // User cancelled prompt
      }
      
      await userService.updateKYCStatus(userId, action, reason);
      // Refresh list
      fetchSubmissions();
      setSelectedDoc(null);
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
          <h2>KYC Review Queue</h2>
          <button onClick={() => navigate('/')} className="back-btn">
            Back to Home
          </button>
        </div>
        
        {submissions.length === 0 ? (
          <div className="no-submissions">
            <p>No pending KYC submissions</p>
          </div>
        ) : (
          <div className="kyc-list">
            {submissions.map(submission => (
              <div key={submission.user_id} className="kyc-item">
                <div className="kyc-info">
                  <h3>{submission.full_name}</h3>
                  <p>User ID: {submission.user_id}</p>
                  <p>Phone: {submission.phone || 'Not provided'}</p>
                  <p>Submitted: {new Date(submission.created_at).toLocaleDateString()}</p>
                </div>
                <div className="kyc-actions">
                  <button 
                    onClick={() => handleReview(submission.user_id, 'VERIFIED')}
                    className="action-btn approve"
                  >
                    ✓ Approve
                  </button>
                  <button 
                    onClick={() => handleReview(submission.user_id, 'REJECTED')}
                    className="action-btn reject"
                  >
                    ✗ Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminKYC;