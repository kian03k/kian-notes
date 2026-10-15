import cv2

#用来去除噪声点
img = cv2.imread('data/lena.png')  # 500,350
cv2.imshow('img',img)

# # dst = cv2.blur(img,(5,5))
# # dst = cv2.boxFilter(img,ddepth=-1,ksize=(5,5),normalize=False)
# dst = cv2.GaussianBlur(img,ksize=(5,5),sigmaX=0,sigmaY=0)
#
# # cv2.CV_16S   (signedint)
# # cv2.CV_8U    (unsigned int)
# # cv2.CV_32F   (float)
#
# # cv2.CV_8SC1
# # cv2.CV_8SC2


# dst = cv2.Sobel(img,ddepth=-1,dx=1,dy=0)  #边缘
# dst = cv2.Laplacian(img,ddepth=-1)
dst = cv2.Canny(img,80,170)

cv2.imshow('dst',dst)

cv2.waitKey(0)
cv2.destroyAllWindows()