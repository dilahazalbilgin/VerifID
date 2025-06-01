import face_recognition
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import time
import uuid
import json
import cv2
import numpy as np
import tempfile
from werkzeug.utils import secure_filename
import logging

# Assuming ocr_utils.py is in the same directory or Python path
from ocr_utils import extract_text_from_id, save_face_from_id_card

# Assuming liveness_detection.py and face_utils.py are updated as per previous steps
# and are in the same directory or Python path.
# Specific imports to avoid ambiguity if function names overlap.
from liveness_detection import (
    get_reference_face_encoding,
    process_liveness_frame,
    verify_face_match,
    generate_random_liveness_commands,
    detect_face_blur,
    validate_face_consistency,
    base64_to_image as liveness_base64_to_image # Use an alias if needed
)
from face_utils import (
    # base64_to_image as fu_base64_to_image, # Example if face_utils also has it
    detect_face_details, # Assuming this is the intended function from face_utils
    capture_face_image_for_test
)


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key' # Change in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Configure CORS properly for both REST and WebSocket
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with proper CORS settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='gevent',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=50 * 1024 * 1024,  # Increase buffer size for large frames
    always_connect=True,  # Always allow connections
    transports=['websocket', 'polling']  # Allow both WebSocket and polling
)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store active verification sessions
verification_sessions = {}

def cleanup_old_sessions():
    """Clean up sessions older than 10 minutes"""
    current_time = time.time()
    sessions_to_remove = []

    for session_id, session in verification_sessions.items():
        session_age = current_time - session.get('created_at', 0)
        disconnected_age = current_time - session.get('disconnected_at', current_time)
        completed_age = current_time - session.get('completed_at', current_time)

        # Remove sessions that are:
        # - Older than 10 minutes
        # - Disconnected for more than 5 minutes
        # - Completed/failed for more than 30 seconds (allow time for frontend cleanup)
        should_remove = (
            session_age > 600 or
            (session.get('disconnected') and disconnected_age > 300) or
            (session.get('status') in ['completed', 'failed'] and completed_age > 30)
        )

        if should_remove:
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        logger.info(f"Cleaning up old session: {session_id}")
        del verification_sessions[session_id]

# Add time module for timestamps
import time

# Liveness constants
LIVENESS_COMMAND_SEQUENCE = ['right', 'center', 'left']  # Standard sequence after initial centering
LIVENESS_COMMAND_TIMEOUT = 7  # Seconds per command
FACE_MOVEMENT_THRESHOLD = 40  # Pixel threshold for movement detection
FRAME_SKIP_RATE = 2  # Process every Nth frame to optimize

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'pong'})

# Single connect handler
@socketio.on('connect')
def handle_connect_socket(): # Renamed to avoid conflict if there were others
    logger.debug(f"Client connected: {request.sid}")
    # Emit a general connection status, specific status can be sent by other events
    emit('connection_response', {'status': 'connected', 'sid': request.sid})


@socketio.on('ping')
def handle_ping():
    """Simple ping handler to keep connection alive"""
    emit('pong')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.debug(f"Client disconnected: {request.sid}")
    # Find and mark any sessions associated with this socket as disconnected
    # Don't delete sessions immediately - keep them for potential reconnection
    for session_id, session in verification_sessions.items():
        if session.get('socket_sid') == request.sid:
            logger.info(f"Marking session {session_id} as disconnected (keeping for potential reconnection)")
            session['disconnected'] = True
            session['disconnected_at'] = time.time()


