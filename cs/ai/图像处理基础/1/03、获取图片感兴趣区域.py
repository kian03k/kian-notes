import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread('data/lena.png')  #图像的读取  (numpy数组)

cv2.imshow('img',img)


face = img[140:260,210:340]  #获取图像的感兴趣区域  （图像的截取）
cv2.imshow('face',face)


img[140:260,210:340] = np.zeros((260-140,340-210,3))  #对感兴趣区域赋值
cv2.imshow('img_face',img)

cv2.waitKey(0)  #等待键盘输入操作
cv2.destroyAllWindows()  #销毁所有窗口
