---
tags: [cv, opencv, python, 图像处理, 边缘检测, 轮廓]
created: 2026-10-12
updated: 2026-10-12
status: ok
---

# 03 · OpenCV 应用

> 本章目标：综合运用前三章 —— 先去噪（滤波）、再找边缘、然后提取轮廓，最后做一个经典的"人脸检测"。
> 原始代码：`3/01、图像色彩空间变换.py` ~ `3/05、人脸检测.py`

---

## 3.1 图像滤波

### 先理解：图像为什么是"波"

图像由像素组成。**色彩的波动 = 频率**：

- **色彩剧烈变化**的地方（轮廓、噪声）→ **高频**区域
- **色彩平滑过渡**的地方 → **低频**区域

**滤波器**就是"从混合信号里挑出想要的信号"：

- **低通滤波**：削弱高频（去噪、平滑）→ 均值、方框、高斯、中值、双边
- **高通滤波**：削弱低频（找边缘）→ Sobel、Laplacian、Canny

### 低通滤波（去噪 / 平滑）

```python
# ① 均值滤波：邻域像素取平均
dst = cv2.blur(img, (5, 5))

# ② 方框滤波：均值滤波的"可归一化"版本
dst = cv2.boxFilter(img, ddepth=-1, ksize=(5, 5), normalize=False)

# ③ 高斯滤波：中心权重更大，按高斯分布加权（最常用）
dst = cv2.GaussianBlur(img, ksize=(5, 5), sigmaX=0, sigmaY=0)

# ④ 中值滤波：取邻域中值，对"椒盐噪声"特别有效
dst = cv2.medianBlur(img, 5)

# ⑤ 双边滤波：去噪同时保边（考虑空间距离 + 灰度相似度）
dst = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
```

| 滤波 | 原理 | 特点 / 适用 |
| --- | --- | --- |
| 均值 blur | 邻域平均 | 简单，会糊掉边缘 |
| 方框 boxFilter | 可调归一化 | 均值的一般形式 |
| 高斯 GaussianBlur | 中心权重高 | 常用，平滑自然 |
| 中值 medianBlur | 邻域中值 | **专治椒盐噪声**，不糊边缘 |
| 双边 bilateralFilter | 距离 + 灰度 | **保边去噪**，慢 |

> `ksize` 是滤波核大小，**必须是奇数**（3、5、7…），否则报错。

### 高通滤波（找边缘）

见下一节。

---

## 3.2 边缘检测

**边缘** = 图像中像素值变化明显的位置。检测方法分三类，OpenCV 里常用的是**梯度类（Sobel）**和**二阶导类（Laplacian、Canny）**。

```python
# ① Sobel：一阶梯度，可分别算 x / y 方向
dst = cv2.Sobel(img, ddepth=-1, dx=1, dy=0)   # dx=1 算水平方向梯度

# ② Laplacian：二阶导数，旋转不变
dst = cv2.Laplacian(img, ddepth=-1)

# ③ Canny：多级边缘检测，公认"最优"边缘算法
dst = cv2.Canny(img, 80, 170)                 # 80=低阈值, 170=高阈值
```

**Canny 的四步**（理解它，就理解了边缘检测）：

1. **高斯平滑**：先去噪
2. **计算梯度**：求幅值和方向（方向取 0/45/90/135°）
3. **非极大值抑制**：只保留梯度方向上的局部最大，把粗边"变细"
4. **滞后阈值**：>高阈值 → 保留为边缘；<低阈值 → 丢弃；介于两者 → 只有连着强边缘才保留

> ⚠️ 用 `cv2.Sobel` 检测边缘时，`ddepth=-1`（即保持 uint8）会导致**负梯度被截断**，边缘可能不全。正规做法是先转 `cv2.CV_64F` 再取绝对值，但入门阶段用 Canny 更省事。

**ddepth 常见取值**：`-1`(同输入)、`cv2.CV_8U`(无符号)、`cv2.CV_16S`(有符号)、`cv2.CV_32F`(浮点)。

---

## 3.3 轮廓查找

**轮廓** = 具有相同颜色/灰度的连续点组成的曲线，用于**图形分析**和**物体识别检测**。

完整流程：**灰度 → 二值化 → 形态学去噪 → 找轮廓 → 绘制/分析**。

```python
import cv2

img  = cv2.imread('data/ditu.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (3, 3), sigmaX=0)          # 去噪

# 二值化：把图变成黑白（阈值 110，大于变 255，否则 0）
_, binary = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)

# 形态学：闭运算填孔 + 开运算去毛刺
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=5)
binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  kernel, iterations=5)

# 找轮廓
contours, _ = cv2.findContours(binary, mode=cv2.RETR_EXTERNAL,
                               method=cv2.CHAIN_APPROX_NONE)

# 在原图上画所有轮廓
cv2.drawContours(img, contours, contourIdx=-1, color=[0, 0, 255], thickness=2)
```

