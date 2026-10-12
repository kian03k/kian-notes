---
tags: [cv, opencv, python, 图像处理]
created: 2026-10-12
updated: 2026-10-12
status: ok
---

# 01 · OpenCV 基础

> 本章目标：把「一张图」在计算机里到底是什么搞清楚，然后学会最基本的读取、显示、保存、绘图和运算。
> 原始代码：`1/01、opencv基础.py` ~ `1/05、图像运算.py`

---

## 1.1 OpenCV 是什么

**OpenCV（Open Source Computer Vision Library）** 是 Intel 发起并维护的开源计算机视觉库，用 C/C++ 写成，同时提供 Python、Java 等接口。Python 版本叫 **OpenCV-Python**：底层还是 C++，但你在 Python 里调用，兼顾了**易读**和**性能**。

它的应用很广：图像拼接、降噪、产品质检、人脸识别、动作跟踪、无人驾驶……

```bash
# 安装（国内建议加清华源加速）
pip install opencv-python==4.3.0.38 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

```python
import cv2      # OpenCV 的 Python 接口
import numpy as np
import matplotlib.pyplot as plt
```

> 💡 一个关键认知：**OpenCV-Python 里所有图像都是 numpy 数组**。理解 numpy 数组，就理解了一半的图像处理。

---

## 1.2 图像的读取 / 显示 / 保存

### 读取 —— `cv2.imread`

```python
# 读取一张图，返回 numpy 数组
img = cv2.imread('data/lena.png')

# 第二个参数 flags 控制读取方式
img_color   = cv2.imread('data/lena.png', cv2.IMREAD_COLOR)      # 彩色（默认，丢透明度）
img_gray    = cv2.imread('data/lena.png', cv2.IMREAD_GRAYSCALE)  # 灰度
img_alpha   = cv2.imread('data/1.jpg',  cv2.IMREAD_UNCHANGED)    # 保留透明通道
# 也可以直接用整数：1=彩色，0=灰度，-1=保留原样
```

| flags | 整数简写 | 含义 |
| --- | --- | --- |
| `cv2.IMREAD_COLOR` | `1` | 彩色加载，忽略透明度（**默认**） |
| `cv2.IMREAD_GRAYSCALE` | `0` | 灰度加载 |
| `cv2.IMREAD_UNCHANGED` | `-1` | 原样加载，含 alpha 透明通道 |

### 显示 —— `cv2.imshow`

```python
cv2.imshow('window_name', img)   # 第一个参数是窗口名，第二个是图像
cv2.waitKey(0)                   # 等待键盘输入，单位毫秒；0 = 一直等
cv2.destroyAllWindows()          # 关闭所有窗口
```

- `cv2.waitKey(0)`：**必须要有**，否则窗口一闪而过。返回按下的键值，常配合 `== 27`（Esc）退出。
- `cv2.destroyAllWindows()`：关闭所有 OpenCV 窗口，释放资源。

### 保存 —— `cv2.imwrite`

```python
cv2.imwrite('data/black.jpg', img)   # (保存路径, 图像)
```

### 用 matplotlib 显示（了解坑）

`imshow` 是弹窗，画图/对比时常用 matplotlib。但有个**著名大坑**：

> ⚠️ **OpenCV 读图是 BGR 通道顺序，matplotlib 按 RGB 显示** —— 直接用 matplotlib 显示 OpenCV 读的图，**红蓝会颠倒**。

三种转法（任选其一）：

```python
# ① 用颜色空间转换函数
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# ② 用 numpy 把通道逆序（最简洁，推荐）
img = img[:, :, ::-1]

# ③ 拆通道再按 RGB 合并
b, g, r = cv2.split(img)
img = cv2.merge([r, g, b])

plt.imshow(img)
plt.show()
```

---

## 1.3 图像就是 numpy 数组

```python
img = cv2.imread('data/lena.png', 0)   # 灰度图

print(img.shape)   # (h, w)  灰度图两维：高、宽
print(img.dtype)   # uint8   每个像素 0~255 的无符号整数

