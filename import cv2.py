import cv2

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Koordinat: x={x}, y={y}")

img = cv2.imread(r"C:\Users\Monster\Desktop\workworkworkworkwork\AdvancedPrograming\css_ile_kimlik_karti_tasarimi.jpeg")  # yolu düzelt
cv2.imshow("Resme Tikla", img)
cv2.setMouseCallback("Resme Tikla", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
