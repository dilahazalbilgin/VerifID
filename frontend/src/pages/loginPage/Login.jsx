import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from '../../styles/LoginPage.module.scss';
import Navbar from '../../components/Navbar';
import verificationImage from '../../assets/verification-image.jpg';

function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Check for success message from registration
  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      // Clear the message from location state
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Required fields validation
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    
    // Email format validation
    const emailRegex = /^\S+@\S+\.\S+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Call the login function from AuthContext
      const userData = await login(formData.email, formData.password);
      
      // Redirect to verification if not verified, otherwise to profile
      if (!userData.isVerified) {
        navigate('/verify');
      } else {
        navigate('/profile');
      }
    } catch (err) {
      setErrors({ general: err.message || 'Invalid email or password' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <Navbar />
      <div className={styles.loginContainer}>
        <div className={styles.imageSection}>
          <img 
            src={verificationImage} 
            alt="Identity Verification" 
            className={styles.verificationImage}
          />
        </div>
        
        <div className={styles.formSection}>
          <h1>Welcome Back</h1>
          <p className={styles.subtitle}>Log in to your VerifID account</p>
          
          {successMessage && (
            <p className={styles.successMessage}>{successMessage}</p>
          )}
          
          {errors.general && <p className={styles.errorMessage}>{errors.general}</p>}
          
          <form onSubmit={handleSubmit} className={styles.loginForm}>
            <div className={styles.formGroup}>
              <label htmlFor="email">Email</label>
              <input 
                type="email" 
                id="email" 
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? styles.inputError : ''}
                disabled={isLoading}
              />
              {errors.email && <p className={styles.fieldError}>{errors.email}</p>}
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="password">Password</label>
              <input 
                type="password" 
                id="password" 
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={errors.password ? styles.inputError : ''}
                disabled={isLoading}
              />
              {errors.password && <p className={styles.fieldError}>{errors.password}</p>}
            </div>
            
            <div className={styles.forgotPassword}>
              <a href="/forgot-password">Forgot password?</a>
            </div>
            
            <button 
              type="submit" 
              className={styles.loginBtn}
              disabled={isLoading}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
            
            <p className={styles.registerLink}>
              Don't have an account? <Link to="/register">Register here</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;



