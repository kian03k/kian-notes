---
tags: [cv, opencv, python, 图像处理]
created: 2026-10-12
updated: 2026-10-12
status: ok
---

# 02 · OpenCV 进阶

> 本章目标：让图像"动起来、变起来" —— 用鼠标和滑动条做交互、对图像做几何变换（缩放/旋转/透视）、在不同色彩空间之间转换、以及用形态学处理形状。
> 原始代码：`2/01、鼠标事件.py` ~ `2/04、透射变换小案例.py`

---

## 2.1 鼠标事件

OpenCV 可以监听窗口里的鼠标动作（按下、松开、双击……），并调用你写的**回调函数**。

```python
import cv2
import numpy as np

def draw_circle(event, x, y, flags, param):
    """鼠标回调函数：event=事件类型, (x,y)=鼠标坐标"""
    if event == cv2.EVENT_LBUTTONDOWN:      # 左键按下
        cv2.circle(img, (x, y), 20, (0, 0, 255))
    elif event == cv2.EVENT_RBUTTONDBLCLK:  # 右键双击
        cv2.circle(img, (x, y), 20, (0, 255, 0))

img = np.zeros((500, 500, 3), dtype=np.uint8)
cv2.imshow('img', img)
cv2.setMouseCallback('img', draw_circle)    # 绑定：窗口 'img' 的鼠标事件交给 draw_circle

while True:
    cv2.imshow('img', img)
    if cv2.waitKey(20) == 27:               # 按 Esc 退出
        break
cv2.destroyAllWindows()
```

**回调函数签名固定**：`(event, x, y, flags, param)`。

- `event`：事件类型，如 `EVENT_LBUTTONDOWN`（左键按下）、`EVENT_RBUTTONDBLCLK`（右键双击）、`EVENT_MOUSEMOVE` 等。
- `x, y`：鼠标在窗口内的坐标。
- 注册用 `cv2.setMouseCallback(winname, onMouse)`。

> 用途：手动标注、画框选 ROI、点击取色……

---

## 2.2 轨迹栏（滑动条）

滑动条通过拖拽实时改参数，是**调参神器**（比如调阈值看效果）。

```python
import cv2
import numpy as np

def call(x):
    pass    # 回调可以什么都不做，值在循环里主动读

img = np.zeros((500, 500, 3), dtype=np.uint8)
cv2.imshow('img', img)

# 创建三条滑动条，控制 B/G/R 分量（0~255）
cv2.createTrackbar('r', 'img', 0, 255, call)
cv2.createTrackbar('g', 'img', 0, 255, call)
cv2.createTrackbar('b', 'img', 0, 255, call)

while True:
    r = cv2.getTrackbarPos('r', 'img')     # 读取当前滑块位置
    g = cv2.getTrackbarPos('g', 'img')
    b = cv2.getTrackbarPos('b', 'img')

    img[:] = [b, g, r]                      # 用滑动条的值填充整张图（BGR 顺序）
    cv2.imshow('img', img)

    if cv2.waitKey(10) == 27:
        break
cv2.destroyAllWindows()
```

关键 API：

| 函数 | 作用 |
| --- | --- |
| `cv2.createTrackbar(名称, 窗口, 默认值, 最大值, 回调)` | 创建滑动条 |
| `cv2.getTrackbarPos(名称, 窗口)` | 读取当前值 |

> 上面这段就是一个**取色器**：拖动三条滑动条，实时看到颜色变化。

---

## 2.3 几何变换

### （1）缩放 —— `cv2.resize`

```python
dst = cv2.resize(img, (200, 200))                    # 指定目标尺寸 (宽, 高)
dst = cv2.resize(img, None, fx=2, fy=2)              # 按比例：放大 2 倍
dst = cv2.resize(img, (1000, 500), interpolation=cv2.INTER_CUBIC)   # 指定插值
```

**插值方法**（决定缩放后的像素怎么算）：

| 方法 | 说明 | 建议 |
| --- | --- | --- |
| `INTER_NEAREST` | 最近邻，最快、最粗糙 | 少用 |
| `INTER_LINEAR` | 双线性（默认） | 放大常用 |
| `INTER_AREA` | 区域重采样 | **缩小**时最好 |
| `INTER_CUBIC` | 三次样条，质量高、较慢 | 放大可用 |

