---
tags: [python, pandas, 性能]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# 逐行遍历：itertuples 用法

## 1. 先说结论

Pandas 是向量化引擎，`for` 循环在大数据集（>10 万行）下极慢（慢 10~100 倍）。能用 `df[df['B'] > 5]` 这类向量化筛选，就不要用循环。

但有些场景**必须**逐行处理：每行做复杂规则判断、根据某列值动态决定是否修改其他列、调用外部 API、写日志等。这时要用**最高效**的遍历方式。

## 2. 推荐写法：df[列列表].itertuples()

"先选列 + `itertuples(index=False)`"是必须循环时最快、最清晰、最安全的方式。

```python
import pandas as pd

df = pd.DataFrame({
    '姓名': ['张三', '李四', '王五', '赵六'],
    '年龄': [23, 25, 22, 28],
    '城市': ['北京', '上海', '广州', '深圳'],
    '薪资': [8000, 12000, 9000, 15000],
    '部门': ['销售', '技术', '销售', '技术']
})

target_columns = ['姓名', '年龄', '薪资']  # 只读关心的列

for row in df[target_columns].itertuples(index=False):  # index=False 不返回索引
    name, age, salary = row  # 按列顺序解包
    if salary > 10000:
        print(f"高薪员工：{name}（{salary}元）")
```

`itertuples()` 返回 namedtuple，支持属性访问，性能接近原生 Python 循环。

## 3. 方法对比

| 方法 | 速度 | 可读性 | 推荐度 | 说明 |
|---|---|---|---|---|
| `df[['A','B']].itertuples(index=False)` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 强烈推荐 | 只读关心的列，快且结构清晰 |
| `df.itertuples()`（全列） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 推荐 | 只用其中几列时浪费内存 |
| `df.iterrows()` | ⭐⭐ | ⭐⭐⭐ | 不推荐 | 每行生成 Series，开销大，慢 10 倍以上 |
| `for i in range(len(df)): df.iloc[i]` | ⭐ | ⭐ | 绝对不要 | 最慢 |

## 4. 属性访问与特殊列名

列名是合法 Python 标识符（无空格、不以数字开头、非关键字）时，可用属性访问，更优雅：

```python
for row in df[['姓名', '薪资']].itertuples(index=False):
    if row.薪资 > 10000:
        print(f"高薪员工：{row.姓名}，薪资：{row.薪资}")
```

列名含空格或特殊字符（如 `'年收入(元)'`）时，属性访问会语法错误，改用位置访问：

```python
for row in df.itertuples(index=False):
    if row[0] > 10000:   # 第 0 列
        print(f"高收入：{row[0]} 元")
```

## 5. 实战案例：逐行判断 + 预警收集

需求：只读 `省份`、`项目名称`、`进度(%)` 三列；进度 > 90% 打印"重点项目"；进度 < 20% 记入预警列表。

```python
df = pd.DataFrame({
    '省份': ['广东', '广东', '江苏', '浙江'],
    '城市': ['广州', '深圳', '南京', '杭州'],
    '项目名称': ['项目A', '项目B', '项目C', '项目D'],
    '进度(%)': [85, 30, 95, 10],
    '负责人': ['张三', '李四', '王五', '赵六']
})

target_cols = ['省份', '项目名称', '进度(%)']
warnings = []

for row in df[target_cols].itertuples(index=False):
    province, project, progress = row  # 解包三列
    if progress > 90:
        print(f"重点项目：{province} - {project}（进度：{progress}%）")
    elif progress < 20:
        warnings.append((province, project, progress))

print("=== 预警项目汇总 ===")
for p, proj, pr in warnings:
    print(f"  {p} | {proj} | {pr}%")
```

### 边遍历边构建新 DataFrame

```python
rows = []
for row in df[target_cols].itertuples(index=False):
    if row[2] > 90:   # 进度 > 90
        rows.append({'省份': row[0], '项目名称': row[1], '进度(%)': row[2]})

result_df = pd.DataFrame(rows)
```

先用 list 收集字典，最后一次性 `pd.DataFrame(list)`——这是"逐行处理 + 动态构建结果"的经典模式。

## 6. 性能对比（10 万行实测）

```python
import time

df_big = pd.DataFrame({
    'A': range(100000),
    'B': [x % 10 for x in range(100000)],
    'C': [f'item_{i}' for i in range(100000)]
})

# 方法1：itertuples（推荐）
start = time.time()
count = 0
for row in df_big[['A', 'B']].itertuples(index=False):
    if row[1] > 5:
        count += 1
print("itertuples:", time.time() - start, "秒")   # ~0.15 秒

# 方法2：iterrows（慢）
start = time.time()
count = 0
for idx, row in df_big.iterrows():
    if row['B'] > 5:
        count += 1
print("iterrows:", time.time() - start, "秒")     # ~5.5 秒，慢约 30 倍

# 方法3：向量化（最快）
start = time.time()
count = (df_big['B'] > 5).sum()
print("向量化:", time.time() - start, "秒")       # ~0.001 秒
```

结论：**向量化 > itertuples > iterrows**。只有逻辑无法向量化时，才用 `itertuples()`。

## 7. 最佳实践

| 场景 | 推荐写法 |
|---|---|
| 必须逐行处理 | `for row in df[['列1','列2']].itertuples(index=False):` |
| 列名是合法标识符 | 用 `row.列名` 访问 |
| 列名含特殊字符 | 用 `row[0]`、`row[1]` 按位置访问 |
| 只是筛选符合条件的行 | 优先 `df[df['列'] > 条件]`（向量化） |
| 要构建新数据 | list 收集字典，最后 `pd.DataFrame(list)` |

## 8. 反面清单：绝对不要这样写

```python
# 慢：每次都按位置查整个 DataFrame
for i in range(len(df)):
    name = df.iloc[i]['姓名']
    age = df.iloc[i]['年龄']

# 慢且开销大：iterrows 每行都创建一个 Series 对象
for idx, row in df.iterrows():
    name = row['姓名']
```

一句话总结：**先选列，再遍历（`df[['关心的列']].itertuples(index=False)`），用属性或位置访问；别用 `iterrows()`，别用 `iloc[i]`。**

> 相关：[[06-str.contains向量化匹配]] 是同一主题（向量化优于循环）的另一个实战案例。

---

上一篇：[[02-三剑客merge-concat-groupby]]　下一篇：[[04-Excel多Sheet读写]]
