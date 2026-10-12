import cv2

#用来去除噪声点
img = cv2.imread('data/ditu.png')  # 500,350
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # 500,350
cv2.imshow('img',img)

gray = cv2.GaussianBlur(gray,(3,3),sigmaX=0)
_,dst = cv2.threshold(gray,110,255,cv2.THRESH_BINARY)

# cv2.inRange()  #HSV色彩空间

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
dst = cv2.morphologyEx(dst,op=cv2.MORPH_CLOSE,kernel=kernel,iterations=5)
dst = cv2.morphologyEx(dst,op=cv2.MORPH_OPEN,kernel=kernel,iterations=5)

x,_ = cv2.findContours(dst,mode=cv2.RETR_EXTERNAL,method=cv2.CHAIN_APPROX_NONE)
print(x)
dst =cv2.drawContours(img,contours=x,contourIdx=-1,color=[0,0,255],thickness=2)

cv2.imshow('dst',dst)

print(len(x))

print('轮廓的面积是：',cv2.contourArea(x[2]))
print('轮廓的周长是：',cv2.arcLength(x[2],closed=True))

a = cv2.minAreaRect(x[2])
print(a)

(x,y,w,h) = cv2.boundingRect(x[2])
cv2.rectangle(img,(x,y),(x+w,y+h),color=[0,255,0])
cv2.imshow('img1',img)



cv2.waitKey(0)
cv2.destroyAllWindows()