---
tags: [python, pandas]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# 三大核心操作：merge / concat / groupby

`merge`、`concat`、`groupby` 是 Pandas 数据处理的"三剑客"，覆盖数据清洗、ETL、分析、报表全流程。

一句话口诀：**merge 拼列，concat 拼行，groupby 汇总**。

## 1. merge：数据库式 JOIN（横向合并，列扩展）

将两个 DataFrame 按列（键）对齐合并，类似 SQL 的 `JOIN`：增加列数，行数可能变化。

```python
df1.merge(df2,
          on='key',              # 公共列名（等值连接）
          left_on='L_key',       # 左表键（两表键名不同时用）
          right_on='R_key',      # 右表键
          how='inner',           # 连接类型：inner / left / right / outer
          suffixes=('_x', '_y')  # 重名列后缀
)
```

### 1.1 四种连接方式对比

| `how` | 说明 | 行数变化 | 适用场景 |
|---|---|---|---|
| `'inner'` | 只保留两表都有的键 | 减少 | 交集：如"有订单的客户" |
| `'left'` | 保留左表所有行，右表无匹配补 NaN | 不变或增加 | 主表保留：如"所有客户，有订单的标出来" |
| `'right'` | 保留右表所有行 | 可能增加 | 右表为主 |
| `'outer'` | 保留所有键，无匹配补 NaN | 增加 | 并集：如"所有客户 + 所有订单" |

### 1.2 示例

```python
df1 = pd.DataFrame({'id': [1, 2, 3], 'name': ['A', 'B', 'C']})
df2 = pd.DataFrame({'id': [2, 3, 4], 'city': ['SH', 'BJ', 'SZ']})

result = df1.merge(df2, on='id', how='left')
```

| id | name | city |
|---|---|---|
| 1 | A | NaN |
| 2 | B | SH |
| 3 | C | BJ |

- `id=4` 不在左表 → 不出现；
- `id=1` 不在右表 → city 为 NaN。

### 1.3 常见陷阱

| 问题 | 解决方案 |
|---|---|
| 重名列自动加后缀，含义不清 | 显式指定 `suffixes=('_left', '_right')` |
| 两表键列名不同 | 用 `left_on`、`right_on` |
| 多对多连接行数爆炸 | 先去重 `drop_duplicates()` |
| 字符串键 vs 数字键连不上 | 统一类型：`df['id'] = df['id'].astype(str)` |

### 1.4 安全合并模板

```python
df_final = (
    df_main
    .merge(df_extra, on='user_id', how='left', suffixes=('', '_extra'))
    .fillna({'status_extra': 'unknown'})
)
```

## 2. concat：堆叠拼接（行/列扩展）

沿轴（axis）堆叠多个 DataFrame，类似 Excel 的"粘贴行"或"粘贴列"。

```python
pd.concat([df1, df2, df3],
          axis=0,              # 0=纵向（加行），1=横向（加列）
          ignore_index=False,  # 是否重置索引
          join='outer',        # 'outer'=保留所有列，'inner'=只留公共列
          keys=['A', 'B', 'C'] # 给每个 DataFrame 加一级索引
)
```

### 2.1 纵向拼接 axis=0（最常用）

```python
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

result = pd.concat([df1, df2], axis=0, ignore_index=True)
```

适用于多个文件/批次数据合并（如每月销售数据拼成全年）。

### 2.2 横向拼接 axis=1

```python
df1 = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
df2 = pd.DataFrame({'age': [20, 25], 'city': ['SH', 'BJ']})

result = pd.concat([df1, df2], axis=1)
```

注意：横向拼接**索引必须对齐**，否则会补 NaN。

### 2.3 多表带标签拼接（keys）

```python
monthly_data = pd.concat(
    [jan, feb, mar],
    keys=['Jan', 'Feb', 'Mar'],
    names=['Month', 'OriginalIndex']
)
```

结果变成 MultiIndex，适合按时间/类别分组分析，后续用 `.xs('Jan')` 提取子集。

### 2.4 常见陷阱

| 问题 | 解决方案 |
|---|---|
| 列名不一致 | `join='outer'` 保留所有列，缺失补 NaN |
| 索引重复 | `ignore_index=True` 重置为 0,1,2... |
| 大数据内存压力 | `pd.concat(..., copy=False)` 减少复制 |
| 拼接后索引混乱 | `reset_index(drop=True)` 清理 |

### 2.5 多文件合并模板

```python
import glob

files = glob.glob("data/*.csv")
dfs = [pd.read_csv(f) for f in files]
full_df = pd.concat(dfs, ignore_index=True)
```

## 3. groupby：分组聚合（行压缩）

将数据按一个或多个列分组，对每组做聚合、转换、过滤：减少行数，生成统计结果。

```python
grouped = df.groupby('col1')                     # 返回 GroupBy 对象
result = grouped.agg({'col2': 'mean', 'col3': 'sum'})
```

### 3.1 常用聚合函数