### `findContours` 的两个关键参数

**mode —— 查找模式**：

| 值 | 含义 |
| --- | --- |
| `RETR_EXTERNAL` | 只检测最外层轮廓 |
| `RETR_LIST` | 检测所有轮廓，不建立层级关系（最常用） |
| `RETR_CCOMP` | 两级：外轮廓 + 内孔 |
| `RETR_TREE` | 树形结构，完整层级 |

**method —— 近似方法**：

| 值 | 含义 |
| --- | --- |
| `CHAIN_APPROX_NONE` | 保存轮廓上**所有点** |
| `CHAIN_APPROX_SIMPLE` | 只保存**角点**（如四边形只存 4 角），省内存，常用 |

### 轮廓分析

```python
# 面积与周长
area = cv2.contourArea(contours[2])                    # 轮廓面积（像素）
peri = cv2.arcLength(contours[2], closed=True)         # 周长

# 最大外接矩形（正矩形，无旋转）
x, y, w, h = cv2.boundingRect(contours[2])
cv2.rectangle(img, (x, y), (x + w, y + h), color=[0, 255, 0])

# 最小外接矩形（可旋转）——返回 (中心, 宽高, 旋转角)
rect = cv2.minAreaRect(contours[2])

# 最小外接圆
(cx, cy), r = cv2.minEnclosingCircle(contours[2])
```

**外接矩形的两种**：

- `boundingRect` → **最大外接矩形**（边与坐标轴平行）
- `minAreaRect` → **最小外接矩形**（紧贴轮廓，可带旋转角）

> 实战中常用 `contourArea` **过滤掉太小的轮廓**（噪点），只留感兴趣的大目标。另外颜色筛选用 `cv2.inRange`（HSV 空间）比二值化更鲁棒。

---

## 3.4 人脸检测

OpenCV 自带 **Haar 级联分类器**，是一个现成的"人脸检测器"（无需训练）。

```python
import cv2

img  = cv2.imread('data/person.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 加载分类器模型（xml 随 opencv 一起安装）
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# 眼睛检测（同理）：
# cv2.data.haarcascades + 'haarcascade_eye.xml'

# 检测：返回人脸矩形列表 [(x, y, w, h), ...]
faces = face_cascade.detectMultiScale(gray,
            scaleFactor=1.2, minNeighbors=5, minSize=(2, 2))

# 画框
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow('img', img); cv2.waitKey(0); cv2.destroyAllWindows()
```

**`detectMultiScale` 参数**：

| 参数 | 含义 |
| --- | --- |
| `scaleFactor` | 每次缩放比例（1.1~1.3），太大易漏检 |
| `minNeighbors` | 一个区域被"确认"为脸的最少邻居数，越大越严 |
| `minSize` | 目标最小尺寸 |

> 💡 `cv2.data.haarcascades` 是一个便捷属性，直接指向 OpenCV 自带的 `data` 目录，比写死绝对路径稳（原代码里写的是 `D:\install\python38\...`，换机器就报错）。
>
> ⚠️ 级联分类器用的是老式 Haar 特征，**正脸效果好、侧脸/遮挡差**。要更准可以上 DNN 模型或 YOLO 人脸检测。本章重点理解"**检测框 = 在原图上画矩形**"这条主线即可。

---

## 本章小结

| 主题 | 关键 API |
| --- | --- |
| 低通滤波 | `blur` / `boxFilter` / `GaussianBlur` / `medianBlur` / `bilateralFilter` |
| 高通/边缘 | `Sobel` / `Laplacian` / `Canny` |
| 二值化 | `cv2.threshold` / `cv2.inRange` |
| 形态学 | `erode` / `dilate` / `morphologyEx` |
| 找轮廓 | `cv2.findContours` |
| 画轮廓 | `cv2.drawContours` |
| 轮廓分析 | `contourArea` / `arcLength` / `boundingRect` / `minAreaRect` / `minEnclosingCircle` |
| 人脸检测 | `CascadeClassifier` + `detectMultiScale` |

**标准"物体检测"流水线**（记住这条线）：
`灰度 → 滤波去噪 → 二值化 → 形态学 → 找轮廓 → 过滤 → 分析/画框`

**练习**：用轮廓检测数出一张图片里的硬币数量（提示：二值化后找轮廓，用面积过滤小噪点，数剩下的轮廓个数）。

---

## 阶段一小结（OpenCV）

到这里你已经掌握：**读入图像 → 变换处理 → 提取信息（边缘/轮廓/目标）** 的完整链条。这是计算机视觉的"手上功夫"。
接下来进入 **阶段二**：让计算机**从数据里自己学**规律 —— [[04-机器学习]]。
