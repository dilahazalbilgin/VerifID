import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from '../../styles/ProfilePage.module.scss';
import Navbar from '../../components/Navbar';

function ProfilePage() {
  const { user, updateProfile, loading } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    idCardNumber: '',
    birthDate: '',
    serialNumber: '',
    gender: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Update form data when user data changes
    if (user) {
      console.log("User data loaded:", user); // Debug log
      setFormData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.email || '',
        idCardNumber: user.idCardNumber || '',
        birthDate: user.birthDate ? new Date(user.birthDate).toISOString().split('T')[0] : '',
        serialNumber: user.serialNumber || '',
        gender: user.gender || '',
        password: '',
        confirmPassword: ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Validate password if provided
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password && formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    setIsLoading(true);
    
    try {
      console.log("Submitting data:", formData); // Debug log
      
      // Prepare data for update (exclude confirmPassword)
      const updateData = {
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        idCardNumber: formData.idCardNumber,
        birthDate: formData.birthDate,
        serialNumber: formData.serialNumber,
        gender: formData.gender
      };
      
      // Only include password if it was provided
      if (formData.password) {
        updateData.password = formData.password;
      }
      
      // Call the updateProfile function from AuthContext with all fields
      await updateProfile(updateData);
      
      setSuccess('Profile updated successfully');
      setIsEditing(false);
      
      // Clear password fields after successful update
      setFormData(prev => ({
        ...prev,
        password: '',
        confirmPassword: ''
      }));
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset form data to original user data
    if (user) {
      setFormData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.email || '',
        idCardNumber: user.idCardNumber || '',
        birthDate: user.birthDate ? new Date(user.birthDate).toISOString().split('T')[0] : '',
        serialNumber: user.serialNumber || '',
        gender: user.gender || '',
        password: '',
        confirmPassword: ''
      });
    }
    setIsEditing(false);
    setError('');
    setSuccess('');
  };

  if (loading) {
    return <div className={styles.loadingContainer}>Loading user data...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return (
    <div className={styles.pageContainer}>
      <Navbar />
      <div className={styles.profileContainer}>
        <div className={styles.profileHeader}>
          <h1>My Profile</h1>
          <p className={styles.subtitle}>Manage your personal information</p>
          {error && <p className={styles.errorMessage}>{error}</p>}
          {success && <p className={styles.successMessage}>{success}</p>}
          
          <div className={styles.verificationBadge}>
            <span className={user.isVerified ? styles.verified : styles.unverified}>
              {user.isVerified ? 'Verified' : 'Not Verified'}
            </span>
            {!user.isVerified && (
              <button
                onClick={() => navigate('/verify')}
                className={styles.verifyButton}
              >
                Verify
              </button>
            )}
          </div>

          {/* Request ID Section */}
          <div className={styles.requestIdSection}>
            <h3>Request ID</h3>
            <p className={styles.requestIdDescription}>
              Use this ID to verify your identity with third-party applications
            </p>
            <div className={styles.requestIdContainer}>
              <code className={styles.requestIdCode}>
                {user.requestId || 'No Request ID available'}
              </code>
              {user.requestId && (
                <button
                  onClick={() => navigator.clipboard.writeText(user.requestId)}
                  className={styles.copyButton}
                  title="Copy to clipboard"
                >
                  Copy
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div className={styles.profileContent}>
          <div className={styles.personalInfo}>
            <div className={styles.sectionHeader}>
              <h3>Personal Information</h3>
              {!isEditing ? (
                <button 
                  onClick={() => setIsEditing(true)}
                  className={styles.editButton}
                >
                  Edit
                </button>
              ) : (
                <div className={styles.editActions}>
                  <button 
                    onClick={handleCancel}
                    className={styles.cancelButton}
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleSubmit}
                    className={styles.saveButton}
                    disabled={isLoading}
                  >
                    {isLoading ? 'Saving...' : 'Save'}
                  </button>
                </div>
              )}
            </div>
            
            <form className={styles.profileForm} onSubmit={handleSubmit}>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>First Name</label>
                  {isEditing ? (
                    <input 
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <p>{formData.firstName || 'Not provided'}</p>
                  )}
                </div>
                
                <div className={styles.formGroup}>
                  <label>Last Name</label>
                  {isEditing ? (
                    <input 
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <p>{formData.lastName || 'Not provided'}</p>
                  )}
                </div>
              </div>
              
              <div className={styles.formGroup}>
                <label>Email</label>
                {isEditing ? (
                  <input 
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                ) : (
                  <p>{formData.email || 'Not provided'}</p>
                )}
              </div>
              
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>ID Card Number</label>
                  {isEditing ? (
                    <input 
                      type="text"
                      name="idCardNumber"
                      value={formData.idCardNumber}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <p>{formData.idCardNumber || 'Not provided'}</p>
                  )}
                </div>
                
                <div className={styles.formGroup}>
                  <label>Serial Number</label>
                  {isEditing ? (
                    <input 
                      type="text"
                      name="serialNumber"
                      value={formData.serialNumber}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <p>{formData.serialNumber || 'Not provided'}</p>
                  )}
                </div>
              </div>
              
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Birth Date</label>
                  {isEditing ? (
                    <input 
                      type="date"
                      name="birthDate"
                      value={formData.birthDate}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <p>{formData.birthDate ? new Date(formData.birthDate).toLocaleDateString() : 'Not provided'}</p>
                  )}
                </div>
                
                <div className={styles.formGroup}>
                  <label>Gender</label>
                  {isEditing ? (
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      disabled={isLoading}
                      className={styles.selectInput}
                    >
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                  ) : (
                    <p>{formData.gender ? formData.gender.charAt(0).toUpperCase() + formData.gender.slice(1) : 'Not provided'}</p>
                  )}
                </div>
              </div>
              
              {isEditing && (
                <div className={styles.securitySection}>
                  <h4 className={styles.securityTitle}>Change Password</h4>
                  <p className={styles.securityNote}>Leave blank to keep current password</p>
                  
                  <div className={styles.formRow}>
                    <div className={styles.formGroup}>
                      <label>New Password</label>
                      <input 
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        disabled={isLoading}
                        placeholder="Minimum 6 characters"
                      />
                    </div>
                    
                    <div className={styles.formGroup}>
                      <label>Confirm Password</label>
                      <input 
                        type="password"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        disabled={isLoading}
                        placeholder="Confirm new password"
                      />
                    </div>
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;