> 经验：**缩小用 `INTER_AREA`，放大用 `INTER_LINEAR` / `INTER_CUBIC`**。
> ⚠️ `resize` 的尺寸参数是 **`(宽, 高)`**，和 shape 的 `(高, 宽)` 顺序相反！

### （2）翻转 —— `cv2.flip`

```python
cv2.flip(img, 0)    # 绕 x 轴翻转（上下颠倒）
cv2.flip(img, 1)    # 绕 y 轴翻转（左右镜像）
cv2.flip(img, -1)   # 同时翻转（旋转 180°）
```

### （3）仿射变换 —— `cv2.warpAffine`

仿射变换 = **平移 + 旋转 + 缩放**的组合，用一个 **2×3 的变换矩阵 M** 描述。特点是保持**平直性**（直线还是直线）和**平行性**（平行线还是平行线）。

```python
# ① 手写矩阵：只平移（x 移 100，y 移 80）
M = np.array([[1, 0, 100], [0, 1, 80]], np.float32)
dst = cv2.warpAffine(img, M, (800, 500))

# ② 旋转：用函数生成矩阵（更常用）
M = cv2.getRotationMatrix2D(center=(100, 100), angle=-30, scale=1)
#                        旋转中心            角度(正=逆时针)      缩放
dst = cv2.warpAffine(img, M, (800, 500))

# ③ 由三对点自动求矩阵（原图 3 点 → 目标图 3 点）
pts1 = np.float32([[0, 0], [500, 0], [500, 350]])
pts2 = np.float32([[0, 0], [300, 300], [50, 500]])
M = cv2.getAffineTransform(pts1, pts2)
dst = cv2.warpAffine(img, M, (800, 500))
```

### （4）透视变换 —— `cv2.warpPerspective`

仿射变换保平行，透视变换不保 —— 它能把**任意四边形**映射成另一个四边形，常用于**矫正倾斜拍摄的文档/车牌**。

```python
# 由四对点求 3×3 矩阵
pts1 = np.float32([[0, 0], [500, 0], [500, 350], [0, 350]])   # 原图四角
pts2 = np.float32([[0, 0], [500, 0], [300, 300], [100, 300]]) # 目标四角
M = cv2.getPerspectiveTransform(pts1, pts2)
dst = cv2.warpPerspective(img, M, (800, 800))
```

**实战小案例**（`2/04`）：把倾斜的车牌图"摆正"：

```python
img = cv2.imread('data/car_lain.png')
pts1 = np.float32([[170, 0], [323, 0], [448, 230], [58, 230]])   # 车牌在原图里的四个角
pts2 = np.float32([[58, 0], [448, 0], [448, 230], [58, 230]])    # 摆正后的四个角
M = cv2.getPerspectiveTransform(pts1, pts2)
dst = cv2.warpPerspective(img, M, (800, 800))
```

> 仿射 = 2×3 矩阵 + `warpAffine` + 3 对点；透视 = 3×3 矩阵 + `warpPerspective` + 4 对点。**记这个对应关系就够了**。

### （5）图像金字塔 —— `pyrUp` / `pyrDown`

金字塔是图像的**多尺度表示**，一层层缩小（或放大），用于图像分割、特征提取。

```python
dst = cv2.pyrUp(img)     # 上采样，尺寸 ×2（变模糊）
dst = cv2.pyrDown(img)   # 下采样，尺寸 ÷2
```

---

## 2.4 色彩空间

**色彩空间**（颜色空间）是用不同方式描述颜色的模型。常用：RGB、HSV、Lab、GRAY。

| 色彩空间 | 组成 | 特点 |
| --- | --- | --- |
| GRAY | 灰度值 0~255 | 无色彩，只有亮度 |
| RGB | R/G/B 三原色 | 显示屏用；红(255,0,0)、黑(0,0,0)、白(255,255,255) |
| HSV | 色调 H / 饱和度 S / 明度 V | **更符合人描述颜色**；H 按角度 0~360°（红 0°、绿 120°、蓝 240°） |
| Lab | 亮度 L + 色度 a、b | 基于人眼感觉设计，L∈[0,100]，a/b∈[-127,127] |

转换统一用 `cv2.cvtColor`：

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lab  = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
```

**灰度怎么来的**：人眼对绿色最敏感，所以加权公式近似为
`Gray ≈ 0.299·R + 0.587·G + 0.114·B`（这正是 `COLOR_BGR2GRAY` 内部的算法）。

> 💡 **HSV 的实用价值**：做颜色筛选（比如找红色物体）时，用 HSV 比 RGB 稳定得多 —— 因为亮度变化对 H 影响小。后面轮廓检测会用 `cv2.inRange` 在 HSV 里做颜色分割。

---

## 2.5 形态学变换

**形态学（Morphology）** 是基于形状的变换，核心工具是一个 **结构元（kernel）**（0/1 矩阵，形状可选矩形/椭圆/十字）。

```python
# 创建结构元
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,    ksize=(3, 3))  # 矩形
# kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,   ksize=(9, 9))  # 十字
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize=(9, 9))  # 椭圆
```

两个基本操作 + 四个组合操作：

```python
# 腐蚀：取邻域最小值 → "变瘦"（去毛刺、断开粘连）
dst = cv2.erode(img, kernel, iterations=1)
# 膨胀：取邻域最大值 → "变胖"（填补空洞、连接断裂）
dst = cv2.dilate(img, kernel, iterations=1)

# 组合操作（一个函数搞定）
cv2.morphologyEx(img, op=cv2.MORPH_OPEN,     kernel=kernel, iterations=1)  # 开：先腐后膨，去毛刺
cv2.morphologyEx(img, op=cv2.MORPH_CLOSE,    kernel=kernel, iterations=1)  # 闭：先膨后腐，填黑洞
cv2.morphologyEx(img, op=cv2.MORPH_TOPHAT,   kernel=kernel, iterations=1)  # 顶帽：原图-开，提取毛刺
cv2.morphologyEx(img, op=cv2.MORPH_BLACKHAT, kernel=kernel, iterations=1)  # 黑帽：闭-原图，提取空洞
cv2.morphologyEx(img, op=cv2.MORPH_GRADIENT, kernel=kernel, iterations=1)  # 梯度：膨-腐，提取简单轮廓
```

| 操作 | = | 作用 |
| --- | --- | --- |
| **腐蚀** erode | 取邻域最小 | 变瘦、去毛刺 |
| **膨胀** dilate | 取邻域最大 | 变胖、填空 |
| **开运算** open | 先腐蚀后膨胀 | 去小噪点/毛刺 |
| **闭运算** close | 先膨胀后腐蚀 | 填小孔洞 |
| **梯度** gradient | 膨胀 − 腐蚀 | 提取轮廓 |
| **顶帽** tophat | 原图 − 开 | 提取亮的小细节 |
| **黑帽** blackhat | 闭 − 原图 | 提取暗的小细节 |

> ⚠️ 形态学一般作用于**二值图或灰度图**，彩色图先转灰度。`iterations` 越大效果越强。

---

## 本章小结

| 主题 | 关键 API |
| --- | --- |
| 鼠标 | `cv2.setMouseCallback` |
| 滑动条 | `cv2.createTrackbar` / `cv2.getTrackbarPos` |
| 缩放 | `cv2.resize`（缩小用 `INTER_AREA`，放大用 `INTER_CUBIC`） |
| 翻转 | `cv2.flip`（0 上下 / 1 左右 / -1 都翻） |
| 仿射 | `cv2.getRotationMatrix2D` / `getAffineTransform` + `warpAffine` |
| 透视 | `cv2.getPerspectiveTransform` + `warpPerspective` |
| 金字塔 | `cv2.pyrUp` / `cv2.pyrDown` |
| 色彩空间 | `cv2.cvtColor` |
| 形态学 | `erode/dilate/morphologyEx` |

**练习**：读一张带文字的倾斜照片，用透视变换把它"摆正"（提示：找出文档四角 → `getPerspectiveTransform` → `warpPerspective`）。

➡️ 下一章：[[03-OpenCV应用]] —— 滤波、边缘检测、轮廓、人脸检测。
