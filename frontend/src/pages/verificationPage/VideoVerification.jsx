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
  
  const [status, setStatus] = useState('initializing'); // initializing, ready, centering, in_progress, completed, error
  const [instruction, setInstruction] = useState('Initializing...');
  const [feedbackMessage, setFeedbackMessage] = useState(''); // For secondary messages like "No face detected"
  const [verificationId, setVerificationId] = useState('');
  
  // Effect 1: Initializes verificationId and sets status to 'ready'
  useEffect(() => {
    const initVerification = async () => {
      setStatus('initializing');
      setInstruction('Initializing verification process...');
      try {
        let id = location.state?.verificationId || null;
        let needsNewId = true;
        
        if (id) {
          console.log("Checking existing verification ID in state:", id);
          const checkResponse = await fetch(`http://localhost:5001/api/verify/face/check/${id}`);
          const checkResult = await checkResponse.json();
          
          if (checkResult.valid && checkResult.session_details?.status !== 'completed' && checkResult.session_details?.status !== 'failed') {
            console.log("Verification ID is valid and session is active:", id);
            setVerificationId(id);
            setStatus('ready'); // Ready to connect socket
            needsNewId = false;
          } else {
            console.log("Verification ID is invalid or session completed/failed, will create new one. Reason:", checkResult.message || checkResult.session_details?.status);
          }
        }
        
        if (needsNewId) {
          console.log("Initializing new verification for user:", user?.id);
          if (!user?.id) {
            console.error("User ID not available for new verification.");
            setInstruction('User information not found. Please log in again.');
            setStatus('error');
            return;
          }
          const response = await fetch('http://localhost:5001/api/verify/face/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.id })
          });
          
          const data = await response.json();
          if (data.verification_id) {
            console.log("Received new verification ID:", data.verification_id);
            setVerificationId(data.verification_id);
            setStatus('ready'); // Ready to connect socket
          } else {
            console.error("Failed to initialize verification:", data);
            setInstruction(data.error || 'Failed to initialize verification process.');
            setStatus('error');
          }
        }
      } catch (error) {
        console.error('Verification initialization error:', error);
        setInstruction('Failed to connect to verification service. Please check server.');
        setStatus('error');
      }
    };
    
    if (user?.id) {
        initVerification();
    } else {
        console.log("Waiting for user data to initialize verification...");
    }

  }, [location.state, user?.id]); // Removed navigate, updateProfile if not directly used by initVerification

  // Effect 2: Webcam/Socket Setup, Event Handlers, and Liveness Logic
  // This effect now runs primarily when verificationId changes.
  // Internal logic gates setup based on the current `status`.
  useEffect(() => {
    if (!verificationId) {
      console.log("Main setup effect: No verificationId, skipping setup.");
      // Cleanup for a previous verificationId would have run if verificationId changed to null/undefined
      return;
    }

    // Only proceed with setup if status is 'ready' for the current verificationId.
    // This prevents re-setup if status changes to other states like 'centering' or 'error'
    // after initial setup for this verificationId.
    if (status !== 'ready') {
      console.log(`Main setup effect: Not in 'ready' state for verificationId ${verificationId}. Current status: ${status}. No new setup initiated.`);
      return;
    }
    
    console.log(`Main setup effect: Status is 'ready' for verificationId ${verificationId}. Proceeding with setup.`);
    setInstruction('Connecting to verification service...');

    let pingIntervalId = null; // Store ping interval ID for cleanup

    function initializeSocketForEffect() {
      console.log("Initializing socket connection to http://localhost:5001 for ID:", verificationId);
      
      if (socketRef.current) {
        console.log("Cleaning up existing socket connection in initializeSocketForEffect");
        socketRef.current.disconnect();
        socketRef.current = null;
      }
      
      socketRef.current = io('http://localhost:5001', {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 10,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 20000,
        autoConnect: true,
        forceNew: true 
      });
      
      socketRef.current.on('connect_error', (error) => {
        console.error("Socket connection error:", error.message, error.data);
        setInstruction(`Connection Error: ${error.message}. Retrying...`);
        setStatus('error');
      });
      
      socketRef.current.on('connect', () => {
        console.log("Socket connected successfully. SID:", socketRef.current.id, "for VerID:", verificationId);
        setInstruction('Connected. Starting verification...');
        console.log("Emitting start_liveness_check with verification_id:", verificationId);
        socketRef.current.emit('start_liveness_check', { verification_id: verificationId });
      });
      
      socketRef.current.on('connection_response', (data) => {
        console.log("Server connection response:", data);
      });
      
      socketRef.current.on('liveness_instruction', (data) => {
        console.log("Received liveness_instruction:", data.instruction, "for VerID:", verificationId);
        setInstruction(data.instruction);
        setFeedbackMessage('');
        if (data.instruction.toLowerCase().includes("center")) {
          setStatus('centering'); // This status change will NOT cause this useEffect to cleanup/re-run.
        } else {
          setStatus('in_progress'); // This status change will NOT cause this useEffect to cleanup/re-run.
        }
      });

      socketRef.current.on('liveness_feedback', (data) => {
        console.log("Received liveness_feedback:", data.message, "for VerID:", verificationId);
        setFeedbackMessage(data.message);
      });
      
      socketRef.current.on('liveness_result', (data) => {
        console.log("Received liveness_result:", data, "for VerID:", verificationId);
        setStatus('completed');
        setFeedbackMessage('');

        if (data.success && data.match_status) {
          setInstruction('Verification Successful! Redirecting...');
          updateProfile({ isVerified: true })
            .then(() => setTimeout(() => navigate('/profile'), 3000))
            .catch(err => console.error('Failed to update profile:', err));
        } else {
          setInstruction(data.message || 'Verification Failed. Redirecting to ID verification...');
          // Redirect to ID verification page after face verification fails
          setTimeout(() => {
            navigate('/verify', {
              state: {
                fromFaceVerification: true,
                failureReason: data.message || 'Face verification failed'
              }
            });
          }, 3000);
        }

        setTimeout(() => {
          if (streamRef.current) {
            console.log("Stopping webcam tracks on liveness_result for VerID:", verificationId);
            streamRef.current.getTracks().forEach(track => track.stop());
          }
        }, 3000);
      });

      socketRef.current.on('liveness_error', (data) => {
        console.error("Liveness process error:", data.message, "for VerID:", verificationId);
        setInstruction(data.message || 'An error occurred during verification.');
        setFeedbackMessage('');
        setStatus('error');
      });
      
      socketRef.current.on('disconnect', (reason) => {
        console.log("Socket disconnected:", reason, "for VerID:", verificationId);
        // Use functional update for setStatus to get the latest status
        setStatus(prevStatus => {
          if (prevStatus !== 'completed' && prevStatus !== 'error') {
            setInstruction('Connection lost. Please check your internet connection.');
            return 'error';
          }
          return prevStatus;
        });
      });
      
      pingIntervalId = setInterval(() => {
        if (socketRef.current && socketRef.current.connected) {
          console.log("Sending ping to keep connection alive for VerID:", verificationId);
          socketRef.current.emit('ping');
        }
      }, 5000);
    }

    const setupWebcamForEffect = async () => {
      console.log("Setting up webcam for VerID:", verificationId);
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 }}, 
          audio: false 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          console.log("Webcam setup complete for VerID:", verificationId);
          initializeSocketForEffect(); 
        }
      } catch (err) {
        console.error('Error accessing webcam for VerID:', verificationId, err);
        setInstruction('Webcam access denied or not available. Please check permissions.');
        setStatus('error');
      }
    };

    setupWebcamForEffect(); // Initiate setup

    return () => {
      // This cleanup runs ONLY when verificationId changes or component unmounts.
      console.log("Main setup effect: Cleaning up resources for VerID (or unmount):", verificationId);
      if (pingIntervalId) {
        clearInterval(pingIntervalId);
        console.log("Cleared ping interval for VerID:", verificationId);
      }
      if (streamRef.current) {
        console.log("Stopping webcam tracks in main cleanup for VerID:", verificationId);
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null; 
      }
      if (socketRef.current) {
        console.log("Disconnecting socket in main cleanup for VerID:", verificationId, "SID:", socketRef.current.id);
        socketRef.current.disconnect();
        socketRef.current = null; 
      }
    };
  }, [verificationId, navigate, updateProfile]); // `status` is removed. `Maps` and `updateProfile` are stable.

  // Effect 3: Frame Sending Logic
  useEffect(() => {
    if (status !== 'centering' && status !== 'in_progress') {
      return;
    }
    
    // Ensure socket is connected before attempting to send frames
    if (!socketRef.current || !socketRef.current.connected) {
        console.log(`Frame sending effect: Socket not ready for ${status} state. Skipping frame logic for VerID: ${verificationId}`);
        return;
    }
    
    console.log(`Status is ${status}. Starting to send frames for verification ID:`, verificationId);
    
    const frameInterval = 500;
    let frameCount = 0;
    
    const sendFrame = () => {
      if (!videoRef.current || !socketRef.current || !socketRef.current.connected) {
        console.log("sendFrame: Video or socket not ready, skipping frame for VerID:", verificationId);
        return;
      }
      
      if (videoRef.current.readyState !== 4) {
        console.log("sendFrame: Video not ready yet, waiting for VerID:", verificationId);
        return;
      }
      
      try {
        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        const frameDataUrl = canvas.toDataURL('image/jpeg', 0.6);
        
        console.log(`Sending frame ${++frameCount} for verification ID: ${verificationId}`);
        socketRef.current.emit('liveness_frame', {
          verification_id: verificationId,
          frame: frameDataUrl
        });
      } catch (err) {
        console.error("Error sending frame for VerID:", verificationId, err);
      }
    };
    
    const intervalId = setInterval(sendFrame, frameInterval);
    sendFrame(); // Send first frame immediately
    
    return () => {
        console.log("Cleaning up frame sending interval for VerID:", verificationId);
        clearInterval(intervalId);
    };
  }, [status, verificationId]); // Depends on status to start/stop sending, and verificationId for the data
  
  const handleReload = () => window.location.reload();
  const handleReconnect = () => {
    setInstruction('Attempting to reconnect...');
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    // Re-initialize by trying to set status to 'ready'.
    // This might require re-fetching verificationId if it's lost or invalid.
    // For simplicity, we set to 'ready', assuming initVerification might run again if needed,
    // or if verificationId is still valid, the main setup effect's condition will be met.
    // A more robust reconnect might re-trigger initVerification.
    // For now, this will make the main setup effect re-evaluate its conditions.
    if(verificationId) { // Only set to ready if we still have a verificationId
        setStatus('ready');
    } else {
        // If no verificationId, trigger full re-initialization
        // This can be done by clearing location.state and letting initVerification run
        // or by directly calling initVerification if user context is available.
        // For now, simplest is to reload, or let initVerification handle missing ID.
        console.log("Reconnect: No verificationId, attempting to re-init by resetting status to initializing");
        setStatus('initializing'); // This should re-trigger initVerification if user.id is present
         // Or force init:
        if (user?.id) { // from line 59 logic
            // Manually trigger re-initialization flow.
            // Clearing verificationId and setting status to initializing will make Effect 1 run initVerification.
            setVerificationId(''); 
            setStatus('initializing'); 
            // initVerification(); // This would be ideal but initVerification is not in this scope directly
            // Instead, rely on Effect 1 re-running due to status/verificationId changes in some cases,
            // OR, a simpler robust reconnect is often a page reload or navigating away and back.
            // For now, setting status to 'ready' if ID exists, or 'initializing' to re-trigger Effect 1.
        } else {
            setInstruction("Cannot reconnect without user information.");
        }
    }
  };

  return (
    <div className="page-container">
      <Navbar />
      <div className="video-verification-wrapper">
        <div className="video-verification-container">
          <h1>Face Liveness Verification</h1>
          
          <div className="video-container">
            <video ref={videoRef} autoPlay playsInline muted className={status === 'completed' ? 'completed' : ''} />
            
            {status === 'initializing' && (
              <div className="status-overlay initializing">
                <div className="spinner"></div>
                <p>{instruction}</p>
              </div>
            )}
            
            {status === 'error' && (
              <div className="status-overlay error">
                <i className="fas fa-exclamation-circle"></i>
                <p>{instruction || 'An error occurred'}</p>
                <p>{feedbackMessage}</p>
                <div className="button-group">
                  <button onClick={handleReload}><i className="fas fa-sync"></i> Try Again</button>
                  {/* <button onClick={handleReconnect}><i className="fas fa-plug"></i> Reconnect</button> */} 
                  {/* Reconnect button might need more robust logic, consider reload for now */}
                </div>
              </div>
            )}
            
            {status === 'completed' && (
              <div className={`status-overlay completed ${instruction.toLowerCase().includes('successful') ? 'success' : 'failure'}`}>
                <i className={`fas ${instruction.toLowerCase().includes('successful') ? 'fa-check-circle' : instruction.toLowerCase().includes('redirecting to id') ? 'fa-arrow-right' : 'fa-times-circle'}`}></i>
                <p>{instruction}</p>
                {instruction.toLowerCase().includes('redirecting to id') && (
                  <p style={{fontSize: '14px', marginTop: '10px', opacity: 0.8}}>
                    You will be redirected to complete ID verification...
                  </p>
                )}
              </div>
            )}
          </div>
          
          {(status === 'centering' || status === 'in_progress') && (
            <div className="instruction-container">
              <h2>{instruction || 'Follow instructions...'}</h2>
              <p className="feedback-message">{feedbackMessage}</p>
              <div className="liveness-instructions-summary">
                <p>Please follow the on-screen prompts carefully.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoVerification;