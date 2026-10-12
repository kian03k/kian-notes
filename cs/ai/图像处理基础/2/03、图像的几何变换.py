import cv2
import numpy as np


img = cv2.imread('data/lena.png')  # 500,350
cv2.imshow('img',img)
#1、缩放
# dst = cv2.resize(img,(200,200))
# dst = cv2.resize(img,(1000,500))

# dst = cv2.resize(img,(1000,500),interpolation=cv2.INTER_AREA)
# dst = cv2.resize(img,(1000,500),interpolation=cv2.INTER_CUBIC)
# dst = cv2.resize(img,(1000,500),interpolation=cv2.INTER_LINEAR)
# dst =cv2.resize(img,None,fx=2,fy=2)
# dst =cv2.resize(img,None,fx=0.5,fy=1.5)

#2、翻转
# dst = cv2.flip(img,0)
# dst = cv2.flip(img,1)
# dst = cv2.flip(img,-1)

#3、仿射变换（旋转、平移和缩放）

# M = np.array([[1,2,1],[1,3,2]],np.float32)
# dst = cv2.warpAffine(img,M,(800,500))

#只平移
# M = np.array([[1,0,100],[0,1,80]],np.float32)
# dst = cv2.warpAffine(img,M,(800,500))

#只旋转

# M = np.array([[0.5,0.8,100],[-0.8,0.5,80]],np.float32)
# dst = cv2.warpAffine(img,M,(800,500))

# M = cv2.getRotationMatrix2D((100,100),-30,1)
# dst = cv2.warpAffine(img,M,(800,500))

# pts1 = np.float32([[0,0],[500,0],[500,350]])
# pts2 = np.float32([[0,0],[300,300],[50,500]])
#
# M = cv2.getAffineTransform(pts1,pts2)  #原图中的三个点和目标图中的三个点确定变换矩阵
# dst = cv2.warpAffine(img,M,(800,500))

#4、透射变换

# M = np.array([[0.2,0.2,2.0],[-0.06,0.3,0.4],[0.001,-0.005,1]],np.float32)
# dst = cv2.warpPerspective(img,M,(800,800))  #M矩阵为3*3

# pts1 = np.float32([[0,0],[500,0],[500,350],[0,350]])
# pts2 = np.float32([[0,0],[500,0],[300,300],[100,300]])
#
# M = cv2.getPerspectiveTransform(pts1,pts2)  ##原图中的四个点和目标图中的四个点确定变换矩阵
# dst = cv2.warpPerspective(img,M,(800,800))

#5、图像金字塔
# dst = cv2.pyrUp(img)
dst = cv2.pyrDown(img)


cv2.imshow('dst',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()