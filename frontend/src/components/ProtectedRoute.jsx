import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute = () => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return user ? <Outlet /> : <Navigate to="/login" />;
};

export const VerificationRoute = () => {
  const { user, loading, isVerified } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (user && !isVerified()) {
    return <Outlet />;
  }
  
  return <Navigate to="/profile" />;
};

export const PublicRoute = () => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return !user ? <Outlet /> : <Navigate to="/profile" />;
};