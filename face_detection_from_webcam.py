import cv2
import  face_recognition

#from face_recognition.codes.face_detection_from_videos import topLeftY, bottomRightX, bottomRightY, topLeftX

cap = cv2.VideoCapture(0)#bilgisayarın kamerasına bağlanmak için 0  diyoruz, 1ve 2 harici kameralar için kullanıyoruz
color = (0, 255, 0)

while True:
    ret, frame = cap.read()#frame alınan görüntü, ret: görüntü başarılı şekilde alındı mı onu gösterir
    frame = cv2.flip(frame, 1)  # y eksenine göre çevirmke için yapıyoruz bunu, ayna görünümü elde etmek için

    faceLocations = face_recognition.face_locations(frame)# görüntüdeki yzüleri ararız

    for index, faceLoc in enumerate(faceLocations):#liste içindeki öğeleri tek tek almak için, hem de onların sırasını bilmek için kullanılır
        topLeftY, bottomRightX, bottomRightY, topLeftX = faceLoc
        pt1 = (topLeftX, topLeftY)#sol üst
        pt2 = (bottomRightX, bottomRightY)#sağ alt

        cv2.rectangle(frame, pt1, pt2, color)

        cv2.imshow("Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()