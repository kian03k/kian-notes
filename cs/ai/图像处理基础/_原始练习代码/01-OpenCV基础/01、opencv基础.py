import cv2
import matplotlib.pyplot as plt
import numpy as np

# img = cv2.imread('data/lena.png')  #图像的读取  (numpy数组)
#
# # print(type(img))
# # print(img)
#
# cv2.imshow('img',img)
#
# cv2.waitKey(0)  #等待键盘输入操作
# cv2.destroyAllWindows()  #销毁所有窗口


# cv2.IMREAD_COLOR  以彩色方式读取 （会丢失透明度信息）
# cv2.IMREAD_GRAYSCALE以灰度方式读取
#cv2.IMREAD_UNCHANGED 保留图片的透明度信息

# img = cv2.imread('data/1.jpg',cv2.IMREAD_COLOR)  #图像的读取  (numpy数组)
# # img = cv2.imread('data/lena.png',1)  #图像的读取  (numpy数组)
#
# # img = cv2.imread('data/lena.png',cv2.IMREAD_GRAYSCALE)  #图像的读取  (numpy数组)
# # img = cv2.imread('data/lena.png',0)  #图像的读取  (numpy数组)
#
# # img = cv2.imread('data/1.jpg',cv2.IMREAD_UNCHANGED)  #图像的读取  (numpy数组)
# # img = cv2.imread('data/1.jpg',-1)  #图像的读取  (numpy数组)
#
#
# print(img.shape)   #(350, 500, 3)  (h(高),w（宽）,c（通道数（b,g,r））)  numpy数组 （行、列）
#
#                    # (439, 780, 4)   (h(高),w（宽）,c（通道数（b,g,r,a(透明度)））)
# print(img)
#
# cv2.imshow('img',img)
#
# cv2.waitKey(0)  #等待键盘输入操作
# cv2.destroyAllWindows()  #销毁所有窗口


# #图像（bgr---rgb）转换
# img = cv2.imread('data/lena.png')  #图像的读取  (numpy数组)
#
# # print(type(img))
# # print(img)
#
# cv2.imshow('img',img)  #图像的通道是  b,g,r  (numpy数组，h,w,c(b,g,r))
# #①
# # img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)    #使用颜色空间转换函数
# #②
# # img = img[:,:,::-1]  #使用numpy数组将 通道进行逆序
# #③
# #使用通道拆分函数
# b,g,r = cv2.split(img)  #按照通道进行拆分
# img = cv2.merge([r,g,b]) #在合并
#
# plt.imshow(img)        #图像的通道是  r,g,b
# plt.show()
#
#
#
# cv2.waitKey(0)  #等待键盘输入操作
# cv2.destroyAllWindows()  #销毁所有窗口


# img1 = cv2.imread('data/lena.png')  #图像的读取  (numpy数组)
# img2 = cv2.imread('data/1.jpg')  #图像的读取  (numpy数组)
# # print(type(img))
# # print(img)
#
# # cv2.imshow('img1',img1)  #覆盖
# # cv2.imshow('img2',img2)
#
# plt.subplot(1,2,1)
# plt.imshow(img1)
#
# plt.subplot(1,2,2)
# plt.imshow(img2)
# plt.show()
#
#
# cv2.waitKey(0)  #等待键盘输入操作
# cv2.destroyAllWindows()  #销毁所有窗口

#numpy 数组在opencv可以当做图像去处理，但是注意类型 uint8
# img = cv2.imread('data/lena.png')  #图像的读取  (numpy数组)
# print(img.dtype)
# img = np.zeros((500,500,3))
# img = np.ones((500,500,3)) * 255
# print(img)
# # img = np.random.randint(0,255,(500,300,3),dtype=np.uint8)
# # print(img.dtype)
#
# # print(type(img))
# # print(img)
#
# cv2.imshow('img',img)
#
# cv2.waitKey(0)  #等待键盘输入操作
# cv2.destroyAllWindows()  #销毁所有窗口


# # img = cv2.imread('data/lena.png')  #图像的读取  (numpy数组)
# img = np.zeros((500,500,3))
# # print(type(img))
# # print(img)
#
# cv2.imshow('img',img)
# cv2.imwrite('data/black.jpg',img)   #图片的保存
#
# cv2.waitKey(0)  #等待键盘输入操作
# cv2.destroyAllWindows()  #销毁所有窗口



img = cv2.imread('data/lena.png', 0)  #图像的读取  (numpy数组)
cv2.imshow('img',img)

print(img.shape)  #h,w,c(b,g,r)
print(img.dtype)  #uint8
print(img.size)   #图像的像素 h*w*c


cv2.waitKey(0)  #等待键盘输入操作
cv2.destroyAllWindows()  #销毁所有窗口

