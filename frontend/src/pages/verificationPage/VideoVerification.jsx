import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { io } from 'socket.io-client';
import './VideoVerification.scss';
import Navbar from '../../components/Navbar';

const VideoVerification = () => {
  const { user, updateProfile } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const videoRef = useRef(null);
  const socketRef = useRef(null);
  const streamRef = useRef(null);
  
  const [status, setStatus] = useState('initializing');
  const [instruction, setInstruction] = useState('');
  const [message, setMessage] = useState('');
  const [verificationId, setVerificationId] = useState('');
  const [referenceFace, setReferenceFace] = useState(null);
  
  // Get verification ID from location state or previous step
  useEffect(() => {
    const initVerification = async () => {
      try {
        // Check if we have a verification ID from the previous step
        let id = null;
        let needsNewId = true;
        
        if (location.state?.verificationId) {
          console.log("Found verification ID in state:", location.state.verificationId);
          id = location.state.verificationId;
          
          // Validate the ID
          const checkResponse = await fetch(`http://localhost:5001/api/verify/face/check/${id}`);
          const checkResult = await checkResponse.json();
          
          if (checkResult.valid) {
            console.log("Verification ID is valid:", id);
            setVerificationId(id);
            setStatus('ready');
            needsNewId = false;
          } else {
            console.log("Verification ID is invalid, will create new one");
          }
        }
        
        if (needsNewId) {
          console.log("Initializing new verification for user:", user.id);
          // Initialize verification if no ID provided or invalid
          const response = await fetch('http://localhost:5001/api/verify/face/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              session_id: user.id,
              user_id: user.id
            })
          });
          
          const data = await response.json();
          if (data.verification_id) {
            console.log("Received new verification ID:", data.verification_id);
            setVerificationId(data.verification_id);
            setStatus('ready');
          } else {
            console.error("Failed to initialize verification:", data);
            setMessage(data.error || 'Failed to initialize verification');
            setStatus('error');
          }
        }
      } catch (error) {
        console.error('Verification initialization error:', error);
        setMessage('Failed to connect to verification service');
        setStatus('error');
      }
    };
    
    initVerification();
  }, [location.state, user.id]);
  
  // Setup webcam and socket connection
  useEffect(() => {
    if (status !== 'ready' || !verificationId) {
      console.log("Not ready to connect socket:", status, verificationId);
      return;
    }
    
    console.log("Connecting to socket with verification ID:", verificationId);
    
    // Test server connectivity first
    fetch('http://localhost:5001/ping')
      .then(response => response.json())
      .then(data => {
        console.log("Server ping successful:", data);
        initializeSocket();
      })
      .catch(error => {
        console.error("Server ping failed:", error);
        setMessage("Cannot connect to verification server. Please check your connection.");
        setStatus('error');
      });
    
    function initializeSocket() {
      // Initialize socket connection with explicit configuration
      socketRef.current = io('http://localhost:5001', {
        transports: ['polling', 'websocket'],  // Start with polling, upgrade to websocket
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        timeout: 20000,  // Increase timeout
        forceNew: true,  // Force a new connection
        autoConnect: true
      });
      
      // Add connection error logging
      socketRef.current.on('connect_error', (error) => {
        console.error("Socket connection error:", error);
        setMessage(`Connection error: ${error.message}. Please try again.`);
        setStatus('error');
      });
      
      // Setup socket event handlers
      socketRef.current.on('connect', () => {
        console.log("Socket connected, socket ID:", socketRef.current.id);
        // Wait a short time before starting verification to ensure connection is stable
        setTimeout(() => {
          console.log("Emitting start_verification with ID:", verificationId);
          socketRef.current.emit('start_verification', { 
            verification_id: verificationId 
          });
        }, 1000);
      });
      
      socketRef.current.on('connection_status', (data) => {
        console.log("Connection status:", data);
      });
      
      socketRef.current.on('verification_connected', (data) => {
        console.log("Verification connected:", data);
        setMessage('Connected to verification service');
      });
      
      socketRef.current.on('error', (data) => {
        console.error("Socket error:", data);
        setMessage(data.message || 'Verification error');
        if (data.message === 'Invalid verification ID') {
          // Clear the invalid verification ID and reinitialize
          setStatus('error');
          // Try to initialize a new verification after a short delay
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        }
      });
      
      socketRef.current.on('verification_instruction', (data) => {
        console.log("Received instruction:", data);
        setInstruction(data.instruction);
        setStatus('in_progress');
      });
      
      socketRef.current.on('frame_processed', (data) => {
        const { result } = data;
        console.log("Frame processed:", result);
        
        // Update UI based on result
        if (result.face_detected) {
          if (result.movement) {
            setMessage(`Movement detected: ${result.movement}`);
          }
          
          if (result.next_instruction) {
            if (result.next_instruction === "Complete") {
              setStatus('verifying');
              setMessage('Liveness check passed. Verifying identity...');
            } else {
              setInstruction(result.next_instruction);
            }
          }
        } else {
          setMessage('No face detected. Please position your face in the camera.');
        }
      });
      
      socketRef.current.on('verification_complete', (data) => {
        console.log("Verification complete:", data);
        setStatus('completed');
        
        if (data.success && data.match) {
          setMessage('Verification completed successfully! Face matched.');
          
          // Update user profile to mark as verified
          updateProfile({ isVerified: true })
            .then(() => {
              setTimeout(() => navigate('/profile'), 3000);
            })
            .catch(err => console.error('Failed to update profile:', err));
        } else if (data.success && !data.match) {
          setMessage(`Face verification failed. The face doesn't match the ID card (${Math.round(data.confidence * 100)}% confidence).`);
          setTimeout(() => navigate('/verify'), 5000);
        } else {
          setMessage(data.message || 'Verification failed');
        }
      });
      
      socketRef.current.on('connect_error', (error) => {
        console.error("Socket connection error:", error);
        setMessage('Connection error. Please try again.');
        setStatus('error');
      });
      
      // Setup webcam
      const setupWebcam = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
              facingMode: 'user',
              width: { ideal: 640 },
              height: { ideal: 480 }
            }, 
            audio: false 
          });
          
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            streamRef.current = stream;
          }
          
          setStatus('streaming');
        } catch (err) {
          console.error('Error accessing webcam:', err);
          setMessage('Could not access webcam');
          setStatus('error');
        }
      };
      
      setupWebcam();
      
      // Cleanup function
      return () => {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        
        if (socketRef.current) {
          console.log("Disconnecting socket");
          socketRef.current.disconnect();
        }
      };
    }
  }, [status, verificationId, updateProfile, navigate]);
  
  // Send frames to server when streaming
  useEffect(() => {
    if (status !== 'streaming' && status !== 'in_progress') return;
    
    console.log("Starting to send frames with verification ID:", verificationId);
    
    const intervalId = setInterval(() => {
      if (videoRef.current && socketRef.current && socketRef.current.connected) {
        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64 and send to server
        const frame = canvas.toDataURL('image/jpeg', 0.8); // Reduced quality for better performance
        
        // Don't log the base64 data
        socketRef.current.emit('face_frame', {
          verification_id: verificationId,
          frame: frame.split(',')[1] // Remove data URL prefix
        });
      }
    }, 500); // Send frame every 500ms
    
    return () => clearInterval(intervalId);
  }, [status, verificationId]);
  
  const debugWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' }, 
        audio: false 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setStatus('streaming');
        console.log("Debug: Webcam accessed successfully");
      }
    } catch (err) {
      console.error('Debug: Error accessing webcam:', err);
      setMessage(`Debug: Webcam error - ${err.message}`);
    }
  };

  return (
    <div className="page-container">
      <Navbar />
      <div className="video-verification-wrapper">
        <div className="video-verification-container">
          <h1>Face Verification</h1>
          
          <div className="video-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={status === 'completed' ? 'completed' : ''}
              style={{ width: '100%', height: 'auto', display: 'block' }}
            />
            
            {status === 'initializing' && (
              <div className="status-overlay initializing">
                <div className="spinner"></div>
                <p>Initializing verification...</p>
              </div>
            )}
            
            {status === 'error' && (
              <div className="status-overlay error">
                <i className="fas fa-exclamation-circle"></i>
                <p>{message || 'An error occurred'}</p>
                <div className="button-group">
                  <button onClick={() => {
                    // Reload the page to try again
                    window.location.reload();
                  }}>
                    <i className="fas fa-sync"></i> Reload Page
                  </button>
                  <button onClick={() => {
                    // Try to reconnect without reloading
                    setStatus('ready');
                  }}>
                    <i className="fas fa-plug"></i> Reconnect
                  </button>
                  <button onClick={debugWebcam}>
                    <i className="fas fa-video"></i> Debug Webcam
                  </button>
                </div>
              </div>
            )}
            
            {status === 'completed' && (
              <div className="status-overlay completed">
                <i className="fas fa-check-circle"></i>
                <p>{message}</p>
                <p className="redirect-message">Redirecting...</p>
              </div>
            )}
            
            {status === 'verifying' && (
              <div className="status-overlay verifying">
                <div className="spinner"></div>
                <p>{message || 'Verifying your identity...'}</p>
              </div>
            )}
          </div>
          
          {(status === 'streaming' || status === 'in_progress') && (
            <div className="instruction-container">
              <h2>{instruction || 'Preparing verification...'}</h2>
              <p>{message || 'Please follow the instructions and keep your face visible'}</p>
              <div className="liveness-instructions">
                <p>For liveness check, you'll need to:</p>
                <ol>
                  <li>Look at the center of the camera</li>
                  <li>Look to your right when instructed</li>
                  <li>Look to your left when instructed</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoVerification;
















