import cv2

img = cv2.imread('data/person.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

dector = cv2.CascadeClassifier('D:\install\python38\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')

# haarcascade_eye.xml
# dector = cv2.CascadeClassifier('D:\install\python38\Lib\site-packages\cv2\data\haarcascade_eye.xml')

list = dector.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=5,minSize=(2,2))


for x,y,w,h in list:
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0))

cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()


