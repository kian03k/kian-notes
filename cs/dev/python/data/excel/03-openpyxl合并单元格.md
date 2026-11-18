---
tags: [python, 踩坑]
created: 2026-11-15
updated: 2026-11-15
status: ok
---

# openpyxl 合并单元格的数据归属

## 结论

**openpyxl 的 `merge_cells()` 会自动清空合并区域内的非左上角单元格，不会出现"取消合并后数据复活"。**

原稿描述的异常在 openpyxl 3.1.5 上无法复现。真正的风险是另一个：**先合并、再向非左上角单元格写入会抛异常**。

## 实测验证

环境：Python 3.13 + openpyxl 3.1.5，Windows。

```python
import openpyxl
wb = openpyxl.Workbook(); ws = wb.active
ws["A1"], ws["A2"], ws["A3"] = "苹果", "香蕉", "橙子"
ws.merge_cells("A1:A3")
```

| 检查项 | 结果 |
|---|---|
| 合并后内存态 `ws["A2"].value` / `ws["A3"].value` | `None` / `None` |
| 合并后 `ws["A2"]` 的单元格类型 | `MergedCell` |
| 保存后重新加载，A2 / A3 | `None` / `None` |
| 保存后的 XML | `<row r="2"></row>` — 连 `<c r="A2">` 标签都不存在 |

原因：`merge_cells()` 内部调用 `_clean_merge_range()`，把主单元格之外的单元格整体替换为空的 `MergedCell` 实例，因此值在合并那一刻就被丢弃了，字节层面也没有残留。

## 原稿的错误

原稿称"库只添加 `<mergeCells>` 标签、未删除其他单元格的 `<c>` 标签"。这个描述对 openpyxl 不成立。

该现象仍可能出现在其他写入路径上——Apache POI 的 `addMergedRegion` 只写合并标记、不处理子单元格数据（社区长期反馈，本次未实测），直接手改 OOXML 也一样。若观察到"数据复活"，应先确认写入方是哪个库，而不是默认归因于 Excel。

## 真正的坑：先合并后写入

合并之后，非左上角单元格已变成只读的 `MergedCell`：

```
>>> ws.merge_cells("A1:A3")
>>> ws["A2"] = "x"
AttributeError: 'MergedCell' object attribute 'value' is read-only
```

`ws.cell(row=2, column=1).value = "y"` 得到同样的异常。

所以写入顺序只有一种正确写法：**先写满区域，再合并**。合并前不需要手工置 `None`，`merge_cells()` 会替你清掉。

## 跨列居中不要用 centerAcrossSelection

原稿推荐的 `Alignment(horizontal='centerAcrossSelection')` 在 openpyxl 中直接抛异常：

```
ValueError: Value must be one of {'general','left','center','right','fill','justify','centerContinuous','distributed'}
```

Excel 界面上的 "Center Across Selection" 在 OOXML 里对应的值是 `centerContinuous`：

```python
from openpyxl.styles import Alignment

ws["A1"] = "苹果"
ws["A1"].alignment = Alignment(horizontal="centerContinuous")
```

这是用样式替代物理合并的常用手法——不产生合并区域，自然没有合并单元格带来的排序、筛选、复制粘贴与后续数据处理问题。代价是仅对横向有效，纵向居中没有对应特性。

> 修正：原稿写作 `horizontal='centerAcrossSelection'`，openpyxl 不支持该取值，实测抛 `ValueError`。正确取值为 `centerContinuous`。

## 检查外部文件是否残留

`merge_cells()` 不会留下脏数据，但别人给的 xlsx 未必由 openpyxl 生成。需要排查时可直接看底层的单元格值：

```python
from openpyxl import load_workbook

def find_merge_residuals(path):
    wb = load_workbook(path)
    issues = []
    for ws in wb.worksheets:
        for rng in ws.merged_cells.ranges:
            for row in range(rng.min_row, rng.max_row + 1):
                for col in range(rng.min_col, rng.max_col + 1):
                    if row == rng.min_row and col == rng.min_col:
                        continue
                    cell = ws.cell(row=row, column=col)
                    if isinstance(cell, openpyxl.cell.cell.MergedCell):
                        continue
                    if cell.value is not None:
                        issues.append(f"{ws.title}!{cell.coordinate} 位于 {rng} 内仍有值: {cell.value!r}")
    return issues
```

判定依据：合并区域内除左上角外，不应存在带值的普通单元格。清洗方式是在合并前把这些单元格置空。

## 相关

- [[01-Excel读写]]：openpyxl / pandas 的选型与基础读写
- 结构说明：`.xlsx` 本质是 ZIP 包，工作表数据在 `xl/worksheets/sheetN.xml`，合并关系记于 `<mergeCells>`，单元格值记于 `<c r="坐标">`。排查底层问题时改后缀为 `.zip` 解压即可。

---

上一篇：[[02-CSV读写]]　回到：[[cs/dev/python/index|Python 导航]]
