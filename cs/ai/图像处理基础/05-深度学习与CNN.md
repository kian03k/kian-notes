---
tags: [ai, 深度学习, cnn, pytorch]
created: 2026-10-12
updated: 2026-10-12
status: ok
---

# 05 · 深度学习与 CNN

> 本章目标：从"一个神经元"讲到"卷积神经网络"，并用 PyTorch 亲手搭一个全连接网络和一个 LeNet5 手写数字识别。
> 原始代码：`4/11、全连接神经网络的搭建.py` ~ `4/13、加载模型进行预测.py`；讲义：深度学习、卷积神经（PPT）

---

## 5.1 从感知机到神经网络

**深度学习（Deep Learning）** 是机器学习的分支，源于**人工神经网络**（模仿大脑神经元的信息处理系统）。

### 单个神经元：M-P 模型

一个神经元做的事就两步：**加权求和 → 过激活函数**。

```
z = w1·x1 + w2·x2 + ... + wn·xn + b
y = f(z)
```

- 感知机（Perceptron）：最原始的单层模型，**二分类**，只能解决**线性可分**问题（连"异或 XOR"都做不了）。
- **多层感知机（MLP）**：把多个神经元按层堆叠，就能拟合非线性关系。

### 神经网络的结构与两个过程

**全连接神经网络**：INPUT → 隐藏层 → 隐藏层 → … → OUTPUT。

- **前向传播（Forward）**：数据从输入一层层算到输出。
- **反向传播（Backward）**：算输出与真实值的误差，把梯度**从后往前**传，更新每一层的参数。

```
参数更新：w = w - η · (∂loss/∂w)      # η 是学习率
```

---

## 5.2 激活函数 / 损失函数 / 优化器

### 常用激活函数

| 函数 | 公式 | 特点 |
| --- | --- | --- |
| **Sigmoid** | `1/(1+e⁻ˣ)` | 输出 (0,1)，易梯度消失，少用于隐藏层 |
| **tanh** | `(eˣ-e⁻ˣ)/(eˣ+e⁻ˣ)` | 输出 (-1,1)，比 sigmoid 好一点 |
| **ReLU** | `max(0, x)` | **最常用**，计算快，缓解梯度消失 |
| **Leaky ReLU** | `max(αx, x)` | 解决 ReLU 负半轴"死掉"问题 |

> 激活函数的作用：**引入非线性**。没有它，再多层叠加也等价于一层线性变换。

### 常用损失函数

| 场景 | 损失函数 | PyTorch |
| --- | --- | --- |
| 回归 | 均方误差 MSE | `nn.MSELoss` |
| 分类 | 交叉熵 | `nn.CrossEntropyLoss` |

### 常用优化器

`SGD`（随机梯度下降）→ `Momentum`（动量）→ `Adagrad` → `RMSprop` → **`Adam`（最常用，自适应学习率）**

```python
optim = torch.optim.Adam(model.parameters(), lr=0.01)
```

---

## 5.3 PyTorch 基础

PyTorch 的核心概念：

```python
import torch

# 张量 Tensor（类似 numpy 数组，但能在 GPU 上算、能自动求导）
x = torch.linspace(-1, 1, 100)         # 均匀取 100 个数
x = torch.unsqueeze(x, dim=1)          # 增加一维，变成 (100, 1)

# 设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

**搭模型的固定套路**：

```python
class Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(输入维度, 隐藏维度)
        self.fc2 = torch.nn.Linear(隐藏维度, 输出维度)

    def forward(self, x):              # 定义前向传播
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x
```

**训练的固定五步**：

```python
pre = net(x)                    # ① 前向
loss = loss_func(pre, y)        # ② 算损失
optim.zero_grad()               # ③ 清空上一轮梯度
loss.backward()                 # ④ 反向传播求梯度
optim.step()                    # ⑤ 更新参数
```

---

## 5.4 demo：全连接网络拟合曲线

用一个三层全连接网络去拟合 `y = x²`，直观感受"神经网络在学习"。

```python
import torch
import matplotlib.pyplot as plt

