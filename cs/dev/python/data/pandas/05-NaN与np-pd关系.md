---
tags: [python, pandas, numpy]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# NaN 与 np、pd 的关系

## 1. 核心区别：一张表

| 对比项 | numpy（np） | pandas（pd） |
|---|---|---|
| 本质 | 数值计算引擎 | 带标签的数据分析工具 |
| 数据结构 | `ndarray`（多维数组） | `Series`（一维）、`DataFrame`（二维表） |
| 核心能力 | 快速数值运算（向量化） | 数据清洗、分组、合并、缺失值处理、带索引的列操作 |
| 适合 | 数学计算、数组运算 | 表格数据处理（类似 Excel） |

写代码时的分工：**用 pd 处理表格，用 np 做数学运算、生成数组或理解 NaN**。

## 2. 两者的关系：你写 pandas，背后是 numpy 在跑

```python
import numpy as np
import pandas as pd

s = pd.Series([1, 2, np.nan])
print(type(s[2]))   # <class 'float'> —— np.nan 是 float
```

- `pd.Series` 里存的 `NaN` 就是 `np.nan`；
- `pd.DataFrame` 的数字列，底层就是 `np.ndarray`；
- `df.mean()`、`df.sum()` 等运算都是 pandas 在调用 numpy。

因此大多数代码只需 `import pandas as pd`，不必显式操作 np——但要理解：**缺失值 NaN 是 NumPy 定义的**。

## 3. 四个常见混淆点

### 3.1 NaN 是 pd 的还是 np 的？

| 问题 | 答案 |
|---|---|
| `np.nan` 是什么 | NumPy 定义的"空值"，浮点类型 |
| `pd.NA` 是什么 | Pandas 1.0+ 引入的更通用缺失值（用于字符串、整数等可空类型） |
| 代码里看到的 NaN 是哪个 | 绝大多数情况下是 `np.nan`（pandas 默认用它） |

### 3.2 pd.isna() 与 np.isnan() 的区别

| 函数 | 支持类型 | 推荐 | 说明 |
|---|---|---|---|
| `pd.isna(x)` | 所有类型：数字、字符串、日期、对象 | 强烈推荐 | 统一接口，安全通用 |
| `np.isnan(x)` | 只支持数值类型（float/int） | 不推荐 | 遇到字符串直接报错 |

```python
s = pd.Series([1, 2, np.nan, "hello", None])

print(pd.isna(s))    # [False, False, True, False, True] —— 全部识别
print(np.isnan(s))   # TypeError: ufunc 'isnan' not supported
```

结论：判断缺失值一律用 `pd.isna()` / `pd.notna()` / `.dropna()`，不要碰 `np.isnan()`。

### 3.3 一行链式调用里，谁在干活？

```python
new_set = set(target_rows['PVID'].dropna())
```

| 步骤 | 谁干的 |
|---|---|
| `target_rows['PVID']` | pandas：取列，返回 Series |
| `.dropna()` | pandas：移除 NaN（内部按 `np.nan` 判断） |
| `set(...)` | Python 内置：转集合 |

用的是 pandas 的方法，底层依赖 numpy 的 NaN 定义——不需要关心 np 是怎么做的。

### 3.4 什么时候才直接用 np

`np.log()`、`np.sqrt()`、`np.random.randint(1, 100, size=10)` 这类纯数组运算用 numpy；日常表格操作几乎用不到。

## 4. 实战口诀

| 场景 | 用谁 |
|---|---|
| 操作表格（取列、筛选、合并、读写 Excel） | pd |
| 统计计算（`df.mean()`、`df.sum()`） | pd（内部调 np） |
| 判断是否空值 | `pd.isna(x)` |
| 判断一个值是不是 NaN | `pd.isna(x)`（**不要** `x == np.nan`） |
| 快速数组运算、生成随机数组 | np |

## 5. 记忆图

```text
你的数据 = pd.DataFrame（表格）
       │
       ├── 列：pd.Series（带标签的一维）
       │     └── 内部数据：np.ndarray（数字数组）
       │           └── 缺失值 = np.nan（NumPy 定义）
       │
       └── 常用操作：
             增删列   → pd
             去空值   → pd.dropna() / pd.isna()
             数学运算 → pd（自动调用 np）
             生成数组 → np（较少直接用）
```

数据处理工作中 95% 的时间只用 pandas；剩下 5% 用 numpy 来理解"为什么 NaN 是 float""为什么 `np.nan != np.nan`"这类问题。

## 6. 反例：永远不要用 == np.nan 判断空值

```python
s = pd.Series([1, 2, np.nan])

print(s[2] == np.nan)        # False！np.nan != np.nan
print(pd.isna(s[2]))         # True —— 唯一正确的判断方式
print(s.isna().iloc[2])      # True —— Series 自带写法，同样正确
```

`np.nan == np.nan` 为 `False` 是 IEEE 754 标准行为，不是 bug——所以**永远不要用 `== np.nan` 判断空值**。

## 7. 记忆点（可写进代码注释）

```python
# - 表格操作全用 pd
# - 缺失值判断用 pd.isna() / pd.notna()
# - 不要用 np.isnan() —— 遇到字符串/对象类型会报错
# - pd 底层用 np 做计算，日常代码基本不需要显式 import numpy
```

## 8. 附：直接用 numpy 时的最小子集

日常表格操作基本用不到 numpy，但出图、造测试数据、做矩阵运算时会碰上这几个：

```python
import numpy as np

A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
A * 2                       # 逐元素乘（不用循环）
A[:, 0]                     # 第 0 列
A[0:2, 1:]                  # 切片

np.max(A, axis=0)           # 沿 axis=0 求最大 → 每列最大  [7,8,9]
np.max(A, axis=1)           # 沿 axis=1 求最大 → 每行最大  [3,6,9]

x = np.linspace(-10, 10, 50)   # -10~10 等分 50 个点，画图常用
```

> `axis` 记法：`axis=0` 是"压掉行、每列留一个值"，`axis=1` 反之。新手最容易搞混，记不住就打印出来看形状。

> 相关：`np.linspace` 造图表的 x 轴序列，见 [[cs/dev/python/data/charts/01-matplotlib出图|charts/01-matplotlib出图]]。

---

上一篇：[[04-Excel多Sheet读写]]　下一篇：[[06-str.contains向量化匹配]]
