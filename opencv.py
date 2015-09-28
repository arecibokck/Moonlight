import cv2
import numpy as np

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    ret, img = cap.read()
    img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("FSociety", img2)
    
    k=cv2.waitKey(10)
    if k==27:
        break

cap.release()
cv.destroyAllWindows()
