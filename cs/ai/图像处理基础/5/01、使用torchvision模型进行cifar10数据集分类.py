import torch
import torchvision

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = torchvision.models.resnet50(pretrained=False,num_classes=10).to(device)  #分类模型

transform = torchvision.transforms.Compose(
    [torchvision.transforms.ToTensor(),
     torchvision.transforms.Resize(224)]
)

train_set = torchvision.datasets.CIFAR10(root='./',download=False,train=True,transform=transform)
test_set = torchvision.datasets.CIFAR10(root='./',download=False,train=False,transform=transform)
#数据分批次
train_loader = torch.utils.data.DataLoader(train_set,batch_size=8,shuffle=True)
test_loader = torch.utils.data.DataLoader(test_set,batch_size=8,shuffle=True)

loss_func = torch.nn.CrossEntropyLoss().to(device)  #损失函数
optim = torch.optim.Adam(model.parameters(),lr=0.01)#优化函数

for epoch in range(1):
    for step,(x,y) in enumerate(train_loader):
        x,y = x.to(device),y.to(device)

        pre = model(x)
        loss = loss_func(pre,y)
        print(loss)
        optim.zero_grad()
        loss.backward()
        optim.step()

    print('peoch:',epoch,'loss:',loss)
torch.save(model,'cifar10_resnet50.pth')
