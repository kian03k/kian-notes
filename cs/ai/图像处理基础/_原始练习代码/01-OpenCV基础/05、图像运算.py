import cv2
import matplotlib.pyplot as plt
import numpy as np

# img1 = cv2.imread('data/bb0.png')  #图像的读取  (numpy数组)  (0--255直接的值)
# img2 = cv2.imread('data/bb.png')  #图像的读取  (numpy数组)

# print(type(img))
# print(img)


# dst = img1 + img2   #大于255  会对255取模
# dst = cv2.add(img2,img1)  #大于255  直接取值为255
# dst = cv2.addWeighted(img1,0.3,img2,0.8,0)  #大于255  直接取值为255

# dst = img2 - img1  #小于0 会对255取模
# dst = cv2.subtract(img2,img1)  #小于0 会直接取0

# dst = img2 * img1
# dst = cv2.multiply(img2,img1)

# dst = img2 / img1
# dst = cv2.divide(img1,img2)

img1 = cv2.imread('data/aa0.png')
h,w,c = img1.shape
img2 = cv2.imread('data/bb0.png')

img2 = cv2.resize(img2,(w,h))

mask = cv2.imread('data/mask.png', 0)
mask_not = cv2.bitwise_not(mask)

# dst = cv2.bitwise_and(img1,img1,mask=mask)
dst1 = cv2.bitwise_and(img2,img2,mask=mask)
dst2 = cv2.bitwise_and(img1,img1,mask=mask_not)


#逻辑运算  （转成二进制）

# 1100110
# 0001011
#
# 0100010

#与： 全1为1,遇0则0
#或：全0为0，遇1则1
#取反 遇0则1，遇1则0
#异或  不同为1，相同为0


dst = cv2.add(dst1,dst2)

# cv2.imshow('img1',dst1)
cv2.imshow('img2',dst)

cv2.waitKey(0)  #等待键盘输入操作
cv2.destroyAllWindows()  #销毁所有窗口
