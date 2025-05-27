import cv2
import pytesseract
from pytesseract import Output
import re
import matplotlib.pyplot as plt
import numpy as np
import string

img_path = r"C:\Users\Monster\Desktop\workworkworkworkwork\AdvancedPrograming\a.jpg"

img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError("Görsel bulunamadı.")

# 2. Filtreleme işlemi (Görüntü iyileştirme)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Griye çevir

# Gürültü azaltma (bilateral filter detayları korur)
filtered = cv2.bilateralFilter(gray, 11, 17, 17)

# Adaptif eşikleme
thresh = cv2.adaptiveThreshold(filtered, 255,
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 15)

# Kenarları belirginleştirme (morfolojik işlem)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
preprocessed_image = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# 3. OCR İşlemi
myconfig = r'--oem 3 --psm 6 -l tur+eng'
data = pytesseract.image_to_data(preprocessed_image, config=myconfig, output_type=Output.DICT)

detected_texts = []

# 4. OCR sonucuna göre kutular çiz
for i in range(len(data['text'])):
    text = data['text'][i].strip()
    if float(data['conf'][i]) > 10 and text != "":
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(preprocessed_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        detected_texts.append(text)

# 5. OCR'dan gelen kelimeleri birleştir
full_text = ' '.join(detected_texts)

# 6. Kimlik bilgilerini ayıkla
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

# Regex sonuçlarını düz metne dönüştür
for key in ["TC Kimlik No", "Doğum Tarihi", "Seri No"]:
    if isinstance(kimlik_bilgileri[key], re.Match):
        kimlik_bilgileri[key] = kimlik_bilgileri[key].group(0)
    else:
        kimlik_bilgileri[key] = "(bulunamadı)"

kimlik_bilgileri["Son Geçerlilik"] = kimlik_bilgileri["Son Geçerlilik"][1] if len(kimlik_bilgileri["Son Geçerlilik"]) > 1 else "(bulunamadı)"

# 7. Ad ve Soyadı için gelişmiş ayıklama
def sec_kelime_grubu(detected_texts, etiketler, max_ilerleme=3):
    for i in range(len(detected_texts)):
        kelime = detected_texts[i].lower()
        if any(etiket in kelime for etiket in etiketler):
            kelime_grubu = []
            for j in range(1, max_ilerleme + 1):
                if i + j < len(detected_texts):
                    sonraki = detected_texts[i + j]
                    temiz = sonraki.strip(string.punctuation)
                    if temiz.isalpha() and len(temiz) > 1:
                        kelime_grubu.append(temiz)
            if kelime_grubu:
                return ' '.join(kelime_grubu)
    return "(bulunamadı)"

kimlik_bilgileri["Soyadı"] = sec_kelime_grubu(detected_texts, ["soyadı", "surname", "sunan"])
kimlik_bilgileri["Adı"] = sec_kelime_grubu(detected_texts, ["adı", "name", "given"])

# 8. Cinsiyet kontrolü
if re.search(r'\bK/?F\b', full_text, re.IGNORECASE):
    kimlik_bilgileri["Cinsiyet"] = "K/F"
elif re.search(r'\bE/?M\b', full_text, re.IGNORECASE):
    kimlik_bilgileri["Cinsiyet"] = "E/M"

# 9. Uyruğu kontrolü
full_text_lower = full_text.lower()
if "türk" in full_text_lower or "t.c" in full_text_lower:
    kimlik_bilgileri["Uyruğu"] = "T.C."

# 10. Sonuçları Yazdır
print("\n--- Çıktı ---")
for key, value in kimlik_bilgileri.items():
    print(f"{key}: {value}")

print("\n--- Tanınan Kelimeler ---")
print(detected_texts)

# 11. Görseli Göster (isteğe bağlı)
plt.figure(figsize=(10, 10))
plt.imshow(preprocessed_image, cmap='gray')
plt.axis('off')
plt.title("Filtrelenmiş Görüntü (OCR Öncesi)")
plt.show()