# 造数据：y = x² + 噪声
x = torch.linspace(-1, 1, 100).unsqueeze(1)      # (100, 1)
y = x ** 2 + 0.2 * torch.rand(x.size())

class Net(torch.nn.Module):
    def __init__(self, n_input, n_hidden, n_output):
        super().__init__()
        self.hidden1 = torch.nn.Linear(n_input, n_hidden)
        self.hidden2 = torch.nn.Linear(n_hidden, n_hidden)
        self.output  = torch.nn.Linear(n_hidden, n_output)

    def forward(self, x):
        x = torch.sigmoid(self.hidden1(x))
        x = torch.sigmoid(self.hidden2(x))
        return self.output(x)

net = Net(n_input=1, n_hidden=10, n_output=1)
loss_func = torch.nn.MSELoss()
optim = torch.optim.Adam(net.parameters(), lr=0.1)

plt.ion(); plt.show()
for epoch in range(1000):
    pre_y = net(x)
    loss = loss_func(pre_y, y)

    optim.zero_grad()
    loss.backward()
    optim.step()

    # 每 50 轮画一次，看拟合曲线逐渐贴合
    if epoch % 50 == 0:
        plt.cla()
        plt.scatter(x.detach().numpy(), y.detach().numpy())
        plt.plot(x.detach().numpy(), pre_y.detach().numpy(), 'r-')
        plt.pause(0.1)
plt.ioff(); plt.show()
```

> 你能看到红线从"乱画"逐渐贴合散点 —— 这就是**梯度下降在起作用**。

---

## 5.5 卷积神经网络（CNN）

### 为什么需要 CNN

全连接网络处理图像有两个问题：**参数量爆炸**（256×256×3 的图，一个全连接层就上亿参数）+ **丢失空间结构**。CNN 用两个特性解决：

1. **局部感知**：一个神经元只看图像的一小块区域
2. **权值共享**：同一个卷积核在整个图上滑动，参数大幅减少

### CNN 的基本结构

```
INPUT → [卷积 → 激活 → 池化] × N → 全连接 → OUTPUT
```

**① 卷积层（Convolution）**：用卷积核在图上滑动做加权求和，提取特征。

```
卷积核 ⨂ 输入图像 → 特征图（feature map）
例：3×3 核扫过，每个位置做 9 次乘加，得到特征图上一个值
```

卷积的三个参数：

| 参数 | 含义 |
| --- | --- |
| **深度 depth** | 卷积核个数 = 输出特征图数量 |
| **步长 stride** | 核每次滑动的格数 |
| **填充 padding** | 边缘补 0 的圈数（保持输出尺寸） |

**② 激活层**：接 ReLU（引入非线性，见 §5.2）。

**③ 池化层（Pooling）**：下采样，把特征图变小（降计算量、防过拟合、保留主要特征）。

```python
torch.nn.MaxPool2d(kernel_size=2, stride=2)   # 最大池化：取窗口最大值（最常用）
torch.nn.AvgPool2d(kernel_size=2, stride=2)   # 均值池化
```

**④ 全连接层**：把特征图拉平，送进分类器输出类别。

**⑤ BatchNorm（BN）**：对每层输出做标准化，加速收敛、防梯度消失。

> BN 的作用：解决"训练中中间层数据分布一直在变（Internal Covariate Shift）"的问题。小 batch 场景可换 GroupNorm / LayerNorm。

### PyTorch 里的对应 API

| 层 | API |
| --- | --- |
| 卷积 | `torch.nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)` |
| 激活 | `torch.nn.ReLU()` |
| 池化 | `torch.nn.MaxPool2d(kernel_size, stride)` |
| 全连接 | `torch.nn.Linear(in_features, out_features)` |
| 展平 | `torch.nn.Flatten()` |

---

## 5.6 demo：LeNet5 手写数字识别

**LeNet-5** 是 CNN 的开山之作（LeCun，1998），专为手写数字识别设计。

```
1×32×32 → 卷积(6) → 池化 → 卷积(16) → 池化 → 卷积(120) → 展平 → FC(84) → FC(10)
```

```python
import torch
import torchvision

