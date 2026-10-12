from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import joblib

boston = load_boston()
x = boston.data             #房屋的数据 （506条，每条13个特征）
y = boston.target

#将数据进行标准化
std = StandardScaler()
x = std.fit_transform(x)
# std.fit(x)
# x = std.transform(x)
# print(x)
#将数据进行分割成训练集和测试集
train_x,test_x,train_y,test_y = train_test_split(x,y)

print(test_x[10])
print(test_y[0])


#加载模型
lg = LinearRegression()
lg.fit(train_x,train_y)  #模型训练  (train_x   (379,13))

#模型评估
ms1 = mean_absolute_error(train_y,lg.predict(train_x))   #在训练集上
print('模型在训练集上的均方差损失：',ms1)

ms1 = mean_absolute_error(test_y,lg.predict(test_x))  #在测试集上
print('模型在测试集上的均方差损失：',ms1)


print('模型的w:',lg.coef_)
print('模型的b:',lg.intercept_)


joblib.dump(lg,'lg.pkl')  #模型保存







