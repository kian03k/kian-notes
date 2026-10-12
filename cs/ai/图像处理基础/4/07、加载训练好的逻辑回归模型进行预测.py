import joblib
import numpy as np


label_name = ['setosa', 'versicolor', 'virginica']


x = np.array([5.1, 3.5, 1.4, 0.2])  # 120 4
x = x.reshape(-1,4)

std = joblib.load('lr_std.pkl')
x = std.transform(x)

model = joblib.load('lr.pkl')
label = model.predict(x)
index = label[0]


print('预测鸢尾花类别为：',label_name[index])
