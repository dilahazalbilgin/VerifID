import cv2
import face_recognition
import os
import base64
import numpy as np
from PIL import Image
import io
import random

def base64_to_image(base64_string):
    """Convert base64 string to OpenCV image"""
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1] #
    
    img_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_data))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) #

def image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image) #
    return base64.b64encode(buffer).decode('utf-8') #

def get_reference_face_encoding(user_id):
    """
    Get reference face encoding from the face_info folder.
    Returns the encoding directly, or None if an error occurs.
    Prints error messages to console.
    """
    # Path to face_info folder
    face_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'face_info') #
    face_path = os.path.join(face_info_dir, f"{user_id}.jpg")

    if not os.path.exists(face_path):
        print(f"[ERROR] Reference face not found for user {user_id} at {face_path}")
        return None

    try:
        reference_image = face_recognition.load_image_file(face_path)
        reference_encodings = face_recognition.face_encodings(reference_image)

        if not reference_encodings:
            print(f"[ERROR] No face found in reference image for user {user_id} at {face_path}")
            return None
        
        print(f"[INFO] Reference face encoding loaded for user {user_id}")
        return reference_encodings[0]
    except Exception as e:
        print(f"[ERROR] Could not load or encode reference face for user {user_id}: {str(e)}")
        return None

def process_liveness_frame(frame, reference_center_x, command_to_check, face_detection_threshold=40):
    """
    Process a single frame for liveness detection based on face displacement.
    Args:
        frame: The input image frame (OpenCV BGR format).
        reference_center_x: The initial center X-coordinate of the face.
        command_to_check: The expected movement command (e.g., 'left', 'right', 'center').
        face_detection_threshold: Pixel difference to detect movement (increased for better accuracy).
    Returns:
        A dictionary with detection results.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        return {
            "face_detected": False,
            "movement_detected": None,
            "command_matched": False,
            "current_center_x": None,
            "error_message": "No face detected in frame"
        }

    # Check for multiple faces
    if len(face_locations) > 1:
        return {
            "face_detected": False,
            "movement_detected": None,
            "command_matched": False,
            "current_center_x": None,
            "error_message": "Multiple faces detected - please ensure only one person is in frame"
        }

    top, right, bottom, left = face_locations[0]
    current_center_x = (left + right) // 2
    face_width = right - left
    face_height = bottom - top
    frame_height, frame_width = rgb_frame.shape[:2]

    # Validate face size for consistent detection (relaxed standards)
    min_face_size = min(frame_width, frame_height) * 0.08  # Relaxed from 0.15
    max_face_size = min(frame_width, frame_height) * 0.95  # Relaxed from 0.8

    if face_width < min_face_size or face_height < min_face_size:
        return {
            "face_detected": False,
            "movement_detected": None,
            "command_matched": False,
            "current_center_x": current_center_x,
            "error_message": "Face too small - please move closer to camera"
        }

    if face_width > max_face_size or face_height > max_face_size:
        return {
            "face_detected": False,
            "movement_detected": None,
            "command_matched": False,
            "current_center_x": current_center_x,
            "error_message": "Face too large - please move away from camera"
        }

    # Calculate movement with improved thresholds
    movement_detected = "center"
    movement_distance = abs(current_center_x - reference_center_x)

    # Use adaptive threshold based on face size for better accuracy (more sensitive to faster movements)
    adaptive_threshold = max(face_detection_threshold, face_width * 0.15)

    # Also check with a smaller threshold for faster movements
    quick_threshold = max(25, face_width * 0.1)  # Even more sensitive threshold

    if current_center_x < reference_center_x - adaptive_threshold:
        movement_detected = "right"  # User looked to their right (face moved to screen's left)
    elif current_center_x > reference_center_x + adaptive_threshold:
        movement_detected = "left"   # User looked to their left (face moved to screen's right)
    elif current_center_x < reference_center_x - quick_threshold:
        movement_detected = "right"  # Catch faster movements with lower threshold
    elif current_center_x > reference_center_x + quick_threshold:
        movement_detected = "left"   # Catch faster movements with lower threshold

    command_matched = bool(command_to_check == movement_detected)  # Ensure Python bool

    print(f"[DEBUG] Movement detection - Current: {current_center_x}, Reference: {reference_center_x}, "
          f"Distance: {movement_distance}, Adaptive Threshold: {adaptive_threshold}, Quick Threshold: {quick_threshold}, "
          f"Detected: {movement_detected}, Expected: {command_to_check}, Matched: {command_matched}")

    return {
        "face_detected": True,
        "face_location": {"top": int(top), "right": int(right), "bottom": int(bottom), "left": int(left)},
        "current_center_x": int(current_center_x),
        "reference_center_x": int(reference_center_x),
        "movement_detected": str(movement_detected),
        "command_matched": bool(command_matched),
        "movement_distance": int(movement_distance),
        "threshold_used": float(adaptive_threshold),
        "face_size": {"width": int(face_width), "height": int(face_height)},
        "error_message": None
    }

def verify_face_match(frame, reference_encoding, tolerance=0.55):
    """
    Verify if the face in the frame matches the reference face encoding.
    Args:
        frame: The input image frame (OpenCV BGR format).
        reference_encoding: The encoding of the reference face.
        tolerance: Distance threshold for a match (lower is stricter).
    Returns:
        Tuple: (match_bool, confidence_score, error_message)
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    live_face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if not live_face_encodings:
        return False, 0.0, "No face detected in the live frame"

    # Check for multiple faces - security risk
    if len(live_face_encodings) > 1:
        return False, 0.0, "Multiple faces detected - please ensure only one person is in frame"

    # Validate face size for quality check
    if face_locations:
        top, right, bottom, left = face_locations[0]
        face_width = right - left
        face_height = bottom - top
        frame_height, frame_width = rgb_frame.shape[:2]

        # Face should be at least 10% of frame width and height for good quality (relaxed from 15%)
        min_face_size = min(frame_width, frame_height) * 0.10
        max_face_size = min(frame_width, frame_height) * 0.9  # Relaxed from 0.8

        if face_width < min_face_size or face_height < min_face_size:
            return False, 0.0, "Face too small - please move closer to camera"

        if face_width > max_face_size or face_height > max_face_size:
            return False, 0.0, "Face too large - please move away from camera"

    # Compare the detected live face with the reference encoding
    face_distances = face_recognition.face_distance([reference_encoding], live_face_encodings[0])

    match = bool(face_distances[0] <= tolerance)  # Ensure it's a Python bool, not numpy bool
    # Convert distance to a similarity score (0 to 1, higher is more similar)
    confidence = float(1.0 - min(face_distances[0], 1.0))  # Ensure it's a Python float

    # Additional confidence check - require minimum confidence (relaxed from 50% to 35%)
    if confidence < 0.35:  # Require at least 35% confidence
        return False, float(confidence), f"Face match confidence too low: {confidence:.2f}"

    print(f"[INFO] Face match result: {match}, confidence: {confidence:.3f}, distance: {face_distances[0]:.3f}")

    return match, float(confidence), "Success" if match else f"Face does not match (confidence: {confidence:.2f})"

