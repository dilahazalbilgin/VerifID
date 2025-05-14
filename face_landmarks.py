import face_recognition
from PIL import Image, ImageDraw
#from PIL.ImageDraw import ImageDraw

path = "E:/opencv_udemy/face_recognition/images/eje.jpg"
image = face_recognition.load_image_file(path)

landmarks = face_recognition.face_landmarks(image) #landmarks içinde dictionary tutan bir liste

PILImage = Image.fromarray(image)
d =ImageDraw.Draw(PILImage)

for landmark in landmarks:#burada bu listeyi tek tek dolaşıyoruz
    for feature in landmark.keys():
        d.line(landmark[feature], width=3)

PILImage.show()