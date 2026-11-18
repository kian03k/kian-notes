---
tags: [python, excel]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# Excel 读写（openpyxl / pandas 分工）

> **适用场景**：读分算总分写回、按列对号入座补数据、单元格级格式调整。
> **一句话选型**：单元格级精细操作 → openpyxl；统计清洗排序 → pandas。

## 1. 选型表

| 库 | 格式 | 定位 |
|---|---|---|
| xlrd / xlwt / xlutils | `.xls` 旧格式 | 遗留代码，**别新写**（新版 xlrd 已不支持 .xlsx） |
| **openpyxl** | `.xlsx` | 单元格级精细操作、格式、行列遍历 |
| **pandas** | `.xlsx` / `.csv` 通吃 | 统计分析首选，一行顶十行 |

> `.xls` 走 xlrd、`.xlsx` 走 openpyxl，引擎不同别混。

## 2. 方案：openpyxl 读 → 算 → 写

```python
import openpyxl

# 读（read_only 大表省内存；values_only 直接拿值不要 cell 对象）
wb = openpyxl.load_workbook("performance.xlsx", read_only=True)
ws = wb["performance"]
for row in ws.iter_rows(min_row=2, values_only=True):
    name, kt, sy, qm, _t, t = row
    print(name, round(kt * 0.1 + sy * 0.3 + qm * 0.6))

# 写
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["姓名", "综合成绩"])
ws.append(["张三", 88])
wb.save("out.xlsx")
```

## 3. 方案：pandas 一行搞定统计与写回

```python
import pandas as pd

df = pd.read_excel("performance.xlsx", sheet_name="performance")
df["综合"] = (df["课堂"] * 0.1 + df["实验"] * 0.3 + df["期末"] * 0.6).round()
df.sort_values("综合", ascending=False).to_excel("sorted.xlsx", index=False)
```

> `index=False` 很关键：不写左侧行号，否则下次读回来会多一列 `Unnamed: 0`。

## 4. 方案：两张表按某列"对号入座"

**场景**：表 A 有「准考证号」，表 B 有「考生号 + 学号」，要把学号按号段补回 A。

```python
import pandas as pd

total = pd.read_excel("总名单.xlsx")       # 大表：考生号 → 学号
sub   = pd.read_excel("我的名单.xls")      # 小表：准考证号

# 把"考生号 → 学号"做成字典再映射（比逐个查找快得多）
m = dict(zip(total["考生号"], total["学号"]))
sub["学号"] = sub["准考证号"].map(m)       # 匹配不上的自动是 NaN
# 想给个默认值：  .map(m).fillna(0)

sub.to_excel("处理后.xlsx", index=False)
```

> **关键**：用字典映射，别在循环里 `list(...).index(x)` —— 后者每次从头线性扫描（O(n)），几千行就明显变卡；字典是 O(1)。

## 5. 陷阱清单

| 坑 | 后果 | 对策 |
|---|---|---|
| 用 xlrd 读 .xlsx | 新版直接报错 | 换 openpyxl / pandas |
| `to_excel` 不写 `index=False` | 多出一列行号 | 显式指定 |
| 循环里 `list.index()` 找值 | O(n²)，几千行就卡 | 先建字典再 `.map()` |
| 多 Sheet 分别 `to_excel` | 后写的**覆盖整个文件** | 用 `pd.ExcelWriter` 一次写 |
| 大表整表载入内存 | 内存爆 | openpyxl 加 `read_only=True` |

> 多 Sheet 写入的完整方案见 [[cs/dev/python/data/pandas/04-Excel多Sheet读写|pandas/04-Excel多Sheet读写]]；
> 合并单元格、跨列居中等格式操作见 [[03-openpyxl合并单元格]]。

---

回到：[[cs/dev/python/index|Python 导航]]　下一篇：[[02-CSV读写]]