img = cv2.imread('data/lena.png')      # 彩色图
print(img.shape)   # (h, w, c)  → c=3，通道顺序是 (B, G, R)
print(img.size)    # 像素总数 = h * w * c
```

要点：

- **形状顺序是 `(高 h, 宽 w, 通道 c)`**，不是常见的 `(宽, 高)`。取尺寸时容易记反。
- **数据类型是 `uint8`**（0~255）。做加减乘除时极易溢出/环绕，见 §1.7。
- **通道顺序是 BGR**，不是 RGB。

既然图像是数组，就可以直接**用 numpy 造一张图**：

```python
img = np.zeros((500, 500, 3), dtype=np.uint8)          # 全黑
img = np.ones((500, 500, 3), dtype=np.uint8) * 255     # 全白
img = np.random.randint(0, 256, (500, 300, 3), dtype=np.uint8)  # 随机噪点图
cv2.imshow('img', img); cv2.waitKey(0); cv2.destroyAllWindows()
```

> ⚠️ 造图时记得 `dtype=np.uint8`，否则 numpy 默认 float64，imshow 显示会异常。

---

## 1.4 读取 / 保存视频

视频 = 一帧一帧的图像。流程是：**捕获 → 逐帧读取 → 处理 → （可选）写入 → 释放**。

```python
cap = cv2.VideoCapture('data/car.mp4')   # 也可传 0 表示摄像头

if cap.isOpened():                       # 判断是否成功打开
    while True:
        ret, frame = cap.read()          # ret: 是否读到；frame: 这一帧图像
        if ret:
            cv2.imshow('video', frame)
            if cv2.waitKey(20) == 27:    # 每帧停 20ms，按 Esc 提前退出
                break
        else:                            # 读不到 → 视频结束
            break
else:
    print('视频捕获失败')

cap.release()                            # 释放摄像头/文件资源
cv2.destroyAllWindows()
```

**保存视频**要先生成 `VideoWriter`，需要帧率和画面尺寸：

```python
cap = cv2.VideoCapture('data/car.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')                 # 编码器（MP4 用 mp4v）
fps = cap.get(cv2.CAP_PROP_FPS)                          # 原视频帧率
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

writer = cv2.VideoWriter('data/car_save.mp4',
                         fourcc=fourcc, fps=fps,
                         frameSize=(w, h))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    writer.write(frame)          # 把每一帧写进去
cap.release()
writer.release()
cv2.destroyAllWindows()
```

> 💡 常见坑：写入的 `frameSize` 必须和实际帧尺寸一致，否则保存出来是坏文件。

---

## 1.5 感兴趣区域（ROI）

ROI = Region of Interest，就是**截取图像的一块矩形区域**。因为图像是数组，切片即可：

```python
img = cv2.imread('data/lena.png')

# 取人脸区域：img[行范围, 列范围]  → 行是 y(height)，列是 x(width)
face = img[140:260, 210:340]
cv2.imshow('face', face)

# 反向操作：把一块区域涂黑（赋值）
img[140:260, 210:340] = np.zeros((260-140, 340-210, 3), dtype=np.uint8)
cv2.imshow('img', img)

cv2.waitKey(0); cv2.destroyAllWindows()
```

> ⚠️ 切片语法是 `img[y1:y2, x1:x2]` —— **先高度后宽度**，别写反。

---

## 1.6 绘制图形

在一张图（或空白画布）上画点、线、形状、文字：

```python
img = np.zeros((600, 600, 3), dtype=np.uint8)

cv2.line(img, (200, 200), (500, 500), color=[100, 255, 0], thickness=3)      # 直线
cv2.circle(img, (300, 300), 100, color=[255, 0, 255], thickness=5)            # 空心圆
cv2.circle(img, (300, 300), 100, color=[255, 255, 255], thickness=-1)         # 实心圆(-1=填充)
cv2.rectangle(img, (200, 200), (500, 500), color=[200, 50, 0], thickness=3)   # 矩形
cv2.ellipse(img, (300, 300), (300, 200), 45, 0, 360, color=[20, 100, 0], thickness=3)  # 椭圆

# 多边形：把所有点放进一个数组
pts = np.array([[(100, 100), (200, 300), (300, 200), (400, 100), (500, 200)]])
cv2.polylines(img, [pts], isClosed=True, color=[0, 0, 255], thickness=3)      # 折线/多边形
cv2.fillPoly(img, [pts], color=[0, 0, 255])                                   # 填充多边形

cv2.putText(img, 'lena', (100, 100),
            fontFace=cv2.FONT_ITALIC, fontScale=2,
            color=[255, 255, 0], thickness=3)                                 # 文字

