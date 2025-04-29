import cv2
import pytesseract
import re

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Görseli oku
img = cv2.imread(r"C:\Users\Monster\Desktop\workworkworkworkwork\AdvancedPrograming\css_ile_kimlik_karti_tasarimi.jpeg")

# Ön işleme (griye çevir + threshold)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# OCR çalıştır
custom_config = r'--oem 3 --psm 6 -l tur'
text = pytesseract.image_to_string(thresh, config=custom_config)

# OCR çıktısını yazdır
print("OCR Çıktısı:\n", text)

# Regex ile bilgiler
tc_kimlik_no = re.search(r'\b\d{11}\b', text)
dogum_tarihi = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
seri_no = re.search(r'[A-Z]{1,3}\d{5,}', text)

# Alanları başta boş olarak tanımlayalım
kimlik_bilgileri = {
    "TC Kimlik No": tc_kimlik_no.group(0) if tc_kimlik_no else "(bulunamadı)",
    "Soyadı": "(bulunamadı)",
    "Adı": "(bulunamadı)",
    "Doğum Tarihi": dogum_tarihi.group(0) if dogum_tarihi else "(bulunamadı)",
    "Cinsiyet": "(bulunamadı)",
    "Seri No": seri_no.group(0) if seri_no else "(bulunamadı)",
    "Uyruğu": "(bulunamadı)",
    "Son Geçerlilik": "(bulunamadı)"
}

# OCR çıktısında satır satır arama yap
lines = text.split('\n')
for idx, line in enumerate(lines):
    line_lower = line.lower()

    if "soyadı" in line_lower or "surname" in line_lower:
        if idx + 1 < len(lines):
            kimlik_bilgileri["Soyadı"] = lines[idx + 1].strip()

    if "adı" in line_lower or "name" in line_lower:
        if idx + 1 < len(lines):
            kimlik_bilgileri["Adı"] = lines[idx + 1].strip()

    if "cinsiyet" in line_lower or "gender" in line_lower:
        if idx + 1 < len(lines):
            kimlik_bilgileri["Cinsiyet"] = lines[idx + 1].strip()

    if "uyruğu" in line_lower or "nationality" in line_lower:
        if idx + 1 < len(lines):
            kimlik_bilgileri["Uyruğu"] = lines[idx + 1].strip()

    if "son geçerlilik" in line_lower or "valid until" in line_lower:
        if idx + 1 < len(lines):
            kimlik_bilgileri["Son Geçerlilik"] = lines[idx + 1].strip()

# Düzenleme fonksiyonları

def temizle_cinsiyet(veri):
    veri = veri.lower()
    if "erkek" in veri:
        return "Erkek"
    elif "kadın" in veri:
        return "Kadın"
    elif "male" in veri:
        return "Male"
    elif "female" in veri:
        return "Female"
    else:
        return "(bulunamadı)"

def temizle_uyruk(veri):
    match = re.search(r'(T\.C\.|TUR|TCTUR|T\.C\. TUR)', veri, re.IGNORECASE)
    return match.group(0) if match else "(bulunamadı)"

# Verileri düzenle
kimlik_bilgileri["Cinsiyet"] = temizle_cinsiyet(kimlik_bilgileri["Cinsiyet"])
kimlik_bilgileri["Uyruğu"] = temizle_uyruk(kimlik_bilgileri["Uyruğu"])


# Sonuçları yazdır
print("\n--- Çıktı ---")
for key, value in kimlik_bilgileri.items():
    print(f"{key}: {value}")
