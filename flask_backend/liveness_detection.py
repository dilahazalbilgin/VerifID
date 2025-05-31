import cv2
import face_recognition
import time
import os
import base64
import numpy as np
from PIL import Image
import io

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

def image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')


def get_reference_face(user_id):
    """Get reference face encoding from face_info folder"""
    # Path to face_info folder
    face_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'face_info')
    face_path = os.path.join(face_info_dir, f"{user_id}.jpg")

    if not os.path.exists(face_path):
        return None, "Reference face not found"

    # Load reference image
    reference_image = face_recognition.load_image_file(face_path)
    reference_encodings = face_recognition.face_encodings(reference_image)

    if not reference_encodings:
        return None, "No face found in reference image"

    return reference_encodings[0], "Success"

def process_liveness_frame(frame, reference_center_x=None, command=None):
    """Process a single frame for liveness detection"""
    # Convert frame to RGB for face_recognition
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    face_locations = face_recognition.face_locations(rgb)
    
    if not face_locations:
        return {
            "face_detected": False,
            "movement": None,
            "command_matched": False,
            "reference_center_x": reference_center_x
        }
    
    # Get face location
    top, right, bottom, left = face_locations[0]
    current_center_x = (left + right) // 2
    
    # If this is the first frame, set reference_center_x
    if reference_center_x is None:
        reference_center_x = current_center_x
    
    # Determine movement
    threshold = 40  # pixel difference tolerance
    movement = "center"
    if current_center_x < reference_center_x - threshold:
        movement = "right"  # screen left = user's RIGHT
    elif current_center_x > reference_center_x + threshold:
        movement = "left"   # screen right = user's LEFT
    
    # Check if movement matches command
    command_matched = (command == movement) if command else False
    
    return {
        "face_detected": True,
        "face_location": (top, right, bottom, left),
        "current_center_x": current_center_x,
        "reference_center_x": reference_center_x,
        "movement": movement,
        "command_matched": command_matched
    }

def verify_face_match(frame, reference_encoding):
    """Verify if the face in the frame matches the reference face"""
    # Convert frame to RGB for face_recognition
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(rgb)
    
    if not face_encodings:
        return False, 0.0
    
    # Compare faces
    face_distances = face_recognition.face_distance([reference_encoding], face_encodings[0])
    match = face_distances[0] <= 0.6  # Threshold for match
    confidence = 1.0 - min(face_distances[0], 1.0)  # Convert distance to confidence
    
    return match, float(confidence)