| 函数 | 作用 |
|---|---|
| `'sum'` / `'mean'` / `'count'` / `'size'` | 基础统计 |
| `'min'` / `'max'` / `'first'` / `'last'` | 极值/取首尾 |
| `'nunique'` | 去重计数 |
| `lambda x: x.tolist()` | 自定义：合并为列表 |
| `lambda x: ', '.join(x)` | 自定义：合并为字符串 |

### 3.2 示例：按部门统计

```python
df = pd.DataFrame({
    'dept': ['A', 'A', 'B', 'B', 'B'],
    'salary': [5000, 6000, 7000, 8000, 9000],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
})

result = df.groupby('dept').agg({
    'salary': ['mean', 'max', 'count'],
    'name': lambda x: ', '.join(x)
})
```

结果为 MultiIndex 列（salary 下挂 mean/max/count），用 `result.columns = ['avg_salary', 'max_salary', 'emp_count', 'names']` 重命名后更清晰。

### 3.3 transform 与 agg 的区别

| 方法 | 作用 | 行数变化 | 用途 |
|---|---|---|---|
| `agg()` | 返回聚合结果（每组一行） | 减少 | 生成统计表 |
| `transform()` | 返回与原表等长的值（每行一个聚合值） | 不变 | 计算组内相对值 |

```python
df['avg_salary_by_dept'] = df.groupby('dept')['salary'].transform('mean')
```

用于计算"与组平均的差值"、"占比"、"排名"等。

### 3.4 apply：最灵活，但最慢

```python
def merge_group(group):
    return pd.Series({
        'employees': ', '.join(group['name']),
        'total_salary': group['salary'].sum(),
        'has_high_earner': group['salary'].max() > 8000
    })

result = df.groupby('dept').apply(merge_group)
```

适合无法用 agg/transform 表达的复杂逻辑（如把一个账户的多行记录合并成一行）。性能敏感时优先用 `agg()` / `transform()`。

### 3.5 常见陷阱

| 问题 | 解决方案 |
|---|---|
| NaN 分组默认被丢弃 | `groupby(..., dropna=False)` 保留 NaN 分组 |
| 想让分组列保留为普通列 | `groupby(..., as_index=False)` |
| 多列分组 | `groupby(['dept', 'region'])` |
| 想过滤组 | `groupby().filter(lambda x: len(x) > 2)` |

### 3.6 安全聚合模板（支持缺失值）

```python
result = (
    df
    .groupby('account', as_index=False)
    .agg({
        'onu_mfr': lambda x: ', '.join(x.dropna().astype(str).unique()),
        'onu_model': lambda x: ', '.join(x.dropna().astype(str).unique()),
        'count': 'size'
    })
)
```

## 4. 三大操作对比总结

| 操作 | 类比 | 行数变化 | 目的 | 适用场景 |
|---|---|---|---|---|
| `merge` | SQL JOIN | 可增可减 | **横向扩展**：补充信息 | 补充客户信息、关联订单 |
| `concat` | Excel 粘贴行/列 | 可增可减 | **纵向/横向拼接** | 合并多文件、多月数据 |
| `groupby` | 数据透视表 | 减少 | **纵向压缩**：统计汇总 | 按部门/地区/时间聚合 |

## 5. 场景选择指南

| 你的需求 | 推荐操作 |
|---|---|
| 把客户表和订单表按 ID 关联 | `merge` |
| 把 12 个月的销售数据拼成一张大表 | `concat` |
| 每个地区总销售额、平均单价 | `groupby(...).agg()` |
| 给每行打上它所在组的平均值 | `groupby().transform()` |
| 把一个账户的多台设备合并成一行 | `groupby().apply(...)` |
| 两表按不同列名连接 | `merge(left_on='A', right_on='B')` |
| 合并多个 CSV 文件 | `concat([pd.read_csv(f) for f in files], ignore_index=True)` |

## 6. 写代码前检查清单

| 检查点 | 做法 |
|---|---|
| 是否有重复列名 | 用 `suffixes=('_x', '_y')` 避免冲突 |
| 是否有缺失键 | `how='left'` 保留主表，避免丢数据 |
| 是否索引混乱 | `reset_index(drop=True)` 清理 |
| 是否需要保留原始索引 | `as_index=False` |
| 是否要合并列表/字符串 | `lambda x: ', '.join(x.dropna().unique())` |
| 是否性能慢 | 避免 `apply()`，优先 `agg()` / `transform()` |
| 是否要导出 JSON | 用 `json.dumps(list)` 或转 `str`，避免列表类型报错 |

## 7. 使用建议

1. 每次写代码前先问自己：**拼列？拼行？还是汇总？**
2. 遇到报错先看数据结构：`df.head()`、`df.dtypes`、`df.groupby('col').size()`。
3. 复杂聚合先用 `print(group.head())` 调试，确认组内数据形态，再写聚合函数。

> Pandas 的力量不在于"会用函数"，而在于"知道什么时候用哪个函数"。掌握这三大操作，就掌握了 80% 的 Pandas 实战。

---

上一篇：[[01-DataFrame创建基础]]　下一篇：[[03-逐行遍历itertuples]]
