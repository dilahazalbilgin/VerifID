import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from '../../styles/VerificationPage.module.scss';
import Navbar from '../../components/Navbar';
import verificationImage from '../../assets/verification-image.jpg';
import { useAuth } from '../../context/AuthContext';

function IDCardVerification() {
  const { user } = useAuth();
  console.log(user);
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [matchDetails, setMatchDetails] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  
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
    setExtractedData(null);
    
    // Create form data to send to backend
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    // Add comprehensive user data if available
    if (user) {
      const userData = {
        id: user.id, // Keep user ID if needed for backend logging/tracking
        // Removed name and surname as per new backend matching
        // name: user.firstName,
        // surname: user.lastName,
        idNumber: user.idCardNumber || '', // Changed from idCardNumber to idNumber
        gender: user.gender || '',
        serialNumber: user.serialNumber || '', // Added serialNumber
        birthDate: user.birthDate || '' // Added birthDate
      };
      
      console.log('Sending user data:', userData);
      formData.append('userData', JSON.stringify(userData));
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
        // Store extracted data for display
        if (result.extracted_data) {
          setExtractedData(result.extracted_data);
        }
        
        // Set match details for display
        if (result.user_match) {
          console.log('Match details:', result.user_match);
          
          // Ensure we have a valid matches array
          const matches = Array.isArray(result.user_match.matches) 
            ? result.user_match.matches 
            : [];
            
          setMatchDetails({
            percentage: result.user_match.match_percentage || 0,
            matches: matches,
            overall: result.user_match.overall_match || false
          });
          
          // Log each match for debugging
          matches.forEach(match => {
            console.log(`Match field: ${match[0]}, matched: ${match[1]}`);
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
  
  // Helper function to format field names for display
  const formatFieldName = (field) => {
    switch(field) {
      case 'idNumber': return 'ID Number (User Data)'; // For frontend sent data
      case 'id_number': return 'ID Number (Extracted)'; // For backend extracted data
      case 'name': return 'First Name';
      case 'surname': return 'Last Name';
      case 'gender': return 'Gender';
      case 'birthDate': return 'Birth Date (User Data)'; // For frontend sent data
      case 'birth_date': return 'Birth Date (Extracted)'; // For backend extracted data
      case 'serialNumber': return 'Serial Number (User Data)'; // For frontend sent data
      case 'serial_number': return 'Serial Number (Extracted)'; // For backend extracted data
      case 'nationality': return 'Nationality';
      case 'expiry_date': return 'Expiry Date';
      default: return field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
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
            
            {/* Display extracted data if available */}
            {extractedData && (
              <div className={styles.extractedData}>
                <h3>Extracted Information:</h3>
                <div className={styles.dataGrid}>
                  {Object.entries(extractedData).map(([key, value]) => (
                    value !== "(bulunamadı)" && (
                      <div key={key} className={styles.dataItem}>
                        <span className={styles.dataLabel}>{formatFieldName(key)}:</span>
                        <span className={styles.dataValue}>{value}</span>
                      </div>
                    )
                  ))}
                </div>
              </div>
            )}
            
            {/* Display match details if available */}
            {matchDetails && matchDetails.matches.length > 0 && (
              <div className={styles.matchDetails}>
                <h3>Match Results</h3>
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
                        {formatFieldName(field)}
                      </span>
                      <span className={styles.matchIcon}>
                        {matched ? 
                          <i className="fas fa-check-circle"></i> : 
                          <i className="fas fa-times-circle"></i>
                        }
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

export default IDCardVerification;

