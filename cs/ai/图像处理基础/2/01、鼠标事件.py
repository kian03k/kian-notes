import cv2
import numpy as np

# events = [i for i in dir(cv2) if 'EVENT' in i]
# print(events)


def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img,(x,y),20,(0,0,255))
    elif  event == cv2.EVENT_RBUTTONDBLCLK:
        cv2.circle(img, (x, y), 20, (0, 255, 0))



img = np.zeros((500,500,3))
cv2.imshow('img',img)
cv2.setMouseCallback('img',draw_circle)

while True:
    cv2.imshow('img',img)
    if cv2.waitKey(20) == 27:
        break


cv2.destroyWindow()