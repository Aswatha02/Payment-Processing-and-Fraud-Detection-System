import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Profile from './components/Auth/Profile';
import Home from './components/Home/Home';
import KYCSubmit from './components/Profile/KYCSubmit';
import WalletDashboard from './components/Wallet/WalletDashboard';
import AdminUsers from './components/Admin/AdminUsers';
import AdminKYC from './components/Admin/AdminKYC';
import AdminLogin from './components/Auth/AdminLogin';
import AdminRegister from './components/Auth/AdminRegister';
import './App.css';

const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

const isAdmin = () => {
  if (!isAuthenticated()) return false;
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.role === 'ADMIN';
  } catch (e) {
    return false;
  }
};

const PrivateRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

const AdminRoute = ({ children }) => {
  return isAdmin() ? children : <Navigate to="/" />;
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
          
          {/* Wallet Dashboard Route */}
          <Route path="/wallet" element={<PrivateRoute><WalletDashboard /></PrivateRoute>} />
          
          {/* Admin Routes */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin/register" element={<AdminRegister />} />
          <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
          <Route path="/admin/kyc" element={<AdminRoute><AdminKYC /></AdminRoute>} />
          
          {/* Home */}
          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;