import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import walletService from '../../services/walletService';
import NotificationBell from '../Notifications/NotificationBell';
import './WalletDashboard.css';

const WalletDashboard = () => {
  const navigate = useNavigate();
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Modal state
  const [modalType, setModalType] = useState(null); // 'deposit', 'withdraw', 'transfer'
  const [amount, setAmount] = useState('');
  const [recipient, setRecipient] = useState('');
  const [actionError, setActionError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user'));
      if (!user) {
        navigate('/login');
        return;
      }
      
      const balanceData = await walletService.getBalance(user.id);
      setBalance(balanceData.balance);
      
      const txData = await walletService.getTransactions(user.id);
      setTransactions(txData.transactions);
      
    } catch (err) {
      console.error('Failed to load wallet data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setActionError('');
    
    try {
      const user = JSON.parse(localStorage.getItem('user'));
      
      if (modalType === 'deposit') {
        await walletService.deposit(user.id, amount);
      } else if (modalType === 'withdraw') {
        await walletService.withdraw(user.id, amount);
      } else if (modalType === 'transfer') {
        await walletService.transfer(user.id, recipient, amount);
      }
      
      // Refresh Data & Close Modal
      setModalType(null);
      setAmount('');
      setRecipient('');
      fetchWalletData();
      
    } catch (err) {
      setActionError(err.detail || 'Transaction failed');
    } finally {
      setActionLoading(false);
    }
  };

  const closeModal = () => {
    setModalType(null);
    setAmount('');
    setRecipient('');
    setActionError('');
  };

  if (loading) {
    return (
      <div className="wallet-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="wallet-container">
      <div className="wallet-card">
        
        <div className="wallet-header">
          <h2>My Wallet</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <NotificationBell />
            <button onClick={() => navigate('/')} className="back-btn">
              Back to Home
            </button>
          </div>
        </div>
        
        <div className="balance-section">
          <h3>Current Balance</h3>
          <div className="balance-amount">${balance.toFixed(2)}</div>
          
          <div className="action-buttons">
            <button onClick={() => setModalType('deposit')} className="wallet-btn deposit">
              Deposit
            </button>
            <button onClick={() => setModalType('withdraw')} className="wallet-btn withdraw">
              Withdraw
            </button>
            <button onClick={() => setModalType('transfer')} className="wallet-btn transfer">
              Transfer
            </button>
          </div>
        </div>

        <div className="transactions-section">
          <h3>Recent Transactions</h3>
          {transactions.length === 0 ? (
            <div className="no-transactions"><p>No transactions found</p></div>
          ) : (
            <div className="transactions-list">
              {transactions.map((tx) => {
                const user = JSON.parse(localStorage.getItem('user'));
                const userId = user ? user.id : 0;
                
                // Determine type and description based on Transaction model
                let txType = tx.type || 'unknown';
                let txDesc = tx.description || 'Transaction';
                
                // Unified Phase 2 format handling
                if (tx.type === 'transfer') {
                  if (tx.sender_id === userId) {
                    txType = 'debit';
                    txDesc = `Transfer to ${tx.receiver_name || `User ${tx.receiver_id}`}`;
                  } else if (tx.receiver_id === userId) {
                    txType = 'credit';
                    txDesc = `Transfer from ${tx.sender_name || `User ${tx.sender_id}`}`;
                  }
                } else if (!tx.type) {
                  // Legacy Transaction Service format
                  if (tx.sender_id === userId) {
                    txType = 'debit';
                    txDesc = `Transfer to User ${tx.receiver_id}`;
                  } else if (tx.receiver_id === userId) {
                    txType = 'credit';
                    txDesc = `Transfer from User ${tx.sender_id}`;
                  }
                } else {
                   // Legacy system credit/debit format (Deposits/Withdrawals)
                   txDesc = tx.description || (txType === 'credit' ? 'Deposit' : 'Withdrawal');
                }
                
                const isCredit = txType === 'credit';

                return (
                <div key={tx.id} className="tx-item">
                  <div className="tx-info">
                    <span className="tx-type">{txType.toUpperCase()}</span>
                    <span className="tx-desc">{txDesc}</span>
                    <span className="tx-date">{new Date(tx.timestamp).toLocaleString()}</span>
                  </div>
                  <div className={`tx-amount ${isCredit ? 'positive' : 'negative'}`}>
                    {isCredit ? '+' : '-'}${tx.amount.toFixed(2)}
                  </div>
                </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Action Modal */}
      {modalType && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>
              {modalType === 'deposit' && 'Deposit Funds'}
              {modalType === 'withdraw' && 'Withdraw Funds'}
              {modalType === 'transfer' && 'Transfer Funds'}
            </h3>
            
            <form onSubmit={handleAction}>
              {modalType === 'transfer' && (
                <div className="form-group">
                  <label>Recipient User ID</label>
                  <input
                    type="number"
                    value={recipient}
                    onChange={(e) => setRecipient(e.target.value)}
                    required
                    placeholder="Enter Recipient ID"
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>Amount ($)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  step="0.01"
                  min="0.01"
                  required
                  placeholder="0.00"
                />
              </div>
              
              {actionError && <div className="error-message">{actionError}</div>}
              
              <div className="button-group">
                <button type="submit" className="wallet-btn" disabled={actionLoading}>
                  {actionLoading ? 'Processing...' : 'Confirm'}
                </button>
                <button type="button" onClick={closeModal} className="wallet-btn secondary">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalletDashboard;
