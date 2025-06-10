import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from '../../styles/RegisterPage.module.scss';
import Navbar from '../../components/Navbar';
import verificationImage from '../../assets/register.png';

function RegisterPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    idCardNumber: '',
    email: '',
    password: '',
    confirmPassword: '',
    birthDate: '',
    serialNumber: '',
    gender: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

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
    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (!formData.idCardNumber.trim()) newErrors.idCardNumber = 'ID Card Number is required';
    if (!formData.serialNumber.trim()) newErrors.serialNumber = 'Serial Number is required';
    if (!formData.birthDate) newErrors.birthDate = 'Birth date is required';
    
    // Email format validation
    const emailRegex = /^\S+@\S+\.\S+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    // Password validation
    if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    // Password confirmation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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
      // Remove confirmPassword before sending to API
      const { confirmPassword, ...registrationData } = formData;
      
      // Call the register function from AuthContext
      await register(registrationData);
      
      // Redirect to login page instead of verification
      navigate('/login', { state: { message: 'Registration successful! Please log in.' } });
    } catch (err) {
      setErrors({ general: err.message || 'Registration failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <Navbar />
      <div className={styles.registerContainer}>
        <div className={styles.imageSection}>
          <img 
            src={verificationImage} 
            alt="Identity Verification" 
            className={styles.verificationImage}
          />
        </div>
        
        <div className={styles.formSection}>
          <h1>Create Your Account</h1>
          <p className={styles.subtitle}>Join VerifID for secure identity verification</p>
          
          {errors.general && <p className={styles.errorMessage}>{errors.general}</p>}
          
          <form onSubmit={handleSubmit} className={styles.registerForm}>
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="firstName">First Name*</label>
                <input 
                  type="text" 
                  id="firstName" 
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className={errors.firstName ? styles.inputError : ''}
                  disabled={isLoading}
                />
                {errors.firstName && <p className={styles.fieldError}>{errors.firstName}</p>}
              </div>
              
              <div className={styles.formGroup}>
                <label htmlFor="lastName">Last Name*</label>
                <input 
                  type="text" 
                  id="lastName" 
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className={errors.lastName ? styles.inputError : ''}
                  disabled={isLoading}
                />
                {errors.lastName && <p className={styles.fieldError}>{errors.lastName}</p>}
              </div>
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="email">Email*</label>
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
            
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="password">Password*</label>
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
              
              <div className={styles.formGroup}>
                <label htmlFor="confirmPassword">Confirm Password*</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className={errors.confirmPassword ? styles.inputError : ''}
                  disabled={isLoading}
                />
                {errors.confirmPassword && <p className={styles.fieldError}>{errors.confirmPassword}</p>}
              </div>
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="idCardNumber">ID Card Number*</label>
              <input 
                type="text" 
                id="idCardNumber" 
                name="idCardNumber"
                value={formData.idCardNumber}
                onChange={handleChange}
                className={errors.idCardNumber ? styles.inputError : ''}
                disabled={isLoading}
              />
              {errors.idCardNumber && <p className={styles.fieldError}>{errors.idCardNumber}</p>}
            </div>
            
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="serialNumber">Serial Number*</label>
                <input 
                  type="text" 
                  id="serialNumber" 
                  name="serialNumber"
                  value={formData.serialNumber}
                  onChange={handleChange}
                  className={errors.serialNumber ? styles.inputError : ''}
                  disabled={isLoading}
                />
                {errors.serialNumber && <p className={styles.fieldError}>{errors.serialNumber}</p>}
              </div>
              
              <div className={styles.formGroup}>
                <label htmlFor="birthDate">Birth Date*</label>
                <input 
                  type="date" 
                  id="birthDate" 
                  name="birthDate"
                  value={formData.birthDate}
                  onChange={handleChange}
                  className={errors.birthDate ? styles.inputError : ''}
                  disabled={isLoading}
                />
                {errors.birthDate && <p className={styles.fieldError}>{errors.birthDate}</p>}
              </div>
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="gender">Gender</label>
              <select 
                id="gender" 
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                disabled={isLoading}
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
              {errors.gender && <p className={styles.fieldError}>{errors.gender}</p>}
            </div>
            
            <button 
              type="submit" 
              className={styles.registerBtn}
              disabled={isLoading}
            >
              {isLoading ? 'Registering...' : 'Register'}
            </button>
            
            <p className={styles.loginLink}>
              Already have an account? <Link to="/login">Login here</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;




