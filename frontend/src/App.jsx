import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, VerificationRoute, PublicRoute } from './components/ProtectedRoute';

// Pages
import HomePage from './pages/homePage/Home.jsx';
import RegisterPage from './pages/registerPage/Register.jsx';
import LoginPage from './pages/loginPage/Login.jsx';
import ProfilePage from './pages/profilePage/Profile.jsx';
import IDCardVerification from './pages/verificationPage/IDCardVerification.jsx';
import VideoVerification from './pages/verificationPage/VideoVerification.jsx';
import NotFound from './pages/NotFound.jsx';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          
          {/* Public routes - only accessible when not logged in */}
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
          
          {/* Verification routes - only accessible when logged in but not verified */}
          <Route element={<VerificationRoute />}>
            <Route path="/verify" element={<IDCardVerification />} />
            <Route path="/video-verification" element={<VideoVerification />} />
          </Route>
          
          {/* Protected routes - only accessible when logged in */}
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
          
          {/* 404 route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

