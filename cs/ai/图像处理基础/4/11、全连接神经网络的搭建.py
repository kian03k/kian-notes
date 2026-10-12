import torch
import matplotlib.pyplot as plt
x = torch.linspace(-1,1,100)
x = torch.unsqueeze(x,dim=1)
y = x ** 2 + 0.2*torch.rand(x.size())

class Net(torch.nn.Module):

    def __init__(self,n_input,n_hidden,n_output):
        super(Net,self).__init__()
        self.hidden1 = torch.nn.Linear(n_input,n_hidden)
        self.hidden2 = torch.nn.Linear(n_hidden, n_hidden)
        self.output = torch.nn.Linear(n_hidden,n_output)

    def forward(self,x):

        x = self.hidden1(x)
        x = torch.sigmoid(x)
        x = self.hidden2(x)
        x = torch.sigmoid(x)
        x = self.output(x)

        return x

net = Net(n_input=1,n_hidden=3,n_output=1)

loss_func = torch.nn.MSELoss()
optim = torch.optim.Adam(params=net.parameters(),lr=0.1)

plt.ion()
plt.show()

for epoch in range(1000):

    pre_y = net(x)
    loss = loss_func(pre_y,y)
    print(loss)

    optim.zero_grad() #进行梯度清0
    loss.backward()
    optim.step()


    plt.cla()
    plt.scatter(x,y)

    plt.plot(x,pre_y.detach().numpy())
    plt.pause(0.001)


plt.ioff()
plt.show()
