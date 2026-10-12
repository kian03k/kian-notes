import cv2


img = cv2.imread('data/lena.png')  # 500,350
cv2.imshow('img',img)
# print(img)
# dst = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# print(dst)
#
# dst1 = cv2.cvtColor(dst,cv2.COLOR_GRAY2BGR)
# print(dst1)


dst = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
dst = cv2.cvtColor(img,cv2.COLOR_BGR2Lab)

# dst = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
cv2.imshow('dst',dst)

cv2.waitKey(0)
cv2.destroyAllWindows()