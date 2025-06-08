# liveness_service.py
import cv2
import face_recognition
import numpy as np
import base64
import io
import os
import random
from PIL import Image

# --- Core Utilities ---

def base64_to_image(base64_string):
    """Converts a base64 encoded string into an OpenCV image (BGR format)."""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    try:
        img_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(img_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception:
        return None

def get_reference_face_encoding(user_id, face_info_dir='./face_info'):
    """
    Loads a reference image for a given user_id and returns the face encoding.
    [VERSION WITH ENHANCED LOGGING]
    """
    face_path = os.path.join(face_info_dir, f"{user_id}.jpg")
    print(f"[DEBUG] Attempting to load reference face from: {os.path.abspath(face_path)}")

    if not os.path.exists(face_path):
        print(f"[ERROR] File does not exist at path: {face_path}")
        return None

    try:
        print(f"[DEBUG] File found. Loading image with face_recognition...")
        reference_image = face_recognition.load_image_file(face_path)
        print(f"[DEBUG] Image loaded successfully. Now encoding face...")
        
        reference_encodings = face_recognition.face_encodings(reference_image)

        if not reference_encodings:
            print(f"[ERROR] Image at {face_path} was loaded, but NO FACE was detected in it.")
            return None
        
        print(f"[SUCCESS] Face encoding successful for user {user_id}.")
        return reference_encodings[0]

    except Exception as e:
        print(f"[CRITICAL ERROR] An exception occurred while processing {face_path}: {e}")
        return None

# --- Functions Required by app.py ---

def generate_random_liveness_commands(num_commands=3):
    """Generate a random sequence of liveness commands."""
    possible_commands = ['left', 'right', 'center']
    commands = ['center']
    for _ in range(num_commands - 1):
        available = [cmd for cmd in possible_commands if cmd != commands[-1]]
        commands.append(random.choice(available))
    return commands

def process_liveness_frame(frame, reference_center_x, command_to_check, face_detection_threshold=40):
    """Process a single frame for liveness detection based on face displacement."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        return {"face_detected": False, "error_message": "No face detected in frame"}
    if len(face_locations) > 1:
        return {"face_detected": False, "error_message": "Multiple faces detected"}

    top, right, bottom, left = face_locations[0]
    current_center_x = (left + right) // 2
    
    movement_detected = "center"
    if current_center_x < reference_center_x - face_detection_threshold:
        movement_detected = "right"
    elif current_center_x > reference_center_x + face_detection_threshold:
        movement_detected = "left"

    command_matched = (command_to_check == movement_detected)

    return {
        "face_detected": True,
        "movement_detected": movement_detected,
        "command_matched": command_matched,
        "face_location": {"top": top, "right": right, "bottom": bottom, "left": left},
        "face_size": {"width": right - left, "height": bottom - top}
    }

def verify_face_match(frame, reference_encoding, tolerance=0.55):
    """Verify if the face in the final frame matches the reference face encoding."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    live_encodings = face_recognition.face_encodings(rgb_frame)

    if not live_encodings:
        return False, 0.0, "No face detected in the final frame"
    if len(live_encodings) > 1:
        return False, 0.0, "Multiple faces detected"

    face_distances = face_recognition.face_distance([reference_encoding], live_encodings[0])
    match = bool(face_distances[0] <= tolerance)
    confidence = float(1.0 - min(face_distances[0], 1.0))
    
    message = "Success" if match else f"Face does not match (confidence: {confidence:.2f})"
    return match, confidence, message

