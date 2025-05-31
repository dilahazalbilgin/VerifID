import cv2
import numpy as np
import base64
import io
from PIL import Image
import face_recognition_models
import face_recognition

print(face_recognition_models.pose_predictor_model_location())


def base64_to_image(base64_string):
    """Convert base64 string to OpenCV image"""
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode base64 string
    img_data = base64.b64decode(base64_string)
    
    # Convert to image
    image = Image.open(io.BytesIO(img_data))
    
    # Convert PIL Image to OpenCV format
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def detect_face(image):
    """Detect faces in the image and return face details using face_recognition"""
    # Find all face locations in the image
    face_locations = face_recognition.face_locations(image)
    
    # Prepare result
    face_details = []
    for face_loc in face_locations:
        # face_recognition returns (top, right, bottom, left)
        top, right, bottom, left = face_loc
        face_details.append({
            'left': int(left),
            'top': int(top),
            'right': int(right),
            'bottom': int(bottom)
        })
    
    return {
        'face_detected': len(face_locations) > 0,
        'face_details': face_details
    }

def process_verification_step(image, step, reference_face=None):
    """Process verification step based on the instruction"""
    # Convert base64 to image if needed
    if isinstance(image, str):
        image = base64_to_image(image)
    
    # Get basic face detection
    face_result = detect_face(image)
    
    # If no face detected, return early
    if not face_result['face_detected']:
        return face_result
    
    # If reference face is provided, compare with current face
    if reference_face and face_result['face_detected']:
        face_result['face_match'] = compare_faces(image, reference_face)
    
    # Process based on step
    if step == 'look_straight':
        # For looking straight, basic face detection is enough
        return face_result
    
    elif step == 'turn_left':
        # For turning left, we would check face orientation
        # This is a simplified implementation
        # In a real implementation, you would analyze face landmarks to determine orientation
        face_landmarks = face_recognition.face_landmarks(image)
        face_result['landmarks'] = face_landmarks if face_landmarks else []
        return face_result
    
    elif step == 'turn_right':
        # For turning right, we would check face orientation
        # This is a simplified implementation
        face_landmarks = face_recognition.face_landmarks(image)
        face_result['landmarks'] = face_landmarks if face_landmarks else []
        return face_result
    
    elif step == 'blink':
        # For blinking, we would detect eye closure
        # This is a simplified implementation
        face_landmarks = face_recognition.face_landmarks(image)
        face_result['landmarks'] = face_landmarks if face_landmarks else []
        return face_result
    
    # Default case
    return face_result

def capture_face_image():
    """Capture a face image from webcam (for testing purposes)"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return None, "Failed to open webcam"
    
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return None, "Failed to capture image"
    
    # Flip the frame for mirror view
    frame = cv2.flip(frame, 1)
    
    # Detect faces
    face_locations = face_recognition.face_locations(frame)
    
    # Draw rectangles around faces
    for face_loc in face_locations:
        top, right, bottom, left = face_loc
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    
    cap.release()
    return frame, "Success"

def compare_faces(current_face_img, reference_face_base64):
    """Compare current face with reference face from ID card"""
    # Convert reference face from base64 if needed
    if isinstance(reference_face_base64, str):
        reference_face_img = base64_to_image(reference_face_base64)
    else:
        reference_face_img = reference_face_base64
    
    # Get face encodings
    current_rgb = cv2.cvtColor(current_face_img, cv2.COLOR_BGR2RGB)
    reference_rgb = cv2.cvtColor(reference_face_img, cv2.COLOR_BGR2RGB)
    
    # Get face encodings (may return empty list if no face detected)
    current_encodings = face_recognition.face_encodings(current_rgb)
    reference_encodings = face_recognition.face_encodings(reference_rgb)
    
    if not current_encodings or not reference_encodings:
        return {
            'match': False,
            'confidence': 0,
            'error': 'Could not encode one or both faces'
        }
    
    # Compare faces
    face_distance = face_recognition.face_distance([reference_encodings[0]], current_encodings[0])[0]
    # Convert distance to similarity score (0-1)
    similarity = 1 - min(face_distance, 1.0)
    
    return {
        'match': similarity > 0.6,  # Threshold can be adjusted
        'confidence': float(similarity),
        'error': None
    }