@app.route('/verify/id', methods=['POST'])
def verify_id_card():
    """Process ID card verification"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        user_data_str = request.form.get('userData') # Changed to user_data_str
        
        logger.debug(f"Received file: {file.filename}")
        logger.debug(f"User data string: {user_data_str}")
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        temp_filepath = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        
        try:
            file.save(temp_filepath)
            logger.debug(f"Temporary file saved to: {temp_filepath}")
            
            img = cv2.imread(temp_filepath)
            if img is None:
                logger.error("Could not read image from temp file.")
                return jsonify({'error': 'Could not read image'}), 400
            
            ocr_result = extract_text_from_id(img, user_data_str) # Pass user_data_str
            
            user_id = None
            if user_data_str:
                try:
                    # user_data_dict is parsed inside extract_text_from_id and also here
                    # Ensure consistency or parse once. For now, keeping similar to original.
                    user_data_dict = json.loads(user_data_str) if isinstance(user_data_str, str) else user_data_str
                    user_id = user_data_dict.get('id')
                except json.JSONDecodeError:
                    logger.warning("Failed to parse userData JSON in /verify/id")
                except Exception as e:
                    logger.error(f"Error extracting user_id from userData: {e}")

            if user_id:
                success, face_path_or_error = save_face_from_id_card(img, user_id)
                if success:
                    logger.info(f"Successfully saved face image for user {user_id} at {face_path_or_error}")
                else:
                    logger.warning(f"Failed to save face image for user {user_id}: {face_path_or_error}")
            
            verification_result = {
                'success': ocr_result.get('success', False),
                'message': ocr_result.get('message', 'ID card processing failed'),
                'verification_id': ocr_result.get('verification_id', str(uuid.uuid4())),
                'extracted_data': ocr_result.get('extracted_data', {}),
                'user_match': ocr_result.get('user_match', {'overall_match': False, 'match_percentage': 0, 'matches': []}),
                'face_image': ocr_result.get('face_image')
            }
            
            logger.debug(f"Final verification result: {json.dumps(verification_result, indent=2)}")
            return jsonify(verification_result)
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
    
    except Exception as e:
        logger.error(f"Error in verify_id_card: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/face/initialize', methods=['POST'])
def initialize_face_verification():
    """Initialize a face verification session"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        # Check if reference face exists
        import os
        face_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'face_info')
        face_path = os.path.join(face_info_dir, f"{user_id}.jpg")
        
        if not os.path.exists(face_path):
            logger.warning(f"Reference face not found for user {user_id} at {face_path}")
            return jsonify({
                'error': 'Reference face not found',
                'message': 'Please complete ID verification first to register your face.'
            }), 400
        
        # Create a new verification session with random commands
        verification_id = str(uuid.uuid4())
        random_commands = generate_random_liveness_commands(3)  # Generate 3 random commands (reduced from 4)
        verification_sessions[verification_id] = {
            'user_id': user_id,
            'status': 'initialized',
            'liveness_commands': random_commands,  # Use random commands for security
            'current_command_index': 0,
            'reference_center_x': None,
            'reference_face_size': None,  # Store reference face size for consistency checks
            'movements_done': [],
            'created_at': time.time(),
            'failed_attempts': 0,  # Track failed attempts
            'max_attempts': 5  # Maximum allowed attempts (increased from 3)
        }
        
        logger.info(f"Face verification session initialized for user {user_id}: {verification_id}")
        
        return jsonify({
            'verification_id': verification_id,
            'status': 'initialized',
            'message': 'Face verification session initialized'
        })
    except Exception as e:
        logger.error(f"Error initializing face verification: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Socket.IO events for Liveness
@socketio.on('start_liveness_check')
def handle_start_liveness_check(data):
    """Initialize liveness check process"""
    verification_id = data.get('verification_id')

    if not verification_id:
        logger.error("No verification_id provided in start_liveness_check")
        emit('liveness_error', {'message': 'No verification ID provided'})
        return

    # Clean up old sessions before checking
    cleanup_old_sessions()

    if verification_id not in verification_sessions:
        logger.error(f"Invalid verification_id in start_liveness_check: {verification_id}")
        emit('liveness_error', {'message': 'Invalid verification session. Please restart verification.'})
        return

    logger.debug(f"Attempting to start liveness check for verification_id: {verification_id}")

    try:
        session = verification_sessions[verification_id]
        user_id = session.get('user_id')

        if not user_id:
            logger.error(f"No user_id found in session {verification_id}")
            emit('liveness_error', {'message': 'Invalid session data'})
            return

        # Load reference face encoding
        from liveness_detection import get_reference_face_encoding

        # Debug the face_info directory path
        import os
        face_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'face_info')
        logger.debug(f"Looking for reference face in: {face_info_dir}")

        # Check if the directory exists
        if not os.path.exists(face_info_dir):
            logger.error(f"face_info directory does not exist: {face_info_dir}")
            os.makedirs(face_info_dir, exist_ok=True)
            logger.info(f"Created face_info directory: {face_info_dir}")

        # Check if the user's face image exists
        face_path = os.path.join(face_info_dir, f"{user_id}.jpg")
        if not os.path.exists(face_path):
            logger.error(f"Reference face image not found for user {user_id} at {face_path}")
            emit('liveness_error', {'message': 'Reference face not found. Please complete ID verification first.'})
            return

        # Try to load the reference face encoding
        reference_encoding = get_reference_face_encoding(user_id)
        if reference_encoding is None:
            logger.error(f"Failed to load reference face encoding for user {user_id}")
            emit('liveness_error', {'message': 'Could not process reference face. Please try again.'})
            return

        logger.info(f"Successfully loaded reference face encoding for user {user_id}")

        # Store reference encoding in session
        session['reference_encoding'] = reference_encoding

        # Initialize liveness check (allow reconnection)
        session['status'] = 'centering'
        session['socket_sid'] = request.sid  # Update socket ID for reconnection
        session['disconnected'] = False  # Mark as reconnected
        if 'disconnected_at' in session:
            del session['disconnected_at']  # Remove disconnection timestamp

        # Use the random commands from the session instead of fixed ones
        if 'liveness_commands' not in session:
            session['liveness_commands'] = generate_random_liveness_commands(3)

        logger.info(f"Liveness check initialized for {verification_id}. Instructing user to center face.")
        emit('liveness_instruction', {'instruction': 'Please position your face in the center of the screen.'})

    except Exception as e:
        logger.error(f"Error in start_liveness_check: {str(e)}", exc_info=True)
        emit('liveness_error', {'message': f"Failed to initialize verification: {str(e)}"})

