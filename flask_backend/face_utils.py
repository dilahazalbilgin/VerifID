import cv2
import numpy as np
import base64
import io
from PIL import Image
import face_recognition # Ensure face_recognition is imported

# The line 'import face_recognition_models' and 'print(face_recognition_models.pose_predictor_model_location())'
# can be removed if not strictly needed for other functionalities, as face_recognition library handles model loading.

def base64_to_image(base64_string):
    """Convert base64 string to OpenCV image"""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1] #
    
    img_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_data))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) #

def detect_face_details(image):
    """
    Detects all faces in an image and returns their locations.
    Args:
        image: OpenCV BGR image.
    Returns:
        A list of face location dictionaries (top, right, bottom, left).
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image) #
    
    face_details_list = []
    for face_loc in face_locations:
        top, right, bottom, left = face_loc
        face_details_list.append({
            'left': int(left),
            'top': int(top),
            'right': int(right),
            'bottom': int(bottom)
        })
    return face_details_list


# The function `process_verification_step` from your original `face_utils.py`
# relies on face landmarks for orientation which can be complex.
# The liveness detection approach from `face_recognition3.py` (checking displacement of face center),
# which is now refined in `liveness_detection.py`, is simpler and often more effective for
# basic left/right/center movements.
# Thus, `process_verification_step` might be redundant for this specific liveness task.
# If you still need it for other purposes, it can be kept.

def capture_face_image_for_test():
    """Capture a face image from webcam (for testing purposes)"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return None, "Failed to open webcam" #
    
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return None, "Failed to capture image" #
    
    frame = cv2.flip(frame, 1) #
    
    # For testing, you can draw face locations
    face_locations = face_recognition.face_locations(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) #
    for face_loc in face_locations:
        top, right, bottom, left = face_loc
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2) #
    
    cap.release()
    return frame, "Success" #

# The `compare_faces` function in your original `face_utils.py` is similar to
# `verify_face_match` in `liveness_detection.py`.
# `liveness_detection.verify_face_match` is more direct for the liveness flow
# as it uses pre-computed encodings. If `face_utils.compare_faces` is used
# for other comparisons (e.g., ID card image directly against another image),
# it can be kept. For the liveness feature, `liveness_detection.verify_face_match`
# will be used in app.py.