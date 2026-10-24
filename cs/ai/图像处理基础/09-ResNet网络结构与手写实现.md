---
tags: [ai, 深度学习, pytorch, resnet, 残差网络]
created: 2026-10-16
updated: 2026-10-16
status: ok
---

# 09 · ResNet 网络结构与手写实现

> 本章目标：搞懂**残差连接为什么有效**，并**自己从零把 ResNet 写出来**，而不是直接调 `torchvision.models.resnet34()`。
> 原始代码：`_原始练习代码/06-ResNet手写实现/`（`model.py` / `train.py` / `predict.py`）

`07` 篇讲的是"**用** ResNet"（拿现成模型做迁移学习），这一篇补上中间缺的一环 ——"**造** ResNet"，把它的结构拆开看。

---

## 9.1 为什么需要残差：深层网络的退化

直觉上"层数越多、表达力越强"，但实验发现：把 20 层网络简单堆到 56 层，**训练误差反而更大**。注意这不是过拟合（过拟合是训练误差小、测试误差大），而是**连训练集都拟合不好**了 —— 这个现象叫**退化（degradation）**。

原因在于：深层网络里，梯度要穿过几十上百层往回传，很容易衰减/爆炸，浅层的参数几乎收不到有效的更新信号。

**残差学习**的思路很巧妙：与其让一堆层直接学目标映射 `H(x)`，不如**让它们学残差** `F(x) = H(x) - x`，然后输出 `F(x) + x`。

- 如果最优解就是"什么都不做"（恒等映射 `H(x) = x`），那网络只要把 `F(x)` 压到 0 就行 —— **这比让一堆非线性层去逼近恒等映射容易得多**；
- 反向传播时，梯度可以通过 `+ x` 这条捷径**直接流回浅层**，不衰减。

> 一句话：**残差连接给梯度开了一条"高速公路"**，所以才能把网络堆到 152 层甚至更深。

---

## 9.2 残差块长什么样

一个残差块有两条路径：

```
        x
        │
        ├──────────────────────┐   ← 捷径（shortcut / skip connection）
        │                      │
   ┌────▼────┐                 │
   │  conv   │                 │
   │   BN    │                 │
   │  ReLU   │                 │
   ├─────────┤                 │
   │  conv   │                 │
   │   BN    │                 │
   └────┬────┘                 │
        │                      │
        └──────────►(+)◄───────┘   ← 逐元素相加
                     │
                   ReLU
                     │
                   输出
```

捷径分两种，**这是理解 ResNet 代码的关键**：

| 类型 | 样子 | 什么时候用 |
| --- | --- | --- |
| **实线捷径** | `x` 直接加过去，什么都不做 | 输入输出 **shape 完全一致** 时 |
| **虚线捷径** | 先过一层 1×1 卷积 + BN（即 `downsample`），再相加 | 输入输出 **shape 不一致** 时 |

为什么需要虚线？因为 `out += identity` 要求两者**形状严格相同**。当特征图被下采样（尺寸减半）、或通道数翻倍时，原始 `x` 对不上，必须先变换。

---

## 9.3 两种残差块：BasicBlock 与 Bottleneck

ResNet 家族里有两套积木：

| | **BasicBlock** | **Bottleneck** |
| --- | --- | --- |
| 用在 | ResNet-18 / 34 | ResNet-50 / 101 / 152 |
| 结构 | 两个 3×3 卷积 | **1×1 → 3×3 → 1×1** |
| `expansion` | **1** | **4** |
| 输出通道 | `out_channel × 1` | `out_channel × 4` |
| 参数量（1000 类） | ResNet-18 ≈11.7 M、34 ≈21.3 M | ResNet-50 ≈25.6 M、101 ≈44.6 M |

**Bottleneck 为什么长这样？** 直接堆两个 3×3 的代价是 `3×3×C×C`。Bottleneck 先用 1×1 把通道**压缩**（降到 1/4），做 3×3 卷积，再用 1×1 **升回来** —— 参数和计算量大幅下降，于是能堆得更深。

`expansion` 这个类属性就是记录"出口通道相对传入的 `out_channel` 放大了几倍"，`ResNet` 主体靠它算通道数。

