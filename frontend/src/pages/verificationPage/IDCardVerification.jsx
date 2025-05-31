import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from '../../styles/VerificationPage.module.scss'
import Navbar from '../../components/Navbar'
import verificationImage from '../../assets/verification-image.jpg'
import { useAuth } from '../../context/AuthContext'

function IDCardVerification() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [verificationStatus, setVerificationStatus] = useState(null)
  const [matchDetails, setMatchDetails] = useState(null)
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };
  
  const handleVerifyIDCard = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    
    setIsUploading(true);
    setVerificationStatus(null);
    setMatchDetails(null);
    
    // Create form data to send to backend
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    // Add comprehensive user data if available
    if (user) {
      formData.append('userData', JSON.stringify({
        id: user.id, // Add user ID for face image storage
        name: user.firstName,
        surname: user.lastName,
        idCardNumber: user.idCardNumber || '',
        gender: user.gender || ''
      }));
    }
    
    try {
      // Direct request to Flask backend
      const response = await fetch('http://127.0.0.1:5001/verify/id', {
        method: 'POST',
        mode: 'cors',
        body: formData
      });
      
      const result = await response.json();
      console.log('Verification result:', result);
      
      if (result.success) {
        // Set match details for display
        if (result.user_match) {
          setMatchDetails({
            percentage: result.user_match.match_percentage,
            matches: result.user_match.matches,
            overall: result.user_match.overall_match
          });
        }
        
        // Set verification status based on match
        if (result.user_match && result.user_match.overall_match) {
          setVerificationStatus('success');
          
          // Store verification ID and face image for next step
          localStorage.setItem('verificationId', result.verification_id);
          if (result.face_image) {
            localStorage.setItem('idCardFace', result.face_image);
          }
          
          // Navigate to video verification with state after a delay
          setTimeout(() => {
            navigate('/video-verification', { 
              state: { 
                verificationId: result.verification_id,
                faceImage: result.face_image,
                matchDetails: result.user_match
              } 
            });
          }, 2000);
        } else {
          setVerificationStatus('warning');
        }
      } else {
        setVerificationStatus('error');
        console.error('Verification failed:', result.message);
      }
    } catch (error) {
      setVerificationStatus('error');
      console.error('Error during verification:', error);
    } finally {
      setIsUploading(false);
    }
  };
  
  return (
    <div className={styles.pageContainer}>
      <Navbar />
      <div className={styles.verificationContainer}>
        <div className={styles.imageSection}>
          <img 
            src={verificationImage} 
            alt="Identity Verification" 
            className={styles.verificationImage}
          />
        </div>
        
        <div className={styles.formSection}>
          <h1>Verify Your Identity</h1>
          <p className={styles.subtitle}>Step 1: Upload a photo of your ID card</p>
          
          <form onSubmit={handleVerifyIDCard} className={styles.verificationForm}>
            <div className={styles.fileUpload}>
              {previewUrl ? (
                <div className={styles.previewContainer}>
                  <img src={previewUrl} alt="ID Card Preview" className={styles.preview} />
                  <button 
                    type="button" 
                    className={styles.changeButton}
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl(null);
                    }}
                  >
                    <i className="fas fa-sync-alt"></i> Change
                  </button>
                </div>
              ) : (
                <div className={styles.uploadContainer}>
                  <input 
                    type="file" 
                    id="id-card" 
                    accept="image/*" 
                    onChange={handleFileChange}
                    className={styles.fileInput}
                  />
                  <label htmlFor="id-card" className={styles.uploadLabel}>
                    <div className={styles.uploadIcon}>
                      <i className="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div className={styles.uploadText}>
                      Click to upload or drag and drop
                    </div>
                    <div className={styles.uploadHint}>
                      JPG, PNG or PDF (max 10MB)
                    </div>
                  </label>
                </div>
              )}
            </div>
            
            {matchDetails && (
              <div className={styles.matchDetails}>
                <h3>Match Results:</h3>
                <div className={styles.matchPercentage}>
                  <span className={styles.percentValue}>
                    {matchDetails.percentage.toFixed(1)}%
                  </span>
                  <span className={styles.percentLabel}>
                    Match
                  </span>
                </div>
                <ul className={styles.matchList}>
                  {matchDetails.matches.map(([field, matched], index) => (
                    <li key={index} className={matched ? styles.matched : styles.unmatched}>
                      <span className={styles.fieldName}>
                        {field === "idCardNumber" ? "ID Card Number" : 
                         field === "name" ? "First Name" :
                         field === "surname" ? "Last Name" :
                         field === "gender" ? "Gender" : field}
                      </span>
                      <span className={styles.matchIcon}>
                        {matched ? <i className="fas fa-check-circle"></i> : <i className="fas fa-times-circle"></i>}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <button 
              type="submit" 
              className={`${styles.verifyButton} ${isUploading ? styles.loading : ''}`}
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i> Processing...
                </>
              ) : (
                <>
                  <i className="fas fa-id-card"></i> Verify ID Card
                </>
              )}
            </button>
            
            {verificationStatus === 'success' && (
              <div className={styles.statusMessage + ' ' + styles.successMessage}>
                <i className="fas fa-check-circle"></i>
                <span>ID verified successfully! Proceeding to face verification...</span>
              </div>
            )}
            
            {verificationStatus === 'warning' && (
              <div className={styles.statusMessage + ' ' + styles.warningMessage}>
                <i className="fas fa-exclamation-triangle"></i>
                <span>ID verification partially successful. Please check the match details.</span>
              </div>
            )}
            
            {verificationStatus === 'error' && (
              <div className={styles.statusMessage + ' ' + styles.errorMessage}>
                <i className="fas fa-times-circle"></i>
                <span>ID verification failed. Please try again with a clearer image.</span>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

export default IDCardVerification










