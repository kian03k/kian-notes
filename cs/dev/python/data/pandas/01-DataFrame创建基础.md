---
tags: [python, pandas]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# DataFrame 创建基础

## 1. 什么是 DataFrame

DataFrame 是 Pandas 最核心的**二维表格型数据结构**，类似 Excel 表格或 SQL 表：

- 每一列可以是**不同数据类型**（整数、字符串、布尔值等）；
- 每一列有**列名（column）**，每一行有**行索引（index）**；
- 支持筛选、合并、聚合等灵活操作，是数据分析的"瑞士军刀"。

类比理解：

| 表格要素 | 对应概念 | 示例 |
|---|---|---|
| 列 | 变量 | 姓名、年龄、账户 |
| 行 | 观测值 | 每个人的记录 |
| 行索引 | 每行的唯一标识 | 默认 `0, 1, 2...`，可自定义 |
| 列名 | 每列的标识 | `df['account']` 中的 `'account'` |

## 2. 创建 DataFrame 的常见方式

```python
import pandas as pd

# 方法1：从字典创建（键 = 列名，值 = 列数据）
data = {
    'account': ['A1', 'B2', 'C3'],
    'balance': [1000, 2000, 1500]
}
df = pd.DataFrame(data)

# 方法2：从 CSV 文件读取
df = pd.read_csv('data.csv')

# 方法3：手动指定数据、列名和行索引
df = pd.DataFrame(
    data=[[1, 'Alice'], [2, 'Bob']],
    columns=['ID', 'Name'],
    index=['row1', 'row2']   # 自定义行索引
)
```

输出示例：

```text
  account  balance
0      A1     1000
1      B2     2000
2      C3     1500
```

## 3. 核心属性

| 属性 | 说明 | 示例输出（上例） |
|---|---|---|
| `df.shape` | 行数和列数的元组 `(rows, columns)` | `(3, 2)` |
| `df.columns` | 所有列名的 `Index` 对象 | `Index(['account', 'balance'], dtype='object')` |
| `df.index` | 行索引的 `Index` 对象（默认 `RangeIndex`） | `RangeIndex(start=0, stop=3, step=1)` |
| `df.dtypes` | 每列的数据类型 | `account object` / `balance int64` |
| `df.head()` | 查看前 5 行（默认） | 显示前 5 行数据 |

## 4. 访问数据

### 4.1 访问列

语法：`df['列名']` 或 `df.列名`（后者要求列名是合法变量名）；返回 `Series`（一维、带索引）。

```python
account_series = df['account']
print(account_series)
```

```text
0    A1
1    B2
2    C3
Name: account, dtype: object
```

注意：`account_series` 是 `Series`，其索引是 `0, 1, 2`（原 DataFrame 的行索引），值是 `['A1', 'B2', 'C3']`。

### 4.2 访问行：loc 与 iloc

- `loc`：按**行索引标签**访问（支持字符串、数字等标签）；
- `iloc`：按**位置序号**访问（从 0 开始的整数）。

```python
df.loc[0]    # 按标签访问第 0 行（所有列）
df.iloc[0]   # 按位置访问第 0 行
```

### 4.3 自定义行索引

```python
df = pd.DataFrame({'account': ['A1', 'B2']}, index=['user1', 'user2'])
print(df.index)          # Index(['user1', 'user2'], dtype='object')
print(df.loc['user1'])   # 按标签 'user1' 访问行
```

## 5. 列名与行索引：为什么要区分

- **列名**：标识列。`df.columns` 查看所有列名；`df['列名']` 取该列（返回 `Series`）。
- **行索引**：标识行。`df.index` 查看所有行索引；`df.loc[索引值]` / `df.iloc[位置]` 取特定行。

关键区别：

- `df['account']` 是**取列**（`'account'` 是列名）；
- `df.index` 是**行的标识符**（与列名无关）；
- `mapping.index` 中的 `index` 是**行索引**——`mapping` 若是 Series 或 DataFrame，其索引就是行标识。

## 6. 案例：为什么 `df['account'].isin(mapping.index)` 能工作

```python
mapping = pd.Series([100, 200], index=['A1', 'B2'])   # mapping.index = ['A1', 'B2']

mask = df['account'].isin(mapping.index)   # 布尔 Series：[True, True, False]
count = mask.sum()                          # 统计匹配数量
```

分步理解：

| 部分 | 含义 |
|---|---|
| `df['account']` | 取列，返回 `Series`（值如 `['A1', 'B2', ...]`） |
| `mapping.index` | 若 `mapping` 是 Series/DataFrame，则为其**行索引**（如 `['A1', 'B2']`） |
| `.isin(...)` | 逐个检查 `account` 值是否在 `mapping.index` 中，返回布尔 `Series` |
| `.sum()` | 统计 `True` 的数量（即匹配的账户数） |

为什么不能直接用字典？若 `mapping` 是普通字典（`{'A1': 100, 'B2': 200}`），`mapping.index` 会报错——字典没有 `index` 属性。替代写法：`mapping.keys()` 或 `pd.Series(mapping).index`。

## 7. 常见操作速查

| 操作 | 代码示例 | 说明 |
|---|---|---|
| 添加新列 | `df['new_col'] = [1, 2, 3]` | 直接赋值 |
| 删除列 | `df.drop('balance', axis=1)` | `axis=1` 表示按列删除 |
| 筛选数据 | `df[df['balance'] > 1500]` | 选出 balance > 1500 的行 |
| 重命名列 | `df.rename(columns={'account': 'acc'})` | 修改列名 |
| 重置行索引 | `df.reset_index(drop=True)` | 丢弃原索引，生成新索引 |

## 总结

- DataFrame = 表格数据：列有**列名**，行有**行索引**。
- `df['列名']` 取列（返回 `Series`）；`df.index` / `df.loc[索引值]` 操作行。
- `mapping.index` 通常指 Pandas 对象（Series/DataFrame）的行索引。
- 记忆：看到 `df['列名']` 是在操作**列**；看到 `df.index` 或 `df.loc[索引值]` 是在操作**行**。

---

回到：[[cs/dev/python/index|Python 导航]]　下一篇：[[02-三剑客merge-concat-groupby]]
