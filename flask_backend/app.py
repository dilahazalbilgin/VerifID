from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import uuid
import json
import cv2
import numpy as np
import tempfile
from werkzeug.utils import secure_filename
import logging
from ocr_utils import extract_text_from_id
from liveness_detection import *
from face_utils import *


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Configure CORS properly for both REST and WebSocket
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with proper CORS settings
# Use gevent mode instead of eventlet due to compatibility issues
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='gevent',  # Use gevent instead of eventlet
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Remove the after_request handler that adds additional CORS headers
# @app.after_request
# def add_cors_headers(response):
#     ...

# Store active verification sessions
verification_sessions = {}

# Add a simple ping route to test connectivity
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'pong'})

# Add a simple socket.io event to test connectivity
@socketio.on('connect')
def handle_connect():
    logger.debug(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    logger.debug(f"Client disconnected: {request.sid}")

@app.route('/verify/id', methods=['POST'])
def verify_id_card():
    """Process ID card verification without storing the image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        user_data = request.form.get('userData')
        
        print(f"Received file: {file.filename}")
        print(f"User data: {user_data}")
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Create a temporary file to process
        temp_filepath = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        
        try:
            # Save file temporarily
            file.save(temp_filepath)
            print(f"Temporary file saved to: {temp_filepath}")
            
            # Read the image
            img = cv2.imread(temp_filepath)
            if img is None:
                return jsonify({'error': 'Could not read image'}), 400
            
            # Process the image
            ocr_result = extract_text_from_id(img, user_data)
            
            # Debug: Print the matches to see if surname is included
            if 'user_match' in ocr_result and 'matches' in ocr_result['user_match']:
                print(f"Matches before sending to frontend: {ocr_result['user_match']['matches']}")
            
            # Create verification result
            verification_result = {
                'success': ocr_result.get('success', False),
                'message': ocr_result.get('message', 'ID card processing failed'),
                'verification_id': ocr_result.get('verification_id', str(uuid.uuid4())),
                'extracted_data': ocr_result.get('extracted_data', {}),
                'user_match': ocr_result.get('user_match', {'overall_match': False, 'match_percentage': 0, 'matches': []}),
                'face_image': ocr_result.get('face_image')
            }
            
            # Ensure user_match has matches array with surname included
            if 'user_match' in verification_result:
                if 'matches' not in verification_result['user_match']:
                    verification_result['user_match']['matches'] = []
                
                # Debug: Print the final response
                print(f"Final verification result: {json.dumps(verification_result, indent=2)}")
            
            return jsonify(verification_result)
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
    
    except Exception as e:
        print(f"Error in verify_id_card: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/face/initialize', methods=['POST'])
def initialize_face_verification():
    """Initialize a face verification session"""
    try:
        data = request.json
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if not session_id or not user_id:
            return jsonify({'error': 'Missing session_id or user_id'}), 400
        
        # Get reference face encoding
        reference_encoding = get_reference_face(user_id)
        if reference_encoding is None:
            return jsonify({'error': 'No reference face found for user'}), 404
        
        # Create a new verification session
        verification_id = str(uuid.uuid4())
        verification_sessions[verification_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'status': 'initialized',
            'steps': ['center', 'right', 'left'],  # Liveness detection steps
            'current_step': 0,
            'reference_encoding': reference_encoding,
            'reference_center_x': None,
            'movements_done': []
        }
        
        print(f"Created verification session: {verification_id}")
        print(f"Current sessions: {list(verification_sessions.keys())}")
        
        return jsonify({
            'verification_id': verification_id,
            'message': 'Face verification initialized'
        })
    except Exception as e:
        print(f"Error in initialize_face_verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/face-capture', methods=['GET'])
def test_face_capture():
    """Test endpoint to capture a face image from webcam"""
    frame, message = capture_face_image()
    
    if frame is None:
        return jsonify({'error': message}), 500
    
    # Save the captured image
    filename = f"test_capture_{uuid.uuid4()}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv2.imwrite(filepath, frame)
    
    return jsonify({
        'success': True,
        'message': 'Face captured successfully',
        'image_path': filepath
    })

@app.route('/api/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    """Serve uploaded files"""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Add a route to check if a verification ID is valid
@app.route('/api/verify/face/check/<verification_id>', methods=['GET'])
def check_verification_id(verification_id):
    if verification_id in verification_sessions:
        return jsonify({
            'valid': True,
            'session': {
                'user_id': verification_sessions[verification_id].get('user_id'),
                'status': verification_sessions[verification_id].get('status')
            }
        })
    else:
        return jsonify({'valid': False})

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print("Client connected to socket")
    emit('verification_connected', {'status': 'connected'})

@socketio.on('start_verification')
def handle_start_verification(data):
    verification_id = data.get('verification_id')
    logger.debug(f"Starting verification: {verification_id}")
    
    if not verification_id:
        logger.error("No verification ID provided")
        emit('error', {'message': 'No verification ID provided'})
        return
    
    # Log all available sessions for debugging
    logger.debug(f"Available sessions: {list(verification_sessions.keys())}")
    
    if verification_id not in verification_sessions:
        logger.error(f"Invalid verification ID: {verification_id}")
        emit('error', {'message': 'Invalid verification ID'})
        return
    
    session = verification_sessions[verification_id]
    session['status'] = 'in_progress'
    
    # Send first instruction
    current_step = session['steps'][session['current_step']]
    logger.debug(f"Sending first instruction: {current_step}")
    emit('verification_instruction', {
        'instruction': f"Please look {current_step}"
    })

@socketio.on('face_frame')
def handle_face_frame(data):
    verification_id = data.get('verification_id')
    frame_data = data.get('frame')
    
    if not verification_id or verification_id not in verification_sessions:
        logger.error(f"Invalid verification ID in face_frame: {verification_id}")
        emit('error', {'message': 'Invalid verification ID'})
        return
    
    if not frame_data:
        logger.error("No frame data provided")
        emit('error', {'message': 'No frame data provided'})
        return
    
    # Get session data
    session = verification_sessions[verification_id]
    
    # Convert base64 to image
    try:
        frame = base64_to_image(frame_data)
    except Exception as e:
        logger.error(f"Error converting frame: {str(e)}")
        emit('error', {'message': 'Invalid frame data'})
        return
    
    # Get current command
    current_command = session['steps'][session['current_step']] if session['current_step'] < len(session['steps']) else None
    
    # Process the frame for liveness detection
    result = process_liveness_frame(
        frame, 
        reference_center_x=session.get('reference_center_x'),
        command=current_command
    )
    
    # Update reference center if not set
    if result['face_detected'] and session['reference_center_x'] is None:
        session['reference_center_x'] = result['reference_center_x']
        emit('frame_processed', {
            'result': {
                'face_detected': True,
                'message': 'Face detected. Starting liveness check.',
                'next_instruction': f"Please look {current_command}"
            }
        })
        return
    
    # If command matched, move to next step
    if result['face_detected'] and result['command_matched']:
        session['movements_done'].append(current_command)
        session['current_step'] += 1
        
        # If all steps completed, verify face match
        if session['current_step'] >= len(session['steps']):
            # Liveness check passed, now verify face match
            match, confidence = verify_face_match(frame, session['reference_encoding'])
            
            session['status'] = 'completed'
            
            if match:
                emit('verification_complete', {
                    'success': True,
                    'message': 'Face verification completed successfully',
                    'match': True,
                    'confidence': confidence
                })
            else:
                emit('verification_complete', {
                    'success': False,
                    'message': 'Face does not match the reference image',
                    'match': False,
                    'confidence': confidence
                })
        else:
            # Move to next step
            next_command = session['steps'][session['current_step']]
            emit('frame_processed', {
                'result': {
                    'face_detected': True,
                    'movement': result['movement'],
                    'command_matched': True,
                    'next_instruction': f"Please look {next_command}"
                }
            })
    else:
        # Command not matched yet
        emit('frame_processed', {
            'result': {
                'face_detected': result.get('face_detected', False),
                'movement': result.get('movement'),
                'command_matched': result.get('command_matched', False),
                'next_instruction': f"Please look {current_command}" if current_command else "Complete"
            }
        })

if __name__ == '__main__':
    # Make sure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the server with gevent mode
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5001, 
        debug=True,
        use_reloader=False  # Disable reloader to avoid duplicate connections
    )











