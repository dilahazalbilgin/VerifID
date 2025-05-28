import cv2
import pytesseract

# Tesseract OCR konfigürasyonu
custom_config = r'--oem 3 --psm 6 -l tur+eng'

# Kamera başlatma
cap = cv2.VideoCapture(0)

# Video kaydedici başlatma
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('kamera_kaydi.avi', fourcc, 20.0, (640, 480))

print("📷 Kamera başlatıldı. 'q' tuşuna basınca kare okunacak...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera hatası!")
        break

    # Görüntüyü griye çevir
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Kontrastı artırmak için histogram eşitleme
    gray = cv2.equalizeHist(gray)

    # OCR işlemi (gri görüntü üzerinden)
    text = pytesseract.image_to_string(gray, config=custom_config)
    print("Tanınan Metin: ", text)

    # Video kaydı (orijinal renkli görüntü kaydediliyor)
    out.write(frame)

    # Görüntüyü ekranda göster (gri görüntü)
    cv2.imshow("Görüntü", gray)

    # Çıkış için 'q' tuşuna basılması beklenir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
out.release()
cv2.destroyAllWindows()