class Lenet5(torch.nn.Module):
    def __init__(self):
        super().__init__()
        # 1×32×32 → 6×28×28
        self.con1 = torch.nn.Conv2d(1, 6, kernel_size=5)
        self.relu1 = torch.nn.ReLU()
        self.maxpool2 = torch.nn.MaxPool2d(kernel_size=2, stride=2)   # → 6×14×14

        self.con3 = torch.nn.Conv2d(6, 16, kernel_size=5)             # → 16×10×10
        self.relu3 = torch.nn.ReLU()
        self.maxpool4 = torch.nn.MaxPool2d(kernel_size=2, stride=2)   # → 16×5×5

        self.con5 = torch.nn.Conv2d(16, 120, kernel_size=5)           # → 120×1×1
        self.relu5 = torch.nn.ReLU()

        self.flatten = torch.nn.Flatten()
        self.fc6 = torch.nn.Linear(120, 84)
        self.out_put = torch.nn.Linear(84, 10)                        # 10 类数字

    def forward(self, x):
        x = self.maxpool2(self.relu1(self.con1(x)))
        x = self.maxpool4(self.relu3(self.con3(x)))
        x = self.relu5(self.con5(x))
        x = self.flatten(x)
        x = self.fc6(x)
        return self.out_put(x)

# ---- 数据准备 ----
transform = torchvision.transforms.Compose([
    torchvision.transforms.Resize(32),
    torchvision.transforms.ToTensor(),
])
train_data = torchvision.datasets.MNIST(root='./', train=True,  download=True, transform=transform)
test_data  = torchvision.datasets.MNIST(root='./', train=False, download=True, transform=transform)

train_loader = torch.utils.data.DataLoader(train_data, batch_size=64, shuffle=True)

# ---- 训练 ----
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
net = Lenet5().to(device)
loss_func = torch.nn.CrossEntropyLoss().to(device)
optim = torch.optim.Adam(net.parameters(), lr=0.01)

net.train()
for epoch in range(10):
    for step, (x, y) in enumerate(train_loader):
        x, y = x.to(device), y.to(device)
        out = net(x)
        loss = loss_func(out, y)

        optim.zero_grad()
        loss.backward()
        optim.step()
    print(f'第 {epoch} 轮，loss = {loss.item():.4f}')

torch.save(net, 'lenet5.pkl')
```

> 注意 `net.train()` / `net.eval()`：**训练模式 vs 评估模式**，会影响 BN、Dropout 的行为，别忘切换。

---

## 5.7 经典 CNN 网络一览（讲义要点）

了解 CNN 的演进，建立"图谱感"：

| 年份 | 网络 | 关键贡献 |
| --- | --- | --- |
| 1998 | **LeNet-5** | CNN 开山之作，手写数字 |
| 2012 | **AlexNet** | ImageNet 夺冠；首次用 ReLU + Dropout，深浅网络分界线 |
| 2014 | **VGG** | 探索"深度"，16~19 层，结构规整；常用来**提特征** |
| 2014 | **GoogLeNet** | Inception 模块，并行结构，1×1 卷积降维 |
| 2015 | **ResNet** | **残差连接**（shortcut），解决深层网络退化，可到上百层 |
| 2017 | **DenseNet** | 密集连接，特征复用，参数更少 |
| 2017 | **SENet** | 通道注意力机制 |
| 2017 | **MobileNet** | 深度可分离卷积，轻量级，面向移动端 |

> 记忆线索：**AlexNet（深层开端）→ VGG（更深）→ GoogLeNet（更宽/并行）→ ResNet（更稳，残差）→ 轻量化（MobileNet）**。
> ResNet 的残差块**怎么用代码实现**，见 [[09-ResNet网络结构与手写实现]]。

---

## 本章小结

- 神经网络 = **前向传播（算） + 反向传播（学）**
- 训练五步：**前向 → 损失 → 清梯度 → 反向 → 更新**
- CNN 四大件：**卷积、激活、池化、全连接**（+ BN）
- PyTorch 套路：`nn.Module` 定义 → `.to(device)` → `optim` 优化 → 循环训练 → `torch.save`

➡️ 下一章：[[06-目标检测]] —— 从"识别一张图"到"找出所有物体"。
