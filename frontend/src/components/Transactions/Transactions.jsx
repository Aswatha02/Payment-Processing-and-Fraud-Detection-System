import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Transactions.css';

const Transactions = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    // Simulate fetching transactions
    // In real implementation, call your payment service API
    setTimeout(() => {
      setTransactions([
        {
          id: 'TXN001',
          date: '2024-03-20',
          amount: 1500.00,
          status: 'completed',
          type: 'payment',
          recipient: 'John Doe',
          description: 'Payment for services'
        },
        {
          id: 'TXN002',
          date: '2024-03-19',
          amount: 250.50,
          status: 'pending',
          type: 'payment',
          recipient: 'Jane Smith',
          description: 'Subscription payment'
        },
        {
          id: 'TXN003',
          date: '2024-03-18',
          amount: 5000.00,
          status: 'completed',
          type: 'transfer',
          recipient: 'Business Corp',
          description: 'Invoice payment'
        },
        {
          id: 'TXN004',
          date: '2024-03-17',
          amount: 75.00,
          status: 'failed',
          type: 'payment',
          recipient: 'Service Provider',
          description: 'Failed transaction'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return '#27ae60';
      case 'pending': return '#f39c12';
      case 'failed': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  const getStatusText = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const filteredTransactions = transactions.filter(t => 
    filter === 'all' ? true : t.status === filter
  );

  if (loading) {
    return (
      <div className="transactions-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="transactions-container">
      <div className="transactions-card">
        <div className="transactions-header">
          <h2>Transaction History</h2>
          <button onClick={() => navigate('/payment')} className="new-payment-btn">
            + New Payment
          </button>
        </div>
        
        <div className="filter-bar">
          <button 
            className={filter === 'all' ? 'active' : ''} 
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={filter === 'completed' ? 'active' : ''} 
            onClick={() => setFilter('completed')}
          >
            Completed
          </button>
          <button 
            className={filter === 'pending' ? 'active' : ''} 
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
          <button 
            className={filter === 'failed' ? 'active' : ''} 
            onClick={() => setFilter('failed')}
          >
            Failed
          </button>
        </div>
        
        <div className="transactions-list">
          {filteredTransactions.length === 0 ? (
            <div className="no-transactions">
              <p>No transactions found</p>
            </div>
          ) : (
            filteredTransactions.map(txn => (
              <div key={txn.id} className="transaction-item">
                <div className="transaction-details">
                  <div className="transaction-icon">
                    {txn.type === 'payment' ? '💰' : '💸'}
                  </div>
                  <div className="transaction-info">
                    <div className="transaction-title">{txn.description}</div>
                    <div className="transaction-meta">
                      {txn.recipient} • {new Date(txn.date).toLocaleDateString()}
                    </div>
                    <div className="transaction-id">ID: {txn.id}</div>
                  </div>
                </div>
                <div className="transaction-right">
                  <div className="transaction-amount">
                    -${txn.amount.toFixed(2)}
                  </div>
                  <div 
                    className="transaction-status"
                    style={{ color: getStatusColor(txn.status) }}
                  >
                    {getStatusText(txn.status)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        
        <div className="transactions-footer">
          <button onClick={() => navigate('/')} className="back-btn">
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default Transactions;