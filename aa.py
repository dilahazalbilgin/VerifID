import cv2
import pytesseract
from pytesseract import Output
import re
import numpy as np
import matplotlib.pyplot as plt


img_path = r"C:\Users\Monster\Desktop\workworkworkworkwork\AdvancedPrograming\a.jpg"
img = cv2.imread(img_path)

img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
img = cv2.filter2D(img, -1, kernel)


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


custom_config = r'--oem 1 --psm 6 -l tur+eng'
data = pytesseract.image_to_data(thresh, config=custom_config, output_type=Output.DICT)

detected_texts = []
full_text = ""

# Kutular çiz ve metinleri topla
for i in range(len(data['text'])):
    word = data['text'][i].strip()
    conf = float(data['conf'][i])
    if word != "" and conf > 10:
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, word, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        detected_texts.append(word)
        full_text += word + " "

# Bilgi çıkarımı
kimlik_bilgileri = {
    "TC Kimlik No": re.search(r'\b\d{11}\b', full_text),
    "Soyadı": "(bulunamadı)",
    "Adı": "(bulunamadı)",
    "Doğum Tarihi": re.search(r'\d{2}\.\d{2}\.\d{4}', full_text),
    "Cinsiyet": "(bulunamadı)",
    "Seri No": re.search(r'[A-Z]{1,3}\d{5,}', full_text),
    "Uyruğu": "(bulunamadı)",
    "Son Geçerlilik": re.findall(r'\d{2}\.\d{2}\.\d{4}', full_text)
}

# Regex match varsa düzelt
for key in ["TC Kimlik No", "Doğum Tarihi", "Seri No"]:
    if isinstance(kimlik_bilgileri[key], re.Match):
        kimlik_bilgileri[key] = kimlik_bilgileri[key].group(0)
    else:
        kimlik_bilgileri[key] = "(bulunamadı)"

kimlik_bilgileri["Son Geçerlilik"] = kimlik_bilgileri["Son Geçerlilik"][-1] if len(kimlik_bilgileri["Son Geçerlilik"]) > 1 else "(bulunamadı)"

# Ad ve Soyad
for i in range(len(detected_texts)):
    kelime = detected_texts[i].lower()
    if "soyadı" in kelime or "surname" in kelime:
        if i + 1 < len(detected_texts):
            kimlik_bilgileri["Soyadı"] = detected_texts[i + 1]
    elif "adı" in kelime or "given" in kelime:
        if i + 1 < len(detected_texts):
            kimlik_bilgileri["Adı"] = detected_texts[i + 1]

# Cinsiyet tespiti
if re.search(r'\bK/?F\b', full_text):
    kimlik_bilgileri["Cinsiyet"] = "K/F"
elif re.search(r'\bE/?M\b', full_text):
    kimlik_bilgileri["Cinsiyet"] = "E/M"

# Uyruğu tespiti
if "t.c" in full_text.lower() or "tur" in full_text.lower():
    kimlik_bilgileri["Uyruğu"] = "T.C."

# Sonuçları yazdır
print("\n--- Çıktı ---")
for key, value in kimlik_bilgileri.items():
    print(f"{key}: {value}")

print("\n--- Tanınan Kelimeler ---")
print(detected_texts)

print("\n--- OCR Tüm Metin ---")
print(full_text)

# Görsel göster
plt.figure(figsize=(14, 14))
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title("OCR Kutulama Sonucu")
plt.show()
