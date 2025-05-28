"""referans fotoğrafı yükleyip encoding hazırla
webcam aç
her frame içinde yüz bul ,encoding yap, eşleşiyosa match yaz, eşleşmiyorsa no match yaz"""

import cv2
import face_recognition

ref_image_path= "E:\\opencv_udemy\\face_recognition\\images\\eje2.png"
reference_image = face_recognition.load_image_file(ref_image_path)
reference_encoding = face_recognition.face_encodings(reference_image)[0]

video_capture=cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for(top, right,bottom, left), face_encoding in zip(face_locations, face_encodings):#zipli ifade ilk yüzün kordinatını ve encodingini beraber almasını, sonra ikinci yüzün koordinatını ve encodingini be3raber almasını sağlar
         #reference_encoding → tek bir encoding (128 değerlik numpy array)
        #compare_faces → birden çok referans encoding olabileceğini varsayıyor → liste ister.
        matches = face_recognition.compare_faces([reference_encoding], face_encoding)

        if True in matches:
            label = "match"
            color = (0, 255, 0)

        else:
            label = "not match"
            color = (0, 0, 255)

        cv2.rectangle(frame,(left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("webcam face recognition", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()