def generate_random_liveness_commands(num_commands=3):
    """
    Generate a random sequence of liveness commands to prevent replay attacks.
    Args:
        num_commands: Number of commands to generate
    Returns:
        List of random commands
    """
    possible_commands = ['left', 'right', 'center']
    commands = []

    # Always start with center to establish reference
    commands.append('center')

    # Add random commands, ensuring no consecutive duplicates
    for i in range(num_commands - 1):
        available_commands = [cmd for cmd in possible_commands if cmd != commands[-1]]
        commands.append(random.choice(available_commands))

    print(f"[INFO] Generated random liveness commands: {commands}")
    return commands

def detect_face_blur(frame, face_location, threshold=50):
    """
    Detect if the face region is blurry (potential anti-spoofing measure).
    Args:
        frame: The input image frame (OpenCV BGR format).
        face_location: Tuple of (top, right, bottom, left) coordinates.
        threshold: Laplacian variance threshold for blur detection.
    Returns:
        Tuple: (is_clear, blur_score)
    """
    top, right, bottom, left = face_location
    face_region = frame[top:bottom, left:right]

    if face_region.size == 0:
        return False, 0

    # Convert to grayscale and calculate Laplacian variance
    gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()

    is_clear = blur_score > threshold
    print(f"[DEBUG] Face blur detection - Score: {blur_score:.2f}, Threshold: {threshold}, Clear: {is_clear}")

    return is_clear, blur_score

def validate_face_consistency(current_face_size, reference_face_size, tolerance=0.5):
    """
    Validate that the face size is consistent with the reference to prevent substitution.
    Args:
        current_face_size: Dict with 'width' and 'height' of current face
        reference_face_size: Dict with 'width' and 'height' of reference face
        tolerance: Allowed size variation (0.3 = 30%)
    Returns:
        Tuple: (is_consistent, size_difference)
    """
    if not reference_face_size:
        return True, 0  # No reference to compare against

    width_diff = abs(current_face_size['width'] - reference_face_size['width']) / reference_face_size['width']
    height_diff = abs(current_face_size['height'] - reference_face_size['height']) / reference_face_size['height']

    max_diff = max(width_diff, height_diff)
    is_consistent = max_diff <= tolerance

    print(f"[DEBUG] Face size consistency - Current: {current_face_size}, Reference: {reference_face_size}, "
          f"Max difference: {max_diff:.2f}, Tolerance: {tolerance}, Consistent: {is_consistent}")

    return is_consistent, max_diff