---

## 9.4 ResNet 主体与 `_make_layer`

整个网络可以拆成三段：

```
conv1 (7×7, s2) → bn → relu → maxpool (3×3, s2)     ← 前置下采样
   ↓
layer1 → layer2 → layer3 → layer4                    ← 四个 stage，每个若干残差块
   ↓
avgpool (自适应) → flatten → fc                      ← 分类头
```

真正有技巧的是 `_make_layer` —— 它负责生成一个 stage 里的一串残差块：

```python
def _make_layer(self, block, channel, block_num, stride=1):
    downsample = None
    # ① 只有当「尺寸要变小（stride≠1）」或「通道数要变」时，才需要虚线捷径
    if stride != 1 or self.in_channel != channel * block.expansion:
        downsample = nn.Sequential(
            nn.Conv2d(self.in_channel, channel * block.expansion,
                      kernel_size=1, stride=stride, bias=False),
            nn.BatchNorm2d(channel * block.expansion))

    layers = []
    # ② 每个 stage 的**第一个**块承担"换尺寸/换通道"的活，所以带 stride 和 downsample
    layers.append(block(self.in_channel, channel, downsample=downsample, stride=stride))
    self.in_channel = channel * block.expansion      # ③ 更新通道数，供后续块使用

    # ④ 剩下的块尺寸不变，直接连续堆
    for _ in range(1, block_num):
        layers.append(block(self.in_channel, channel))

    return nn.Sequential(*layers)
```

三个要点：

1. **一个 stage 里只有第一个块会改变尺寸/通道**，后面的块输入输出完全一致 → 走实线捷径；
2. `self.in_channel` 必须在**第一个块建好之后**才更新 —— 顺序反了，第一个块拿到的就是错的输入通道；
3. 虚线用 **1×1 卷积 + stride** 实现下采样，而不是池化 —— 池化丢信息，1×1 卷积可以学。

对照实际网络看：`resnet34()` 四个 stage 首块的 `downsample` 状态是 **无 / 有 / 有 / 有** —— 只有 layer1 的输入通道正好是 64（= 64×1）、stride 又是 1，可以走实线；后面三个 stage 既要缩小尺寸又要加宽通道，都必须走虚线。

配合各 stage 的配置，就得到了不同深度的 ResNet：

```python
def resnet34(num_classes=1000, include_top=True):
    return ResNet(BasicBlock, [3, 4, 6, 3], num_classes, include_top)

def resnet101(num_classes=1000, include_top=True):
    return ResNet(Bottleneck, [3, 4, 23, 3], num_classes, include_top)
```

`[3, 4, 6, 3]` 就是 layer1~layer4 各自的**块数**（3+4+6+3 = 16 个块 × 2 层 = 32，加上首尾 = 34 层，名字由此而来）。

---

## 9.5 完整实现

下面是整理版（逻辑与原件完全一致，只是把重复的 `self.relu = ...` 合并、补了注释）。原封不动的原件在 `_原始练习代码/06-ResNet手写实现/`。

