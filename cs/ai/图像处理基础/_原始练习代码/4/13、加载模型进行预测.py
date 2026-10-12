import cv2
import torch

class Lenet5(torch.nn.Module):
    def __init__(self):
        super(Lenet5, self).__init__()
        self.con1 = torch.nn.Conv2d(in_channels=1,  #1 32*32
                                    out_channels=6,
                                    kernel_size=5)  #6*28*28
        self.relu1 = torch.nn.ReLU()
        self.maxpool2 = torch.nn.MaxPool2d(kernel_size=2,stride=2)  #6 14*14

        self.con3 = torch.nn.Conv2d(in_channels=6,
                                    out_channels=16,
                                    kernel_size=5)  #16 10*10
        self.relu3 = torch.nn.ReLU()

        self.maxpool4 = torch.nn.MaxPool2d(kernel_size=2,stride=2) #16 5*5

        self.con5 = torch.nn.Conv2d(in_channels=16,
                                    out_channels=120,
                                    kernel_size=5)  #120 1*1
        self.relu5 = torch.nn.ReLU()

        self.flatten = torch.nn.Flatten()  #展平层120*1
        self.fc6 = torch.nn.Linear(120,84)
        self.out_put=torch.nn.Linear(84,10)

    def forward(self,x):
        x = self.con1(x)
        x = self.relu1(x)
        x = self.maxpool2(x)
        x = self.con3(x)
        x = self.relu3(x)
        x = self.maxpool4(x)
        x = self.con5(x)
        x = self.relu5(x)
        x = self.flatten(x)
        x = self.fc6(x)
        out = self.out_put(x)
        return out

net = torch.load('lenet5.pkl')

img = cv2.imread('data\p02.png',0)
img = cv2.resize(img,(32,32))

test = img.reshape(-1,1,32,32) #NCWH
test = test/255.0

test = torch.tensor(test,dtype=torch.float32)

device = torch.device('cuda')
net =net.to(device)
test = test.to(device)
pre = net(test)

pre_y = torch.argmax(pre)
print(pre_y)
