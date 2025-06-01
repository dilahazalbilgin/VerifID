import cv2
import pytesseract
from pytesseract import Output
import re
import numpy as np
import string
import json
import base64
import traceback
from datetime import datetime # Import datetime for date parsing
import os

def extract_text_from_id(img, user_data=None):
    """Process ID card image and extract text information"""
    if img is None:
        return {"success": False, "message": "Invalid image"}

    # Image preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(filtered, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 15)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    preprocessed_image = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # OCR processing
    ocr_config = r'--oem 3 --psm 6 -l tur+eng'
    ocr_result = pytesseract.image_to_data(preprocessed_image, config=ocr_config, output_type=Output.DICT)

    detected_texts = []
    for i in range(len(ocr_result["text"])):
        text = ocr_result["text"][i].strip()
        if float(ocr_result["conf"][i]) > 10 and text != "":
            detected_texts.append(text)

    full_text = ' '.join(detected_texts)
    full_text_lower = full_text.lower()

    # Initialize ID card information
    id_card_info = {
        "id_number": "(bulunamadı)",
        "surname": "(bulunamadı)",
        "name": "(bulunamadı)",
        "birth_date": "(bulunamadı)",
        "gender": "(bulunamadı)",
        "serial_number": "(bulunamadı)",
        "nationality": "(bulunamadı)",
        "expiry_date": "(bulunamadı)"
    }

    # Extract ID card information using regex
    id_number_match = re.search(r'\b\d{11}\b', full_text)
    if id_number_match:
        id_card_info["id_number"] = id_number_match.group(0)

    birth_date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', full_text)
    if birth_date_match:
        id_card_info["birth_date"] = birth_date_match.group(0)

    serial_number_match = re.search(r'\b[A-Z]\d{2}[A-Z]\d{5}\b', full_text)
    if serial_number_match:
        id_card_info["serial_number"] = serial_number_match.group(0)

    all_dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', full_text)
    if len(all_dates) > 1:
        id_card_info["expiry_date"] = all_dates[1]

    def extract_name_surname_robustly(ocr_data_dict, detected_texts_list):
        surname_labels = ["soyadı", "surname", "soyad", "sunan"]
        name_labels = ["adı", "name", "given", "isim"]

        extracted_surname = "(bulunamadı)"
        extracted_name = "(bulunamadı)"
        
        for i in range(len(ocr_data_dict["text"])):
            word = ocr_data_dict["text"][i].strip()
            conf = float(ocr_data_dict["conf"][i])
            
            if conf > 60:
                lower_word = word.lower()
                
                if extracted_surname == "(bulunamadı)" and any(label in lower_word for label in surname_labels):
                    potential_words = []
                    for j in range(1, 4):
                        if i + j < len(ocr_data_dict["text"]):
                            next_word = ocr_data_dict["text"][i + j].strip(string.punctuation)
                            if len(next_word) > 1 and re.match(r'^[a-zA-ZçÇğĞıİöÖşŞüÜ\-\']+$', next_word):
                                potential_words.append(next_word)
                            else:
                                break
                    if potential_words:
                        extracted_surname = ' '.join(potential_words).upper()

                if extracted_name == "(bulunamadı)" and any(label in lower_word for label in name_labels):
                    potential_words = []
                    for j in range(1, 4):
                        if i + j < len(ocr_data_dict["text"]):
                            next_word = ocr_data_dict["text"][i + j].strip(string.punctuation)
                            if len(next_word) > 1 and re.match(r'^[a-zA-ZçÇğĞıİöÖşŞüÜ\-\']+$', next_word):
                                potential_words.append(next_word)
                            else:
                                break
                    if potential_words:
                        extracted_name = ' '.join(potential_words).upper()

        if extracted_surname == "(bulunamadı)" or extracted_name == "(bulunamadı)":
            potential_name_surname_candidates = []
            excluded_words = {"T.C.", "REPUBLIC", "TURKEY", "KIMLIK", "ID", "CARD", "TC", "AD", "SOYAD", "CINSİYET", "MILLIYETI", "DOĞUM"}
            
            for text in detected_texts_list:
                if text.isupper() and len(text) > 1 and not any(char.isdigit() for char in text) and text not in excluded_words:
                    potential_name_surname_candidates.append(text)
            
            if len(potential_name_surname_candidates) >= 2:
                if extracted_surname == "(bulunamadı)":
                    extracted_surname = potential_name_surname_candidates[0]
                if extracted_name == "(bulunamadı)":
                    extracted_name = potential_name_surname_candidates[1]
            elif len(potential_name_surname_candidates) == 1:
                if extracted_surname == "(bulunamadı)":
                    extracted_surname = potential_name_surname_candidates[0]
        
        return extracted_name, extracted_surname

    id_card_info["name"], id_card_info["surname"] = extract_name_surname_robustly(ocr_result, detected_texts)


    # Determine gender
    if re.search(r'\bK/?F\b', full_text, re.IGNORECASE):
        id_card_info["gender"] = "K/F"
    elif re.search(r'\bE/?M\b', full_text, re.IGNORECASE):
        id_card_info["gender"] = "E/M"

    # Determine nationality
    if "türk" in full_text_lower or "t.c" in full_text_lower:
        id_card_info["nationality"] = "T.C."

    # Extract face from ID card
    face_image_base64 = None
    try:
        import face_recognition
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            margin = 30
            top = max(0, top - margin)
            left = max(0, left - margin)
            bottom = min(img.shape[0], bottom + margin)
            right = min(img.shape[1], right + margin)

            face_image = img[top:bottom, left:right]
            _, buffer = cv2.imencode('.jpg', face_image)
            face_image_base64 = 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')
    except ImportError:
        print("Face_recognition library not found. Face extraction skipped.")
    except Exception as e:
        print(f"Error extracting face: {str(e)}")
        traceback.print_exc()

    # Create verification ID
    verification_id = "verify_" + str(abs(hash(str(id_card_info))))[:8]

    # Prepare response
    response = {
        "success": True,
        "message": "ID card processed successfully",
        "extracted_data": id_card_info,
        "verification_id": verification_id,
        "face_image": face_image_base64,
        "user_match": {
            "overall_match": False,
            "match_percentage": 0,
            "matches": []
        }
    }

    # Compare with user data if provided
    if user_data:
        try:
            user_data_dict = user_data if isinstance(user_data, dict) else json.loads(user_data)
            print(f"User data for matching: {user_data_dict}")

            matches = []
            match_count = 0
            total_fields_to_compare = 0 # Renamed for clarity

            # Define fields to compare and their corresponding extracted keys
            fields_to_check = {
                "serialNumber": "serial_number",
                "idNumber": "id_number",
                "birthDate": "birth_date",
                "gender": "gender"
            }

            for user_key, extracted_key in fields_to_check.items():
                if user_key in user_data_dict:
                    total_fields_to_compare += 1 # Count every field present in user_data for comparison

                    user_value = user_data_dict[user_key]
                    extracted_value = id_card_info[extracted_key]
                    current_match = False

                    if extracted_value == "(bulunamadı)":
                        # If extracted data is missing, it's a mismatch for this field
                        current_match = False
                        print(f"{user_key} match: False (Extracted data not found) - User: '{user_value}'")
                    else:
                        # Perform comparison based on the field type
                        if user_key == "gender":
                            user_gender_lower = user_value.lower().strip()
                            extracted_gender_normalized = extracted_value.lower().replace('/', '')
                            if (user_gender_lower == 'female' and ('k' in extracted_gender_normalized or 'f' in extracted_gender_normalized)) or \
                               (user_gender_lower == 'male' and ('e' in extracted_gender_normalized or 'm' in extracted_gender_normalized)):
                                current_match = True
                            print(f"Gender match: {current_match} - User: '{user_value}' vs Extracted: '{extracted_value}'")
                        
                        elif user_key == "birthDate":
                            # Frontend date format (2003-07-03T00:00:00.000Z) vs Extracted date format (03.07.2003)
                            try:
                                user_birth_date_str_iso = user_value.split('T')[0] # '2003-07-03'
                                user_birth_date_obj = datetime.strptime(user_birth_date_str_iso, '%Y-%m-%d')
                                user_birth_date_formatted = user_birth_date_obj.strftime('%d.%m.%Y')
                                current_match = user_birth_date_formatted == extracted_value.strip()
                            except (ValueError, AttributeError): # Handle if user_value is not a string or malformed
                                current_match = False # Date format mismatch or error
                            print(f"Birth Date match: {current_match} - User: '{user_value}' (formatted: '{user_birth_date_formatted}') vs Extracted: '{extracted_value}'")

                        else: # For serialNumber and idNumber
                            current_match = user_value.strip().upper() == extracted_value.strip().upper()
                            print(f"{user_key} match: {current_match} - User: '{user_value}' vs Extracted: '{extracted_value}'")
                    
                    matches.append([user_key, current_match])
                    if current_match:
                        match_count += 1

            # Calculate match percentage
            match_percentage = (match_count / total_fields_to_compare * 100) if total_fields_to_compare > 0 else 0

            response["user_match"] = {
                "overall_match": match_percentage >= 50, # You can adjust this threshold
                "match_percentage": match_percentage,
                "matches": matches
            }

            print(f"Match results: {match_count}/{total_fields_to_compare} fields matched ({match_percentage}%)")
            print(f"Final matches array: {matches}")

        except Exception as e:
            print(f"Error comparing user data: {str(e)}")
            traceback.print_exc()

    return response

def save_face_from_id_card(img, user_id):
    """
    Extract face from ID card image and save it to face_info directory
    
    Args:
        img: OpenCV image of the ID card
        user_id: User ID to use as filename
    
    Returns:
        bool: True if successful, False otherwise
        str: Path to saved face image or error message
    """
    try:
        # Create face_info directory if it doesn't exist
        face_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'face_info')
        os.makedirs(face_info_dir, exist_ok=True)
        
        # Extract face from ID card
        import face_recognition
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return False, "No face detected in ID card"
        
        # Get the first face with a larger margin
        top, right, bottom, left = face_locations[0]
        
        # Increase margin to make the extracted face bigger
        margin = 100
        
        # Calculate new boundaries with larger margins
        top = max(0, top - margin)
        left = max(0, left - margin)
        bottom = min(img.shape[0], bottom + margin)
        right = min(img.shape[1], right + margin)
        
        # Extract face image
        face_image = img[top:bottom, left:right]
        
        # Save face image to file
        file_path = os.path.join(face_info_dir, f"{user_id}.jpg")
        cv2.imwrite(file_path, face_image)
        
        print(f"Face image saved to {file_path}")
        return True, file_path
    except Exception as e:
        error_msg = f"Error saving face image: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg

