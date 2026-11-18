---
tags: [python, pandas, excel]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# Excel 多 Sheet 读写

## 1. 中间数据格式：直接用 DataFrame

从 Excel 读取的数据本身就是 `pd.DataFrame`，转填、清洗、合并的中间数据也应保持 DataFrame 格式：

- 保留列名、索引、数据类型等结构信息，后续处理与写回都简单；
- 若中间用 list/dict，会丢失结构信息，写入 Excel 时要手动重建表格，复杂且易错；
- `to_excel()` 直接接受 DataFrame 作为输入，无需转换。

```python
import pandas as pd

# 读取
df1 = pd.read_excel('input.xlsx', sheet_name='Sheet1')
df2 = pd.read_excel('input.xlsx', sheet_name='Sheet2')

# 中间处理（清洗、计算、合并）——全部在 DataFrame 上操作
df1['新列'] = df1['原列'] * 2
df_merged = pd.concat([df1, df2], ignore_index=True)
```

> 除非数据量极小或有特殊格式需求，不要用 list/dict 做中间格式；即使那样，也建议最后转成 DataFrame 再写入。

## 2. 多 Sheet 一次性写入：pd.ExcelWriter

推荐用 `pd.ExcelWriter` 一次写多个 Sheet：

- 效率高：只打开/关闭一次文件，避免多次 I/O；
- 代码简洁：一个上下文管理器搞定所有 Sheet；
- 避免文件被占用/冲突：分别写入可能因文件未关闭导致写入失败；
- Pandas 官方推荐做法。

```python
# 读取多个 sheet
df_sheet1 = pd.read_excel('input.xlsx', sheet_name='Sheet1')
df_sheet2 = pd.read_excel('input.xlsx', sheet_name='Sheet2')

# 一块写入多个 sheet
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    df_sheet1.to_excel(writer, sheet_name='Sheet1_处理后', index=False)
    df_sheet2.to_excel(writer, sheet_name='Sheet2_原始', index=False)
    # 可继续添加更多 sheet
    pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_excel(writer, sheet_name='新表', index=False)
```

### 为什么不要分别写入

```python
df_sheet1.to_excel('output.xlsx', sheet_name='Sheet1')  # 第一次写
df_sheet2.to_excel('output.xlsx', sheet_name='Sheet2')  # 第二次写 → 覆盖整个文件！
```

默认情况下，直接对文件路径调用 `to_excel()` 会**覆盖整个文件**——第二次写入会丢掉第一个 Sheet 的成果，或直接报错。要写多个 Sheet 必须经 `ExcelWriter`。

## 3. 保留原文件所有 Sheet，只修改部分

先读取所有 Sheet（`sheet_name=None` 返回 dict），处理需要修改的，再统一写回：

```python
# 读取所有 sheet，返回 {sheet名: DataFrame}
all_sheets = pd.read_excel('input.xlsx', sheet_name=None)

# 只处理需要修改的 sheet
all_sheets['Sheet1'] = all_sheets['Sheet1'].assign(新列=lambda x: x['A'] * 2)

# 一次性写回所有 sheet
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    for sheet_name, df in all_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
```

这样既保留原始结构，又只修改了需要的部分。

## 4. 最佳实践速查

| 项目 | 推荐做法 |
|---|---|
| 中间数据格式 | `pandas.DataFrame`（保留结构、类型、列名） |
| 多 Sheet 写入方式 | `pd.ExcelWriter` 一次性写入 |
| 写入引擎 | `engine='openpyxl'`（支持 .xlsx，功能完整） |
| 是否保留索引 | 一般设 `index=False`，除非确实需要行索引 |

## 5. 扩展

需要格式化单元格、设置列宽、添加图表时，可在 `openpyxl` / `xlsxwriter` 引擎下进一步扩展；基础流程始终是：**DataFrame → ExcelWriter 一次性写入**。

> 相关：单元格级操作（合并单元格、样式）见 Python `data/` 下的 openpyxl 笔记。

---

上一篇：[[03-逐行遍历itertuples]]　下一篇：[[05-NaN与np-pd关系]]