cv2.imshow('img', img); cv2.waitKey(0); cv2.destroyAllWindows()
```

要点：

- `thickness=-1` 表示**填充**（画实心图形）。
- 文字用 `cv2.putText`，坐标是**文字左下角**的基准点。
- ⚠️ `cv2.putText` **不能直接写中文**（会显示成 `???`），中文要用 PIL 绘制。

> 应用示例：检测到人脸后，用 `cv2.rectangle` 把框画上去（见 [[03-OpenCV应用]]）。

---

## 1.7 图像运算

图像运算就是**逐像素处理**，分**算术运算**（加减乘除）和**逻辑运算**（与或非异或，也叫按位运算）。

> ⚠️ 前提：参与运算的两张图，**尺寸和类型必须完全一致**，否则 OpenCV 报错。

### 算术运算

同一个 `+` 号，numpy 和 OpenCV 行为**不一样**，这是最容易踩的坑：

```python
# 加法
dst = img1 + img2                 # numpy：超过 255 会对 256 取模（255+1=0，变黑！）
dst = cv2.add(img1, img2)         # OpenCV：超过 255 直接截断为 255（更符合直觉）
dst = cv2.addWeighted(img1, 0.3, img2, 0.8, 0)   # 加权和：0.3*a + 0.8*b + 0

# 减法
dst = img2 - img1                 # numpy：小于 0 对 256 取模
dst = cv2.subtract(img2, img1)    # OpenCV：小于 0 截断为 0

# 乘除
dst = cv2.multiply(img2, img1)
dst = cv2.divide(img1, img2)
```

**一句话记住**：想让它"加爆了变白、减没了变黑"，用 `cv2.add / cv2.subtract`；用 `+ -` 会出现**取模环绕**（黑→白突变的怪象）。

### 逻辑运算与掩膜（mask）

逻辑运算是按二进制位操作，常用来**抠图/叠加**：

```python
img1 = cv2.imread('data/aa0.png')
h, w, c = img1.shape
img2 = cv2.imread('data/bb0.png')
img2 = cv2.resize(img2, (w, h))          # 尺寸对齐

mask     = cv2.imread('data/mask.png', 0)   # 掩膜：8 位单通道
mask_not = cv2.bitwise_not(mask)            # 掩膜取反

# 用掩膜从两张图各取一半，再拼起来
dst1 = cv2.bitwise_and(img2, img2, mask=mask)      # 取 img2 的 mask 区域
dst2 = cv2.bitwise_and(img1, img1, mask=mask_not)  # 取 img1 的 mask 之外区域
dst  = cv2.add(dst1, dst2)                          # 叠加

cv2.imshow('img', dst); cv2.waitKey(0); cv2.destroyAllWindows()
```

逻辑运算的规则（转成二进制后）：

| 运算 | 函数 | 规则 |
| --- | --- | --- |
| 与 AND | `cv2.bitwise_and` | 全 1 才 1，遇 0 则 0 |
| 或 OR | `cv2.bitwise_or` | 全 0 才 0，遇 1 则 1 |
| 非 NOT | `cv2.bitwise_not` | 遇 0 变 1，遇 1 变 0 |
| 异或 XOR | `cv2.bitwise_xor` | 不同为 1，相同为 0 |

> **掩膜（mask）是什么**：一张"遮罩"，控制运算只作用在指定区域。掩膜值非空的像素才参与运算，其余置 0。掩膜一般是 **8 位单通道**图。

---

## 本章小结

| 操作 | 关键 API |
| --- | --- |
| 读图 | `cv2.imread(path, flags)` |
| 显示 | `cv2.imshow` + `cv2.waitKey(0)` + `cv2.destroyAllWindows()` |
| 保存 | `cv2.imwrite(path, img)` |
| 图像模型 | numpy 数组，`(h, w, c)`，`uint8`，BGR |
| 读写视频 | `cv2.VideoCapture` / `cv2.VideoWriter` |
| ROI | `img[y1:y2, x1:x2]` |
| 绘图 | `line / circle / rectangle / ellipse / polylines / putText` |
| 运算 | `cv2.add/subtract/multiply/divide`、`cv2.bitwise_*` |

**练习**：用 numpy 造一张 512×512 的黑色画布，在上面画一个红色矩形框 + 一段文字，保存为 `test.jpg` 并显示出来。

➡️ 下一章：[[02-OpenCV进阶]] —— 鼠标交互、几何变换、形态学。
