import cv2
import pytesseract
from pytesseract import Output
import re
import matplotlib.pyplot as plt

img_path = r"C:\Users\Monster\Desktop\workworkworkworkwork\AdvancedPrograming\a.jpg"

img = cv2.imread(img_path)


myconfig = r'--oem 3 --psm 6 -l tur'

data = pytesseract.image_to_data(img, config=myconfig, output_type=Output.DICT)


detected_texts = []

# Metin tespiti ve kutu çizme
for i in range(len(data['text'])):
    text = data['text'][i].strip()
    if float(data['conf'][i]) > 10 and text != "":
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        detected_texts.append(text)

# Görseli göster
plt.figure(figsize=(10,10))
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title("OCR ile Seçilen Metinler")
plt.show()

# OCR'dan gelen kelimeleri birleştir
full_text = ' '.join(detected_texts)

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

# Soyadı ve Adı için daha sağlam kontrol
for i in range(len(detected_texts)):
    kelime = detected_texts[i].lower()
    if "soyadı" in kelime or "surname" in kelime:
        if i + 1 < len(detected_texts):
            kimlik_bilgileri["Soyadı"] = detected_texts[i + 1]
    elif "adı" in kelime or "name" in kelime:
        if i + 1 < len(detected_texts):
            kimlik_bilgileri["Adı"] = detected_texts[i + 1]


if re.search(r'\bK/?F\b', full_text, re.IGNORECASE):
    kimlik_bilgileri["Cinsiyet"] = "K/F"
elif re.search(r'\bE/?M\b', full_text, re.IGNORECASE):
    kimlik_bilgileri["Cinsiyet"] = "E/M"


full_text_lower = full_text.lower()
if "türk" in full_text_lower:
    kimlik_bilgileri["Uyruğu"] = "T.C."


seri_no = re.search(r'[A-Z]{1,3}\d{5,}', full_text)
if seri_no:
    kimlik_bilgileri["Seri No"] = seri_no.group(0)
else:
    kimlik_bilgileri["Seri No"] = "(bulunamadı)"

# Terminal çıktısı
print("\n--- Çıktı ---")
for key, value in kimlik_bilgileri.items():
    print(f"{key}: {value}")

# Tanınan Kelimeler
print("\n--- Tanınan Kelimeler ---")
print(detected_texts)
