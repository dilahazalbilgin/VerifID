import cv2
import face_recognition


image = cv2.imread("E:\\opencv_udemy\\face_recognition\\images\\dila.jpg")

path = "E:\\opencv_udemy\\face_recognition\\images\\dilatest.jpg"#bu resmi referans olarak kullanıyoruz
reevesImage = face_recognition.load_image_file(path)

reevesFaceLoc = face_recognition.face_locations(reevesImage)
reevesImageEncoding = face_recognition.face_encodings(reevesImage)[0]#birden fazla yüz olursa o yüzün indeks numarasını gir

testPath = "E:\\opencv_udemy\\face_recognition\\images\\dila.jpg"
testImage = face_recognition.load_image_file(testPath)
faceLoc = face_recognition.face_locations(testImage)
testImageEncoding = face_recognition.face_encodings(testImage,faceLoc)[0]

matchedFaces = face_recognition.compare_faces([reevesImageEncoding], testImageEncoding)#

top, right, bottom, left = faceLoc[0]
if True in matchedFaces:
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.putText(image, "match", (left, top-10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
else:
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.putText(image, "no match", (left, top-10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0,255), 2)#

# Referans görüntüyü BGR formatına çevir (çünkü OpenCV bunu ister)
reevesImageBGR = cv2.cvtColor(reevesImage, cv2.COLOR_RGB2BGR)

# Referans yüzün konumunu kullan
ref_top, ref_right, ref_bottom, ref_left = reevesFaceLoc[0]
cv2.rectangle(reevesImageBGR, (ref_left, ref_top), (ref_right, ref_bottom), (255, 0, 0), 2)
cv2.putText(reevesImageBGR, "reference", (ref_left, ref_top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


cv2.imshow("reference", reevesImageBGR)
cv2.imshow("result", image)
cv2.waitKey(0)
cv2.destroyAllWindows()