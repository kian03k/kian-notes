
import torch
import torchvision
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

transform = torchvision.transforms.Compose([torchvision.transforms.Resize(32),
                               torchvision.transforms.ToTensor()]) #进行数据处理
train_data = torchvision.datasets.MNIST(root=r'./',download=False,train=True,transform=transform)
test_data = torchvision.datasets.MNIST(root=r'./',download=False,train=False,transform=transform)

train_loader = torch.utils.data.DataLoader(train_data,batch_size=64,shuffle=True)
test_loader = torch.utils.data.DataLoader(test_data,batch_size=64,shuffle=True)

devic = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

net = Lenet5().to(devic)
loss_func = torch.nn.CrossEntropyLoss().to(devic)
optim = torch.optim.Adam(net.parameters(),lr=0.01)

net.train()  #表明是训练过程
# net.eval()   #表明是测试过程
for i in range(10):
    for step,(x,y) in enumerate(train_loader):

        x = x.to(devic)
        y = y.to(devic)
        # print(x.shape)  #N C W H       h,w,c
        out = net(x)   #32*32
        loss = loss_func(out,y)

        optim.zero_grad()
        loss.backward()
        optim.step()
    print("第{}轮训练后的损失为：{}".format(i,loss))

torch.save(net,'lenet5.pkl')