```python
import torch
import torch.nn as nn


# ========== 18 / 34 用的残差块 ==========
class BasicBlock(nn.Module):
    expansion = 1                     # 出口通道 = out_channel × 1

    def __init__(self, in_channel, out_channel, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channel, out_channel, kernel_size=3,
                               stride=stride, padding=1, bias=False)   # bias=False：后面紧跟 BN，偏置是冗余的
        self.bn1 = nn.BatchNorm2d(out_channel)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(out_channel, out_channel, kernel_size=3,
                               stride=1, padding=1, bias=False)        # 第二个卷积 stride 固定为 1
        self.bn2 = nn.BatchNorm2d(out_channel)
        self.downsample = downsample      # 虚线捷径，为 None 时就是实线

    def forward(self, x):
        identity = x                      # 先把输入存下来
        if self.downsample is not None:
            identity = self.downsample(x) # 虚线：变换后形状才对得上

        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))   # 注意：这里**不做** ReLU

        out += identity                   # 关键一步：残差相加
        out = self.relu(out)              # 相加之后才 ReLU
        return out


# ========== 50 / 101 / 152 用的残差块 ==========
class Bottleneck(nn.Module):
    expansion = 4                     # 出口通道 = out_channel × 4

    def __init__(self, in_channel, out_channel, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        # 1×1 压缩通道
        self.conv1 = nn.Conv2d(in_channel, out_channel, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channel)
        # 3×3 提特征（stride 落在这一层）
        self.conv2 = nn.Conv2d(out_channel, out_channel, kernel_size=3,
                               stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channel)
        # 1×1 升回 4 倍通道
        self.conv3 = nn.Conv2d(out_channel, out_channel * self.expansion,
                               kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channel * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        if self.downsample is not None:
            identity = self.downsample(x)

        out = self.relu(self.bn1(self.conv1(x)))
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))   # 同样：最后一个 BN 后不接 ReLU

        out += identity
        out = self.relu(out)
        return out


# ========== 主体 ==========
class ResNet(nn.Module):
    def __init__(self, block, blocks_num, num_classes=1000, include_top=True):
        super(ResNet, self).__init__()
        self.include_top = include_top   # 置 False 可只取骨干（迁移学习时有用）
        self.in_channel = 64

        self.conv1 = nn.Conv2d(3, self.in_channel, kernel_size=7,
                               stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_channel)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(block, 64,  blocks_num[0])
        self.layer2 = self._make_layer(block, 128, blocks_num[1], stride=2)
        self.layer3 = self._make_layer(block, 256, blocks_num[2], stride=2)
        self.layer4 = self._make_layer(block, 512, blocks_num[3], stride=2)

        if self.include_top:
            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))   # 自适应：不管输入多大，都池化成 1×1
            self.fc = nn.Linear(512 * block.expansion, num_classes)

        # 卷积核用 Kaiming 初始化（配合 ReLU）
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    def _make_layer(self, block, channel, block_num, stride=1):
        downsample = None
        if stride != 1 or self.in_channel != channel * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channel, channel * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(channel * block.expansion))

        layers = [block(self.in_channel, channel, downsample=downsample, stride=stride)]
        self.in_channel = channel * block.expansion
        for _ in range(1, block_num):
            layers.append(block(self.in_channel, channel))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.maxpool(self.relu(self.bn1(self.conv1(x))))

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        if self.include_top:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)
        return x


def resnet34(num_classes=1000, include_top=True):
    return ResNet(BasicBlock, [3, 4, 6, 3], num_classes, include_top)


def resnet101(num_classes=1000, include_top=True):
    return ResNet(Bottleneck, [3, 4, 23, 3], num_classes, include_top)
```

---

## 9.6 demo①：mini 训练（可运行）

原 `train.py` 用的是花卉 5 分类数据集（`flower_data/`），那份数据不在，跑不起来。这里换成 **torchvision 自带的 CIFAR-10**，用同样一套"训练 → 验证 → 存最优"的流程，**改小数据量**以便在 CPU 上快速验证流程。

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from model import resnet34          # 上面自己写的那个

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# CIFAR-10 是 32×32 的小图，直接喂给 ResNet 也成立（推算见 9.8）
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

train_set = datasets.CIFAR10('./data', train=True,  download=True, transform=transform)
test_set  = datasets.CIFAR10('./data', train=False, download=True, transform=transform)

# 只是验证流程，各取一小撮 —— 真跑 5 万张在 CPU 上要很久
train_set = torch.utils.data.Subset(train_set, range(2000))
test_set  = torch.utils.data.Subset(test_set,  range(500))

train_loader = torch.utils.data.DataLoader(train_set, batch_size=32, shuffle=True,  num_workers=2)
test_loader  = torch.utils.data.DataLoader(test_set,  batch_size=32, shuffle=False, num_workers=2)

net = resnet34(num_classes=10).to(device)      # ⭐ 类别数改成 10
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=1e-3)

