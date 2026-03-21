import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Payment.css';

const Payment = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    recipient: '',
    amount: '',
    description: '',
    payment_method: 'card'
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
    
    if (!formData.recipient || !formData.amount) {
      setError('Please fill in all required fields');
      return;
    }
    
    if (parseFloat(formData.amount) <= 0) {
      setError('Amount must be greater than 0');
      return;
    }
    
    setLoading(true);
    
    // Simulate payment processing
    setTimeout(() => {
      setLoading(false);
      navigate('/transactions');
    }, 2000);
  };

  return (
    <div className="payment-container">
      <div className="payment-card fade-in">
        <div className="payment-header">
          <h2>New Payment</h2>
          <p>Send money securely</p>
        </div>
        
        <div className="payment-content">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Recipient *</label>
              <input
                type="text"
                name="recipient"
                value={formData.recipient}
                onChange={handleChange}
                placeholder="Enter recipient name or email"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Amount *</label>
              <div className="amount-input">
                <span className="currency">$</span>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  placeholder="0.00"
                  step="0.01"
                  min="0.01"
                  required
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="What's this for?"
                rows="3"
              />
            </div>
            
            <div className="form-group">
              <label>Payment Method</label>
              <select name="payment_method" value={formData.payment_method} onChange={handleChange}>
                <option value="card">Credit/Debit Card</option>
                <option value="bank">Bank Transfer</option>
                <option value="wallet">Digital Wallet</option>
              </select>
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="button-group">
              <button type="submit" className="payment-btn" disabled={loading}>
                {loading ? 'Processing...' : `Pay $${formData.amount || '0.00'}`}
              </button>
              <button 
                type="button" 
                onClick={() => navigate('/')} 
                className="payment-btn secondary"
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

export default Payment;