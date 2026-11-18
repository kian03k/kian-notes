---
tags: [python, pandas, 性能]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# 案例：str.contains 向量化优化多模型匹配

## 1. 场景与原始写法

需求：从设备表中筛出"型号包含任一目标型号"的行，目标型号有 20 多个（B866、V271E、HN8145XR 等）。

```python
import pandas as pd

target_models = [
    'B866', 'B866-S2', 'B867', 'V271e-30', 'V271e-20', 'V271E',
    'V176', 'V175', 'V271-20', 'H8156XR', 'B866-S1', 'B866-L1',
    'V173-30', 'V173-20', 'V173', 'HN8145XR', 'V176-20', 'V152',
    'V173-50', 'G7611V2', 'G7615AV5', 'G7611'
]

def contains_target_model(value, target_models):
    """检查值是否包含任何目标模型"""
    if pd.isna(value):
        return False
    value_str = str(value).upper()
    return any(model.upper() in value_str for model in target_models)

mask = (
    df['router_model'].astype(str).apply(lambda x: contains_target_model(x, target_models)) |
    df['onu_model'].astype(str).apply(lambda x: contains_target_model(x, target_models))
)
filtered_df = df[~mask].copy()
```

> 注：原稿把函数和 `target_models` 定义写在了调用之后，按顺序执行会 NameError，此处已调整为可运行顺序。

## 2. 为什么 .apply(lambda) 慢

| 问题 | 说明 |
|---|---|
| 逐行处理 | `.apply()` 逐行执行，相当于 Python for 循环，每行调用一次函数 |
| 解释器开销 | 每次调用都有函数调用栈、变量查找、内层循环开销 |
| 无法向量化 | Pandas 底层是 C 实现，`.apply()` 会跳出向量化引擎，回到慢速 Python 层 |
| 内存不连续 | 逐行处理无法利用 CPU 缓存与 SIMD 指令 |

10 万行数据慢 10~100 倍；百万行以上可能从几秒变成几分钟。此处最坏还要对每行做 `len(target_models)` 次子串查找，复杂度 O(行数 × 模型数)。

## 3. 优化写法及其原理

```python
pattern = '|'.join(target_models)   # 'B866|B866-S2|V271e-30|...'

mask = (
    df['router_model'].astype(str).str.contains(pattern, na=False, case=False) |
    df['onu_model'].astype(str).str.contains(pattern, na=False, case=False)
)
```

快的四个原因：

1. **向量化**：`str.contains()` 是 Pandas 内置的 C 实现函数，底层用正则引擎一次性处理整个 Series——"一次扫描，全部匹配"，充分利用 CPU 缓存与 SIMD 指令，而不是一行一行调用 Python 函数。
2. **正则 `|` 实现"任一匹配"**：`'B866|B866-S2|V271e-30'` 是一个正则表达式，含义是"包含 B866 或 B866-S2 或 V271e-30……"。单次扫描即可判断是否含任意一个目标子串，替代 Python 层的 `for model in target_models` 循环。
3. **避免重复计算**：`.apply()` 版本每行要做 O(m) 次 `in` 判断（m=模型数）；优化后整列只扫描一遍。Pandas 的 `str.contains` 底层是 Python `re` 模块，对 `|` 多分支模式有内部优化，远快于逐个 `in`。
4. **`astype(str)` 与 `na=False` 兜底**：不加 `astype(str)` 时，列中若有数字（如 `123`），`str.contains()` 会报错；不加 `na=False` 时，NaN 会让 mask 也是 NaN，后续 `df[mask]` 会出错或丢数据。`case=False` 则向量化地忽略大小写，省去手动 `.str.lower()`。

## 4. 性能对比（100 万行 × 50 个型号，估算）

| 方法 | 时间 | 原理 |
|---|---|---|
| `.apply(lambda ...)`：每行对每个型号做 `in` 查找 | ~150 秒 | Python 循环，约 5000 万次 `in` 操作 |
| `str.contains(pattern)` 两列结果按位或 | ~0.8 秒 | C 层正则引擎，每列单次扫描 |

提速约 180 倍。

## 5. 为什么不要按型号循环调用 str.contains

```python
# 低效：每个型号扫描两列，50 个型号 = 100 次全列扫描
mask = pd.Series(False, index=df.index)
for model in target_models:
    mask |= df['router_model'].str.contains(model, na=False, case=False) | \
            df['onu_model'].str.contains(model, na=False, case=False)
```

虽然每个 `str.contains` 本身是向量化的，但循环让它执行 100 次。正确做法是**先 `'|'.join` 拼成一个正则，只扫描两列、做一次 OR**。

## 6. 注意事项与生产级写法

| 问题 | 建议 |
|---|---|
| 型号含正则元字符（`.` `*` `+` `?` `(` `)` `[` `]` 等）会导致语法错误或误匹配 | 用 `re.escape()` 包装每个型号 |
| 型号数千个时 pattern 超长（>10KB），正则效率下降 | 分批处理，或评估其他匹配方案 |
| 大数据内存压力：`str.contains()` 会生成中间布尔 Series | 分块处理（如 `df.iloc[i:i+100000]`） |
| 子串 vs 完整词：`'B866'` 会匹配 `'XB866X'` | 只想匹配完整型号时，在拼好的 pattern 外层套一层 `\b(?:...)\b` 词边界 |

生产级安全写法：

```python
import re

pattern = '|'.join(re.escape(model) for model in target_models)  # 转义特殊字符
mask = (
    df['router_model'].astype(str).str.contains(pattern, na=False, case=False) |
    df['onu_model'].astype(str).str.contains(pattern, na=False, case=False)
)
```

## 7. 超大数据量（>1000 万行）的进一步选择

- **Dask / Modin**：Pandas API 的并行化替代；
- **Polars**（Rust 实现，通常比 Pandas 快 5~10 倍）：

```python
import polars as pl

pattern = '|'.join(re.escape(m) for m in target_models)
df_pl = pl.DataFrame(df)
mask = (
    df_pl['router_model'].str.contains(pattern, case_sensitive=False) |
    df_pl['onu_model'].str.contains(pattern, case_sensitive=False)
)
```

## 8. 总结

| 维度 | `.apply()` | `str.contains()` |
|---|---|---|
| 执行方式 | Python 循环（逐行） | C 向量化（批量） |
| 复杂度 | O(行数 × 模型数) | O(行数)（单列单次扫描） |
| 性能 | 秒级 → 分钟级 | 毫秒 ~ 秒级 |
| 内存效率 | 低（频繁函数调用） | 高（连续内存操作） |
| 可读性/可维护性 | 复杂 | 简洁 |
| 数据规模上限 | 10 万行就明显卡顿 | 百万行依然流畅 |

**多模式子串匹配的黄金写法**：`'|'.join(re.escape(...))` 拼一个 pattern → `str.contains(na=False, case=False)` → 两列结果用 `|` 合并。

> 相关：逐行遍历的性能对比见 [[03-逐行遍历itertuples]]；正则 `Match` 对象的用法见 [[03-正则匹配对象]]。

---

上一篇：[[05-NaN与np-pd关系]]　回到：[[cs/dev/python/index|Python 导航]]