for epoch in range(2):
    # ---- 训练 ----
    net.train()                                  # 打开 BN / Dropout 的训练行为
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = loss_fn(net(images), labels)
        loss.backward()
        optimizer.step()

    # ---- 验证 ----
    net.eval()                                   # 关键：切评估模式，BN 用滑动统计量
    correct = 0
    with torch.no_grad():                        # 推理不建计算图，省内存
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            correct += (net(images).argmax(dim=1) == labels).sum().item()
    print(f'epoch {epoch + 1}  loss={loss.item():.3f}  acc={correct / len(test_set):.3f}')
```

> 几个从原 `train.py` 里学到的细节：
> - **进度条**用 `\r` + `*` 号手搓（`print(..., end='')` 覆盖同一行），不用装 tqdm；
> - **只在验证准确率创新高时才存权重**（`if val_accurate > best_acc: torch.save(...)`）—— 存最优，而不是存最后一个 epoch；
> - 训练前 `net.train()`、验证前 `net.eval()`，**这一对切换不能漏**（BN 和 Dropout 行为不同）。

> 💡 数据集下不动（离线环境）时不必卡住：自己写一个 20 行的 `Dataset` 就能把训练流程跑通 —— 只要实现 `__len__` 和 `__getitem__`（返回 `(图片 tensor, 标签)`），`DataLoader` / `Subset` / 训练循环全都照用，**换数据源不影响一行训练代码**：
>
> ```python
> class MyDataset(torch.utils.data.Dataset):
>     def __init__(self, images, labels, transform=None):
>         self.images, self.labels, self.transform = images, labels, transform
>
>     def __len__(self):
>         return len(self.labels)
>
>     def __getitem__(self, i):
>         img = Image.fromarray(self.images[i])   # numpy (H,W,3) uint8 → PIL
>         if self.transform:
>             img = self.transform(img)
>         return img, self.labels[i]
> ```
>
> 这也是自定义数据集（`ImageFolder` 不够用时）的标准写法。

---

## 9.7 demo②：预测单张图片

```python
import json
import torch
from PIL import Image
from torchvision import transforms
from model import resnet34

# ① 预处理必须和训练时**完全一致**
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ② 类别索引 → 名字（训练时用 class_to_idx 反写出来的）
class_indict = json.load(open('class_indices.json'))     # {"0": "daisy", "1": "dandelion", ...}

# ③ 建模型 + 载权重
model = resnet34(num_classes=5)
model.load_state_dict(torch.load('./resNet34.pth', map_location='cpu'))
model.eval()

# ④ 读图 → 预处理 → 加 batch 维
img = Image.open('./roses.jpg').convert('RGB')
x = preprocess(img).unsqueeze(0)          # (C, H, W) → (1, C, H, W)

# ⑤ 推理
with torch.no_grad():
    prob = torch.softmax(model(x), dim=1) # 输出转概率
conf, idx = torch.max(prob, dim=1)        # 取最大概率及其下标

