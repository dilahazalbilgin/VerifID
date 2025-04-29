import cv2
import pytesseract

try:
    image_path = r"C:\Users\Monster\Desktop\workworkworkworkwork\AdvancedPrograming\1_3LHUQh52gLaSx0Zsnrr_xA.webp" 
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Resim bulunamadı: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang="tur")
    print("Tespit Edilen Metin:\n", text)
except Exception as e:
    print("Hata oluştu:", e)
