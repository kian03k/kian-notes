import torch
import torchvision
import cv2

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = torchvision.models.resnet50(pretrained=False,num_classes=10).to(device)  #分类模型

model = torch.load('cifar10_resnet50.pth')

img = cv2.imread(r'data/002.jpg')

img = cv2.resize(img,(224,224))

img = img.reshape(-1,3,224,224) #N C H W
img = img/255.0

test = torch.tensor(img,dtype=torch.float32)

device = torch.device('cuda')
net =model.to(device)
test = test.to(device)
pre = net(test)

pre_y = torch.argmax(pre)
print(pre_y)

