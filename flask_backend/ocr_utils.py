import cv2
import pytesseract
from pytesseract import Output
import re
import numpy as np
import string
import json
import base64

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
    
    # OCR processing
    ocr_config = r'--oem 3 --psm 11 -l tur+eng'
    ocr_result = pytesseract.image_to_data(thresh, config=ocr_config, output_type=Output.DICT)
    
    # Extract text from OCR result
    detected_texts = []
    for i in range(len(ocr_result["text"])):
        if int(ocr_result["conf"][i]) > 30:  # Filter by confidence
            text = ocr_result["text"][i].strip()
            if len(text) > 1:  # Filter out single characters
                detected_texts.append(text)
    
    # Combine all detected text
    full_text = ' '.join(detected_texts)
    
    # Helper function to extract text after specific labels
    def extract_field_after_label(texts, labels, max_steps=3):
        for i in range(len(texts)):
            word = texts[i].lower()
            if any(label in word for label in labels):
                field_value = []
                for j in range(1, max_steps + 1):
                    if i + j < len(texts):
                        next_word = texts[i + j]
                        clean = next_word.strip(string.punctuation)
                        if clean.isalpha() and len(clean) > 1:
                            field_value.append(clean)
                if field_value:
                    return ' '.join(field_value)
        return "(bulunamadı)"
    
    # Extract ID card information
    id_card_info = {
        "id_number": re.search(r'\b\d{11}\b', full_text),
        "surname": "(bulunamadı)",
        "name": "(bulunamadı)",
        "birth_date": re.search(r'\d{2}\.\d{2}\.\d{4}', full_text),
        "gender": "(bulunamadı)",
        "serial_number": re.search(r'[A-Z]{1,3}\d{5,}', full_text),
        "nationality": "(bulunamadı)",
        "expiry_date": re.findall(r'\d{2}\.\d{2}\.\d{4}', full_text)
    }
    
    # Convert regex matches to strings
    for key in ["id_number", "birth_date", "serial_number"]:
        if isinstance(id_card_info[key], re.Match):
            id_card_info[key] = id_card_info[key].group(0)
        else:
            id_card_info[key] = "(bulunamadı)"
    
    # Handle expiry date (usually the second date on the card)
    id_card_info["expiry_date"] = id_card_info["expiry_date"][1] if len(id_card_info["expiry_date"]) > 1 else "(bulunamadı)"
    
    # Extract name and surname
    id_card_info["surname"] = extract_field_after_label(detected_texts, ["soyadı", "surname", "sunan"])
    id_card_info["name"] = extract_field_after_label(detected_texts, ["adı", "name", "given"])
    
    # Determine gender
    if re.search(r'\bK/?F\b', full_text, re.IGNORECASE):
        id_card_info["gender"] = "K/F"
    elif re.search(r'\bE/?M\b', full_text, re.IGNORECASE):
        id_card_info["gender"] = "E/M"
    
    # Determine nationality
    if "türk" in full_text.lower() or "t.c" in full_text.lower():
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
    except Exception as e:
        print(f"Error extracting face: {str(e)}")
    
    # Create verification ID
    verification_id = "verify_" + str(hash(str(id_card_info)))[:8]
    
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
            total_fields = 0
            
            # Compare name
            if 'name' in user_data_dict and id_card_info['name'] != "(bulunamadı)":
                total_fields += 1
                name_match = user_data_dict['name'].lower() in id_card_info['name'].lower()
                matches.append(["name", name_match])
                if name_match:
                    match_count += 1
                print(f"Name match: {name_match} - '{user_data_dict['name']}' vs '{id_card_info['name']}'")
            
            # Compare surname
            if 'surname' in user_data_dict and id_card_info['surname'] != "(bulunamadı)":
                total_fields += 1
                user_surname = user_data_dict['surname'].lower()
                extracted_surname = id_card_info['surname'].lower()
                
                surname_match = (
                    user_surname in extracted_surname or
                    extracted_surname in user_surname or
                    user_surname.replace('i', 'ı') in extracted_surname or
                    user_surname.replace('ı', 'i') in extracted_surname
                )
                
                matches.append(["surname", surname_match])
                if surname_match:
                    match_count += 1
                print(f"Surname match: {surname_match} - '{user_surname}' vs '{extracted_surname}'")
            
            # Compare ID number
            if 'idCardNumber' in user_data_dict and id_card_info['id_number'] != "(bulunamadı)":
                total_fields += 1
                id_match = user_data_dict['idCardNumber'] == id_card_info['id_number']
                matches.append(["idCardNumber", id_match])
                if id_match:
                    match_count += 1
                print(f"ID match: {id_match} - '{user_data_dict['idCardNumber']}' vs '{id_card_info['id_number']}'")
            
            # Compare gender
            if 'gender' in user_data_dict and id_card_info['gender'] != "(bulunamadı)":
                total_fields += 1
                gender_match = False
                if user_data_dict['gender'].lower() == 'female' and id_card_info['gender'] == 'K/F':
                    gender_match = True
                elif user_data_dict['gender'].lower() == 'male' and id_card_info['gender'] == 'E/M':
                    gender_match = True
                matches.append(["gender", gender_match])
                if gender_match:
                    match_count += 1
                print(f"Gender match: {gender_match} - '{user_data_dict['gender']}' vs '{id_card_info['gender']}'")
            
            # Calculate match percentage
            match_percentage = (match_count / total_fields * 100) if total_fields > 0 else 0
            
            # Update response with match data
            response["user_match"] = {
                "overall_match": match_percentage >= 50,
                "match_percentage": match_percentage,
                "matches": matches
            }
            
            print(f"Match results: {match_count}/{total_fields} fields matched ({match_percentage}%)")
            print(f"Final matches array: {matches}")
            
        except Exception as e:
            print(f"Error comparing user data: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return response

def extract_face_from_id(image):
    """Extract face from ID card image with a larger margin"""
    try:
        import face_recognition
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return None
        
        top, right, bottom, left = face_locations[0]
        
        face_height = bottom - top
        face_width = right - left
        
        margin_vertical = int(face_height * 0.5)
        margin_horizontal = int(face_width * 0.5)
        
        top = max(0, top - margin_vertical)
        left = max(0, left - margin_horizontal)
        bottom = min(image.shape[0], bottom + margin_vertical)
        right = min(image.shape[1], right + margin_horizontal)
        
        face_image = image[top:bottom, left:right]
        
        return face_image
    except Exception as e:
        print(f"Error extracting face: {str(e)}")
        return None

def levenshtein_distance(s1, s2):
    """Calculate the Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]