@socketio.on('liveness_frame')
def handle_liveness_frame(data):
    verification_id = data.get('verification_id')
    frame_data_b64 = data.get('frame')

    # Clean up old sessions periodically
    cleanup_old_sessions()

    if not verification_id:
        logger.error("No verification_id provided in liveness_frame")
        emit('liveness_error', {'message': 'No verification ID provided'})
        return

    if verification_id not in verification_sessions:
        logger.error(f"Invalid verification_id in liveness_frame: {verification_id}")
        # Don't emit error if session was just cleaned up - this is normal during completion
        return
    
    session = verification_sessions[verification_id]

    # Prevent processing if session is already completed or failed
    if session.get('status') in ['completed', 'failed']:
        logger.debug(f"Ignoring frame for {session.get('status')} session: {verification_id}")
        return

    if not frame_data_b64:
        logger.error(f"No frame data provided for {verification_id}")
        emit('liveness_feedback', {'message': 'No frame data received'})
        return
    
    # Initialize frame counter if not exists
    if 'frame_counter' not in session:
        session['frame_counter'] = 0
    
    session['frame_counter'] += 1
    
    # Process every 2nd frame to reduce load
    if session['frame_counter'] % 2 != 0:
        return
    
    try:
        # Convert base64 to image
        import base64
        import cv2
        import numpy as np
        
        # Remove data URL prefix if present
        if ',' in frame_data_b64:
            frame_data_b64 = frame_data_b64.split(',')[1]
            
        # Decode base64 to binary
        img_data = base64.b64decode(frame_data_b64)
        
        # Convert to numpy array
        nparr = np.frombuffer(img_data, np.uint8)
        
        # Decode image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            logger.error(f"Failed to decode image for {verification_id}")
            emit('liveness_feedback', {'message': 'Failed to process image'})
            return
            
        # Process based on session status
        if session['status'] == 'centering':
            # Simple face detection for centering
            import face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if face_locations:
                # Face detected, set reference center and move to first command
                top, right, bottom, left = face_locations[0]
                session['reference_center_x'] = (left + right) // 2

                # Store reference face size for consistency checks
                face_width = right - left
                face_height = bottom - top
                session['reference_face_size'] = {'width': face_width, 'height': face_height}

                session['status'] = 'in_progress'
                session['current_command_index'] = 0

                # Start with first command
                first_command = session['liveness_commands'][session['current_command_index']]
                session['command_start_time'] = time.time()

                logger.info(f"Centering successful for {verification_id}. Starting with command: {first_command}")
                emit('liveness_instruction', {
                    'instruction': f"Please look {first_command}"
                })
            else:
                # No face detected, keep centering
                emit('liveness_feedback', {
                    'message': "No face detected. Please ensure your face is clearly visible."
                })
        
        elif session['status'] == 'in_progress':
            # Process liveness detection frame
            from liveness_detection import process_liveness_frame, verify_face_match
            
            # Get current command
            current_command_index = session.get('current_command_index', 0)
            if current_command_index >= len(session['liveness_commands']):
                logger.error(f"Invalid command index {current_command_index} for session {verification_id}")
                emit('liveness_error', {'message': 'Invalid command sequence'})
                return
            
            current_command = session['liveness_commands'][current_command_index]
            reference_center_x = session.get('reference_center_x')
            
            if reference_center_x is None:
                logger.error(f"Reference center X not set for session {verification_id}")
                emit('liveness_error', {'message': 'Reference position not established'})
                return
            
            # Process the frame for liveness detection
            result = process_liveness_frame(frame, reference_center_x, current_command)

            if not result['face_detected']:
                error_msg = result.get('error_message', 'Face not detected. Please keep your face in view.')
                emit('liveness_feedback', {'message': error_msg})

                # Track failed attempts
                session['failed_attempts'] = session.get('failed_attempts', 0) + 1
                if session['failed_attempts'] >= session.get('max_attempts', 5):
                    emit('liveness_result', {
                        'success': False,
                        'message': 'Verification failed: Too many failed attempts.',
                        'match_status': False
                    })
                    # Mark session as failed instead of deleting immediately
                    if verification_id in verification_sessions:
                        verification_sessions[verification_id]['status'] = 'failed'
                        verification_sessions[verification_id]['completed_at'] = time.time()
                return

            # Validate face consistency if we have reference data (made less strict)
            if session.get('reference_face_size'):
                current_face_size = result.get('face_size', {})
                is_consistent, size_diff = validate_face_consistency(
                    current_face_size,
                    session['reference_face_size']
                )

                # Only warn, don't fail the verification for consistency issues
                if not is_consistent:
                    logger.warning(f"Face size inconsistency detected: {size_diff:.2f}")
                    # Just log the warning, don't return/fail

            # Check for face blur (anti-spoofing) - made less strict
            face_location = result.get('face_location')
            if face_location:
                is_clear, blur_score = detect_face_blur(
                    frame,
                    (face_location['top'], face_location['right'], face_location['bottom'], face_location['left'])
                )

                # Only warn for very blurry images, don't fail for moderate blur
                if not is_clear and blur_score < 25:  # Only fail for extremely blurry images
                    emit('liveness_feedback', {
                        'message': 'Image quality very low. Please ensure better lighting.'
                    })
                    return

            # Log the detected movement
            logger.debug(f"Movement detected: {result['movement_detected']}, expected: {current_command}, "
                        f"distance: {result.get('movement_distance', 0)}, threshold: {result.get('threshold_used', 0)}")
            
            # Check if the command was matched
            if result['command_matched']:
                # Command matched, move to next or complete
                session['movements_done'].append(current_command)
                current_command_index += 1
                session['current_command_index'] = current_command_index
                
                if current_command_index >= len(session['liveness_commands']):
                    # All commands completed, verify face match
                    logger.info(f"All liveness commands completed for {verification_id}. Verifying face match.")
                    
                    # Ensure reference encoding is available
                    if 'reference_encoding' not in session:
                        logger.error(f"Reference encoding not found in session {verification_id}")
                        emit('liveness_error', {'message': 'Reference face data not available'})
                        return
                    
                    # Verify face match
                    match_result, confidence, match_message = verify_face_match(frame, session['reference_encoding'])

                    logger.info(f"Face match result for {verification_id}: {match_result}, confidence: {confidence}, message: {match_message}")

                    # Send result to client
                    if match_result:
                        emit('liveness_result', {
                            'success': True,
                            'message': 'Verification Successful! Face matched and liveness confirmed.',
                            'match_status': match_result,
                            'confidence': confidence,
                            'match_threshold': 0.55  # Updated threshold (relaxed)
                        })
                    else:
                        emit('liveness_result', {
                            'success': False,
                            'message': f'Verification Failed: {match_message}',
                            'match_status': match_result,
                            'confidence': confidence,
                            'match_threshold': 0.55
                        })
                    
                    # Mark session as completed instead of deleting immediately
                    if verification_id in verification_sessions:
                        verification_sessions[verification_id]['status'] = 'completed'
                        verification_sessions[verification_id]['completed_at'] = time.time()
                else:
                    # Move to next command
                    next_command = session['liveness_commands'][current_command_index]
                    session['command_start_time'] = time.time()
                    
                    emit('liveness_instruction', {
                        'instruction': f"Please look {next_command}"
                    })
            else:
                # Not matched yet, provide feedback
                emit('liveness_feedback', {
                    'message': f"Detected: {result['movement_detected']}. Please look {current_command}."
                })
                
                # Check for timeout
                if 'command_start_time' in session and time.time() - session['command_start_time'] > 10:  # 10 second timeout
                    session['status'] = 'failed'
                    
                    emit('liveness_result', {
                        'success': False,
                        'message': f"Verification Failed: Timeout on '{current_command}' command.",
                        'match_status': False
                    })
                    
                    # Mark session as failed instead of deleting immediately
                    if verification_id in verification_sessions:
                        verification_sessions[verification_id]['status'] = 'failed'
                        verification_sessions[verification_id]['completed_at'] = time.time()
    
    except Exception as e:
        logger.error(f"Error processing liveness frame: {str(e)}", exc_info=True)
        emit('liveness_error', {'message': f"Error processing frame: {str(e)}"})


# Test routes (can be removed or secured in production)
@app.route('/api/test/face-capture', methods=['GET'])
def route_test_face_capture(): # Renamed to avoid conflict
    frame, message = capture_face_image_for_test() # Use updated function name
    if frame is None:
        return jsonify({'error': message}), 500
    filename = f"test_capture_{uuid.uuid4()}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv2.imwrite(filepath, frame)
    return jsonify({'success': True, 'message': 'Face captured successfully', 'image_path': filepath})

@app.route('/api/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/api/verify/face/check/<verification_id>', methods=['GET'])
def check_verification_id_route(verification_id):
    # Clean up old sessions first
    cleanup_old_sessions()

    if verification_id in verification_sessions:
        session_info = verification_sessions[verification_id]
        return jsonify({
            'valid': True,
            'session_details': {
                'user_id': session_info.get('user_id'),
                'status': session_info.get('status'),
                'disconnected': session_info.get('disconnected', False),
                'created_at': session_info.get('created_at'),
                'current_command_index': session_info.get('current_command_index', 0),
                'liveness_commands': session_info.get('liveness_commands', [])
            }
        })
    else:
        return jsonify({
            'valid': False,
            'message': 'Verification ID not found or expired'
        })


if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO server with gevent...")
    # Make sure gevent-websocket is installed
    try:
        from geventwebsocket.handler import WebSocketHandler
        from gevent.pywsgi import WSGIServer
        
        http_server = WSGIServer(('0.0.0.0', 5001), app, 
                                handler_class=WebSocketHandler)
        logger.info("Server starting with WebSocketHandler")
        http_server.serve_forever()
    except ImportError:
        logger.warning("gevent-websocket not found, falling back to default SocketIO run")
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5001, 
            debug=True,
            use_reloader=False
        )




