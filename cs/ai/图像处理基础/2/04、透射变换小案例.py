import cv2
import numpy as np


img = cv2.imread('data/car_lain.png')  # 500,350
cv2.imshow('img',img)


pts1 = np.float32([[170,0],[323,0],[448,230],[58,230]])
pts2 = np.float32([[58,0],[448,0],[448,230],[58,230]])

M = cv2.getPerspectiveTransform(pts1,pts2)  ##原图中的四个点和目标图中的四个点确定变换矩阵
dst = cv2.warpPerspective(img,M,(800,800))


cv2.imshow('dst',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
