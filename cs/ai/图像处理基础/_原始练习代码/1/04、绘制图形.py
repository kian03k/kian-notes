import cv2
import numpy as np
img = np.zeros((600,600,3),dtype=np.uint8)
#
# cv2.line(img,(200,200),(500,500),color=[100,255,0],thickness=3)

# # cv2.circle(img,(300,300),300,color=[255,0,255],thickness=5)   #画空心圆
# # cv2.circle(img,(300,300),300,color=[255,255,255],thickness=-1) #画实心心圆
#
# cv2.rectangle(img,(200,200),(500,500),color=[200,50,0],thickness=3)
# cv2.rectangle(img,(200,200),(500,500),color=[200,50,0],thickness=-1)

#
# cv2.ellipse(img,(300,300),(300,200),angle=0,startAngle=0,endAngle=360,color=[200,100,0],thickness=3)
# cv2.ellipse(img,(300,300),(300,200),angle=45,startAngle=0,endAngle=360,color=[20,100,0],thickness=3)
# cv2.ellipse(img,(300,300),(300,200),angle=-45,startAngle=0,endAngle=360,color=[20,100,0],thickness=3)

# cv2.ellipse(img,(300,300),(300,200),angle=0,startAngle=0,endAngle=-90,color=[200,100,0],thickness=3)

# cv2.ellipse(img,(300,300),(300,200),angle=0,startAngle=0,endAngle=360,color=[200,100,0],thickness=-1)


pts = np.array([[(100,100),(200,300),(300,200),(400,100),(500,200)]])

# # cv2.polylines(img,pts=pts,isClosed=False,color=[0,0,255],thickness=3)
# # cv2.polylines(img,pts=pts,isClosed=False,color=[0,0,255],thickness=3)
# # cv2.polylines(img,pts=pts,isClosed=True,color=[0,0,255],thickness=3)
# cv2.fillPoly(img,pts=pts,color=[0,0,255])

cv2.putText(img,'lena',(100,100),fontFace=cv2.FONT_ITALIC,fontScale=3,color=[255,255,0],thickness=5)
# cv2.putText(img,'李娜',(100,100),fontFace=cv2.FONT_ITALIC,fontScale=1,color=[255,255,0],thickness=1)

cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# img = cv2.imread('data/lena.png')
#
# cv2.rectangle(img,(210,140),(340,260),color=[200,50,0],thickness=3)
#
# # face = img[140:260,210:340]
# cv2.imshow('img',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

