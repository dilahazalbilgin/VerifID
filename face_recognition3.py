"""import cv2
import face_recognition
import pyttsx3
import time

# Sesli motor başlat
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print(f"[🔊] {text}")
    engine.say(text)
    engine.runAndWait()

# 1. Referans fotoğrafı yükle (aynı klasörde olmalı)
reference_image_path = "E:\\opencv_udemy\\face_recognition\\images\\eje2.png"
reference_image = face_recognition.load_image_file(reference_image_path)
reference_encodings = face_recognition.face_encodings(reference_image)

if not reference_encodings:
    print("[ERROR] Referans fotoğrafında yüz bulunamadı.")
    exit()

reference_encoding = reference_encodings[0]
print("[INFO] Referans fotoğraf yüklendi.")

# 2. Kamera başlat
cap = cv2.VideoCapture(0)
time.sleep(2)

# 3. Yüzü merkezleyerek başlangıç X koordinatını belirle
print("[INFO] Yüz merkezi pozisyonu belirleniyor...")
reference_center_x = None
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb)
    if faces:
        top, right, bottom, left = faces[0]
        reference_center_x = (left + right) // 2
        print(f"[INFO] Yüz X referans merkezi: {reference_center_x}")
        speak("Face detected. Let's start.")
        break

# 4. Liveness komut sırası
expected_sequence = ['right', 'center', 'left']
movement_sequence = []
threshold = 50  # piksel farkı toleransı

for command in expected_sequence:
    speak(f"Please look {command}")
    print(f"[➡️] Komut bekleniyor: {command}")
    command_given_time = time.time()
    detected = False

    while time.time() - command_given_time < 7:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)

        if faces:
            top, right, bottom, left = faces[0]
            current_center_x = (left + right) // 2

            movement = "center"
            if current_center_x < reference_center_x - threshold:
                movement = "right"  # ekranın sol tarafı → kullanıcının SAĞI
            elif current_center_x > reference_center_x + threshold:
                movement = "left"   # ekranın sağ tarafı → kullanıcının SOLU

            cv2.putText(frame, f"Detected: {movement}", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if movement == command:
                print(f"[✓] Doğru hareket: {movement}")
                movement_sequence.append(movement)
                detected = True
                break

        cv2.imshow("Liveness Detection", frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

        if detected:
            break

# 5. Liveness sonucu
if movement_sequence == expected_sequence:
    speak("Liveness check passed. Thank you.")
    print("[✅] Canlılık testi başarıyla tamamlandı.")

    # 6. Yüz karşılaştırması yap
    ret, final_frame = cap.read()
    if ret:
        cv2.imwrite("liveness_success.jpg", final_frame)
        print("[📸] Son kare kaydedildi.")

        final_rgb = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
        live_encodings = face_recognition.face_encodings(final_rgb)

        if live_encodings:
            live_encoding = live_encodings[0]
            match_result = face_recognition.compare_faces([reference_encoding], live_encoding)[0]

            if match_result:
                print("[🎉] Yüz eşleşti. Kimlik doğrulandı.")
                speak("Face match successful. Identity verified.")
            else:
                print("[⚠️] Yüz eşleşmesi başarısız.")
                speak("Face does not match the reference image.")
        else:
            print("[❌] Yüz tespit edilemedi.")
            speak("No face detected in the final frame.")
else:
    print("[❌] Liveness test failed.")
    speak("Liveness check failed.")

cap.release()
cv2.destroyAllWindows()
"""
import cv2
import face_recognition
import time
import pyttsx3

# Sesli konuşma motoru başlat
engine = pyttsx3.init()
engine.setProperty('rate', 150)


def speak(text):
    print(f"[🔊] {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass  # bazı sistemlerde kasma yapabiliyor, engelliyoruz


# Kamera başlat (düşük çözünürlük)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Referans yüzü yükle
reference_image_path = "E:\\opencv_udemy\\face_recognition\\images\\enescan.jpg"
reference_image = face_recognition.load_image_file(reference_image_path)
reference_encodings = face_recognition.face_encodings(reference_image)
if not reference_encodings:
    print("[ERROR] Referans yüz bulunamadı!")
    cap.release()
    exit()
reference_encoding = reference_encodings[0]
print("[INFO] Referans fotoğraf yüklendi.")

# Liveness testi parametreleri
commands = ['right', 'center', 'left']
movements_done = []
face_center_x = None
required_movements = 3
frame_count = 0

# Ana döngü
print("[INFO] Yüz merkezi pozisyonu belirleniyor...")
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)

    if face_locations:
        top, right, bottom, left = face_locations[0]
        face_center_x = (left + right) // 2
        print(f"[INFO] Yüz X referans merkezi: {face_center_x}")
        speak("Face detected. Let's start.")
        break

cv2.waitKey(500)

# Hareketleri sırayla iste
for command in commands:
    speak(f"Please look {command}")
    print(f"[➡️] Komut bekleniyor: {command}")
    detected = False
    start_time = time.time()

    while time.time() - start_time < 7:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if frame_count % 3 == 0:  # sadece her 3 karede bir işlem yap
            face_locations = face_recognition.face_locations(rgb)

            if face_locations:
                top, right, bottom, left = face_locations[0]
                current_x = (left + right) // 2

                if face_center_x:
                    movement = None
                    if current_x < face_center_x - 40:
                        movement = 'right'  # kullanıcının SAĞI → ekranın SOLU
                    elif current_x > face_center_x + 40:
                        movement = 'left'  # kullanıcının SOLU → ekranın SAĞI
                    else:
                        movement = 'center'

                    cv2.putText(frame, f"Detected: {movement}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    if movement == command:
                        print(f"[✓] Doğru hareket: {movement}")
                        movements_done.append(movement)
                        detected = True
                        break

        if frame_count % 2 == 0:
            cv2.imshow("Liveness Detection", frame)
        frame_count += 1

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    if not detected:
        print(f"[!] {command} hareketi algılanamadı.")

# Canlılık testi tamamlandıysa devam et
if len(movements_done) == required_movements:
    speak("Liveness check passed. Thank you.")
    print("[✅] Canlılık testi başarıyla tamamlandı.")

    # Ekran görüntüsü al
    ret, final_frame = cap.read()
    if ret:
        cv2.imwrite("liveness_success.jpg", final_frame)
        print("[📸] Son kare kaydedildi.")

        # Karşılaştırma
        live_encodings = face_recognition.face_encodings(final_frame)
        if live_encodings:
            match_result = face_recognition.compare_faces([reference_encoding], live_encodings[0])[0]
            if match_result:
                print("[🎉] Yüz eşleşti. Kimlik doğrulandı.")
                speak("Face match successful. Identity verified.")
            else:
                print("[❌] Yüz eşleşmedi. Kimlik doğrulanamadı.")
                speak("Face does not match. Identity not verified.")
        else:
            print("[⚠️] Canlı yüz algılanamadı.")
else:
    print("[❌] Canlılık testi başarısız.")

cap.release()
cv2.destroyAllWindows()

