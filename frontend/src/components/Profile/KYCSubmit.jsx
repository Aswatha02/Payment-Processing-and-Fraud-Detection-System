import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/userService';
import './Profile.css';

const KYCSubmit = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    id_type: 'passport',
    id_number: '',
    document: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      document: e.target.files[0]
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.id_number) {
      setError('Please enter your ID number');
      return;
    }
    
    if (!formData.document) {
      setError('Please upload a document');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Update KYC status to SUBMITTED
      const user = JSON.parse(localStorage.getItem('user'));
      await userService.updateKYCStatus(user.id, 'SUBMITTED');
      
      setSuccess('KYC documents submitted successfully! Our team will review them shortly.');
      
      // Redirect after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err) {
      setError(err.detail || 'Failed to submit KYC documents');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-container">
      <div className="profile-card fade-in">
        <div className="profile-header">
          <h2>KYC Verification</h2>
          <p>Submit your documents for verification</p>
        </div>
        
        <div className="profile-content">
          <div className="info-banner">
            <span className="info-icon">ℹ️</span>
            <span>Please upload a clear image of your government-issued ID</span>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>ID Type</label>
              <select name="id_type" value={formData.id_type} onChange={handleChange}>
                <option value="passport">Passport</option>
                <option value="drivers_license">Driver's License</option>
                <option value="national_id">National ID Card</option>
                <option value="voter_id">Voter ID</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>ID Number</label>
              <input
                type="text"
                name="id_number"
                value={formData.id_number}
                onChange={handleChange}
                placeholder="Enter your ID number"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Upload Document</label>
              <input
                type="file"
                name="document"
                onChange={handleFileChange}
                accept="image/*,.pdf"
                required
              />
              <small className="hint">Accepted formats: JPG, PNG, PDF (Max 5MB)</small>
            </div>
            
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            
            <div className="button-group">
              <button type="submit" className="auth-btn" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit KYC'}
              </button>
              <button 
                type="button" 
                onClick={() => navigate('/')} 
                className="auth-btn secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default KYCSubmit;