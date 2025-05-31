import face_recognition
import cv2

# Görüntüyü yükle
path = r"E:\opencv_udemy\face_recognition\videos\test3.mp4"
cap = cv2.VideoCapture(path)
color = (255,0,0)


while True:
    ret,frame = cap.read()

    faceLocations = face_recognition.face_locations(frame)

    for index, faceLoc in enumerate(faceLocations):
        topLeftY, bottomRightX, bottomRightY, topLeftX = faceLoc

        pt1=(topLeftX, topLeftY)
        pt2= (bottomRightX, bottomRightY)

        cv2.rectangle(frame, pt1,pt2,color)
    
    # Görüntüyü göster
    cv2.imshow("Yüz Tespiti", frame)

    if cv2.waitKey(1) &0xFF ==ord("q"):
        break



cap.release()
cv2.destroyAllWindows()


"""
import cv2
import face_recognition

cap = cv2.VideoCapture(0)
color = (0,255,0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame,1) #y eksenine göre çevirmke için yapıyoruz bunu, ayna görünümü elde etmek için

    faceLoactions = face_recognition.face_locations(frame)
    

"""

