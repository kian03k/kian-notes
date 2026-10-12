import cv2
import numpy as np

img = cv2.imread('data/j4.png')  # 500,350
cv2.imshow('img',img)


kernel = cv2.getStructuringElement(cv2.MORPH_RECT,ksize=(3,3))
# kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,ksize=(9,9))
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,ksize=(9,9))
# print(kernel.dtype)
# kernel = np.ones((3,3))
# kernel = np.uint8([[1,0,0],[1,1,1]])

# dst = cv2.erode(img,kernel=kernel,iterations=10)  #腐蚀
# dst = cv2.dilate(dst,kernel,iterations=10) #膨胀

# dst = cv2.morphologyEx(img,op=cv2.MORPH_OPEN,kernel=kernel,iterations=10)  #其他的形态学操作 (开运算)  去掉毛刺
# dst = cv2.morphologyEx(img,op=cv2.MORPH_CLOSE,kernel=kernel,iterations=10)  #其他的形态学操作 （闭运算） 填充黑洞
# dst = cv2.morphologyEx(img,op=cv2.MORPH_TOPHAT,kernel=kernel,iterations=10)  #其他的形态学操作 （顶帽、礼帽运算） 提取毛刺
# dst = cv2.morphologyEx(img,op=cv2.MORPH_BLACKHAT,kernel=kernel,iterations=10)  #其他的形态学操作 （黑帽运算） 提取空洞

dst = cv2.morphologyEx(img,op=cv2.MORPH_GRADIENT,kernel=kernel,iterations=2)  #其他的形态学操作 （梯度） 提取简单轮廓

cv2.imshow('dst',dst)

cv2.waitKey(0)
cv2.destroyAllWindows()