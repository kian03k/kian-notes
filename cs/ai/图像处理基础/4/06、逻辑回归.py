from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score,recall_score,confusion_matrix
import joblib
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from sklearn.neighbors import KNeighborsClassifier,KNeighborsRegressor

from sklearn.svm import SVC,SVR,LinearSVC,NuSVC
from sklearn.naive_bayes import GaussianNB,BernoulliNB,MultinomialNB

from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor

from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor,AdaBoostClassifier,AdaBoostRegressor,GradientBoostingClassifier,GradientBoostingRegressor

iris = load_iris()
print(iris)
x = iris.data   #4个特征 (花萼的长度、宽度、花瓣的长度、宽度)
label = iris.target


std = StandardScaler()
x = std.fit_transform(x)
joblib.dump(std,'lr_std.pkl')  #保存标准化的模型

train_x,test_x,train_label,test_label = train_test_split(x,label)

# lr = LogisticRegression()
# lr.fit(train_x,train_label)

# lr = KNeighborsClassifier()
# lr.fit(train_x,train_label)

# lr = GaussianNB()
# lr.fit(train_x,train_label)

# lr = DecisionTreeClassifier()
# lr.fit(train_x,train_label)


lr = AdaBoostClassifier()
lr.fit(train_x,train_label)

ps = precision_score(train_label,lr.predict(train_x),average='micro')
print('模型在训练集上的准确率为：',ps)
ps = precision_score(test_label,lr.predict(test_x),average='micro')
print('模型在测试集上的准确率为：',ps)
cm = confusion_matrix(train_label,lr.predict(train_x))
print('模型在训练集上的混淆矩阵为：',cm)
cm = confusion_matrix(test_label,lr.predict(test_x))
print('模型在测试集上的混淆矩阵为：',cm)

joblib.dump(lr,'lr.pkl')





