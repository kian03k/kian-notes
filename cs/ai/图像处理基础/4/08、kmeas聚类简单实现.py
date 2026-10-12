import matplotlib.pyplot as plt
from sklearn.cluster import KMeans,MiniBatchKMeans

from sklearn.metrics import davies_bouldin_score,silhouette_score,calinski_harabasz_score

from sklearn.datasets import make_blobs,make_circles,make_moons

# x,_ = make_blobs(n_samples=1000,n_features=2,centers=4)
# x,_ = make_circles(n_samples=1000,factor=0.5)
x,_ = make_moons(n_samples=1000)

plt.subplot(1,2,1)
plt.scatter(x[:,0],x[:,1])

km = KMeans(n_clusters=8)
km.fit(x)

plt.subplot(1,2,2)
plt.scatter(x[:,0],x[:,1],c=km.predict(x))

plt.show()
s = silhouette_score(x,km.labels_)
print('km的轮廓系数：',s)


