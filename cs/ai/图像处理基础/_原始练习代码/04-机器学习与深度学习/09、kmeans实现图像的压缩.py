import cv2
from sklearn.cluster import KMeans
import numpy as np

img0 = cv2.imread('data\lena.png')  #h,w,c
h,w,c = img0.shape
img = img0.reshape(h*w,c)


km = KMeans(n_clusters=8)
km.fit(img)

new_img = km.cluster_centers_[km.labels_]

new_img = new_img.astype(np.uint8)
new_img = new_img.reshape(h,w,c)

cv2.imshow('img',img0)
cv2.imshow('new',new_img)

cv2.imwrite('data/new_lena8.png',new_img)

cv2.waitKey(0)
cv2.destroyAllWindows()


