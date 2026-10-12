import cv2
import numpy as np

# def call(x):
#     print(x)
#     pass
#
# img = np.zeros((500,500,3))
# cv2.imshow('img',img)
#
# cv2.createTrackbar('voice','img',0,100,call)
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()

def call(x):
    pass

img = np.zeros((500,500,3))
cv2.imshow('img',img)

cv2.createTrackbar('r','img',0,255,call)
cv2.createTrackbar('g','img',0,255,call)
cv2.createTrackbar('b','img',0,255,call)

while True:

    r = cv2.getTrackbarPos('r','img')
    g = cv2.getTrackbarPos('g','img')
    b = cv2.getTrackbarPos('b','img')

    img[:] = [b,g,r]

    cv2.imshow('img',img)

    if cv2.waitKey(10) == 27:
        break
cv2.destroyAllWindows()

