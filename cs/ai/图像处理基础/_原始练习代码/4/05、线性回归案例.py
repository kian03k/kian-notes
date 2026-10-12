from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
from sklearn.preprocessing import StandardScaler

import pandas as pd
import numpy as np
train = pd.read_csv('data/train.csv')   #读取数据
test = pd.read_csv('data/test.csv')

train = train.drop('id',axis=1)  #删除第一列编号
test = test.drop('id',axis=1)

x = train.iloc[:,train.columns != 'y']
y = train.iloc[:,train.columns == 'y']

std = StandardScaler()  #标准化  （0,1）   均值  和方差
# std.fit(x) # 0 , 0.5
# x = std.transform(x)
x = std.fit_transform(x)
test= std.transform(test)
#加载模型
lg = LinearRegression()
lg.fit(x,y)  #模型训练  (train_x   (379,13))
#模型评估
ms1 = mean_absolute_error(y,lg.predict(x))   #在训练集上
print('模型在训练集上的均方差损失：',ms1)

count = lg.predict(test)
print('在测试集上预测的结果为：',np.floor(count))


# joblib.dump(lg,'lg.pkl')  #模型保存