print(class_indict[str(idx.item())], f'{conf.item():.3f}')
```

训练时顺手记录的类别映射（`train.py` 里的 `/train` 目录名）：

```python
flower_list = train_dataset.class_to_idx             # {'daisy':0, 'dandelion':1, 'roses':2, ...}
cla_dict = dict((v, k) for k, v in flower_list.items())
json.dump(cla_dict, open('class_indices.json', 'w'), indent=4)   # {"0":"daisy", ...}
```

> 预测的精髓就是**四个对齐**：尺寸对齐、通道顺序对齐（NCHW）、数值范围对齐（归一化）、**类别索引对齐**。训练怎么处理，预测就得一模一样。

---

## 9.8 踩坑

1. **最后的 BN 后面不接 ReLU**。`BasicBlock.forward` 里第二次 `bn2` 之后直接 `out += identity`，**加完才 ReLU**。写成 `relu → bn2 → relu → +=` 是错的，残差相加前的非线性会破坏恒等映射的性质。

2. **`bias=False`**。卷积后紧跟 BN 时，BN 里的 `β` 会抵消卷积的偏置，留着纯属浪费参数。

3. **`downsample` 的触发条件别写少**：`stride != 1` **或** `in_channel != channel * expansion`。只判 stride 会漏掉"通道数变了但尺寸没变"的情况（比如 `include_top=False` 接到别的骨干后面时）。

4. **`self.in_channel` 的更新时机**。必须在第一个块 append 之后再赋值 —— 因为第一个块的输入通道还是**上一个 stage 的输出通道**。

5. **输入尺寸没硬性要求**。原始论文用 224×224（ImageNet），但网络靠 `AdaptiveAvgPool2d` 收尾，**尺寸换成 32×32 也成立**。以 ResNet-34 为例：

   | 阶段 | 32×32 输入 | 224×224 输入 |
   | --- | --- | --- |
   | conv1 (s2) | 16 | 112 |
   | maxpool (s2) | 8 | 56 |
   | layer1 | 8 | 56 |
   | layer2 (s2) | 4 | 28 |
   | layer3 (s2) | 2 | 14 |
   | layer4 (s2) | 1 | 7 |
   | avgpool | **1×1** ✅ | **1×1** ✅ |

   所以 CIFAR-10 的 32×32 可以直接喂进去，不必强行 resize 到 224（当然，小图上特征少，效果会打折）。

6. **加载预训练权重的顺序别搞反**。`fc` 层形状对不上时，`strict=False` **也救不了** —— 它只能忽略"多了/少了某个 key"，而**形状不匹配（size mismatch）是硬错误**：

   ```
   RuntimeError: Error(s) in loading state_dict for ResNet:
       size mismatch for fc.weight: copying a param with shape torch.Size([10, 512])
       from checkpoint, the shape in current model is torch.Size([5, 512]).
   ```

   所以迁移学习的正确顺序是（原 `train.py` 里被注释掉的那段就是这个套路）：

   ```python
   net = resnet34()                                    # ① 先按预训练的类别数（1000）建模型
   net.load_state_dict(torch.load('resnet34-pre.pth')) # ② 形状匹配，直接加载
   for p in net.parameters():                          # ③ 冻结骨干
       p.requires_grad = False
   net.fc = nn.Linear(net.fc.in_features, num_classes) # ④ 最后才换分类头
   ```

   如果模型已经建成了自己的类别数、又想复用预训练骨干，就**手动过滤掉 `fc` 的权重**：

   ```python
   state = {k: v for k, v in torch.load('resnet34-pre.pth').items()
            if not k.startswith('fc.')}
   missing, unexpected = net.load_state_dict(state, strict=False)
   # 此时 missing 里会列出 ['fc.weight', 'fc.bias']，符合预期
   ```

7. **`expansion` 只影响出口通道**。`BasicBlock.expansion = 1` 不是"没用"，而是 ResNet 主体统一用 `channel * block.expansion` 算通道时的乘数 —— 写成 1 才能让两种块共用同一套 `_make_layer`。

---

## 9.9 小结

| 概念 | 要点 |
| --- | --- |
| 退化问题 | 网络变深反而训练误差上升，不是过拟合，是梯度传不下去 |
| 残差学习 | 让网络学 `F(x) = H(x) - x`，输出 `F(x) + x`；恒等映射变简单，梯度有捷径 |
| 两种捷径 | 实线（shape 一致，直接加）/ 虚线（1×1 卷积 + BN 变换后再加） |
| 两种块 | BasicBlock（两个 3×3，`expansion=1`）/ Bottleneck（1×1→3×3→1×1，`expansion=4`） |
| `_make_layer` | 每个 stage 只有第一个块换尺寸/通道，其余块 shape 不变 |
| 训练套路 | `train()/eval()` 切换、`no_grad()` 验证、按最优验证精度存权重 |

> 走到这里，`05`（CNN 原理）→ `06`（目标检测）→ `07`（用现成 ResNet 迁移）→ `09`（手写 ResNet）串成了一条线：
> **知道卷积为什么行 → 知道检测怎么用 → 会调预训练模型 → 能自己写出骨干网络。**

---

> 📌 回顾整套笔记：[[index]] · [[01-OpenCV基础]] · [[02-OpenCV进阶]] · [[03-OpenCV应用]] · [[04-机器学习]] · [[05-深度学习与CNN]] · [[06-目标检测]] · [[07-迁移学习]] · [[08-训练日志分析与可视化]]
