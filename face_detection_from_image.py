import face_recognition
import cv2

# Görüntüyü yükle
path = r"E:\opencv_udemy\face_recognition\images\super_yazilim1.jpg"
image = cv2.imread(path)

# OpenCV görüntüyü BGR olarak okur, face_recognition için RGB'ye çevir
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Yüzleri tespit et
face_locations = face_recognition.face_locations(rgb_image)

# Bulunan yüzlerin etrafına dikdörtgen çiz
for i, (top, right, bottom, left) in enumerate(face_locations):
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)  # Yeşil dikdörtgen
    cv2.putText(image, f"Face {i+1}: {top, right, bottom, left}", (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Değişken değerlerini OpenCV penceresinde göster
info_text = f"Faces Detected: {len(face_locations)}"
cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

# Görüntüyü göster
cv2.imshow("Yüz Tespiti", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
