import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Profile from './components/Auth/Profile';
import Home from './components/Home/Home';
import KYCSubmit from './components/Profile/KYCSubmit';
import Transactions from './components/Transactions/Transactions';
import Payment from './components/Payment/Payment';
import AdminUsers from './components/Admin/AdminUsers';
import AdminKYC from './components/Admin/AdminKYC';
import './App.css';

const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

const PrivateRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Profile Routes */}
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          
          {/* KYC Routes */}
          <Route path="/kyc-submit" element={<PrivateRoute><KYCSubmit /></PrivateRoute>} />
          
          {/* Payment Routes */}
          <Route path="/transactions" element={<PrivateRoute><Transactions /></PrivateRoute>} />
          <Route path="/payment" element={<PrivateRoute><Payment /></PrivateRoute>} />
          
          {/* Admin Routes */}
          <Route path="/admin/users" element={<PrivateRoute><AdminUsers /></PrivateRoute>} />
          <Route path="/admin/kyc" element={<PrivateRoute><AdminKYC /></PrivateRoute>} />
          
          {/* Home */}
          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;