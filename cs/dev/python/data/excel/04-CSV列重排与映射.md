---
tags: [python, 脚本, csv]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# CSV 列重排与值映射

> **适用场景**：数据集预处理——把列序换成模型要求的顺序、把 `1/0` 标签改成 `正面/负面`。
> 用标准库 `csv`，不依赖 pandas，几百万行也能流式跑。

## 1. 方案：小文件（全读进内存）

```python
import csv

with open("in.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

for row in rows:                       # 交换前两列
    row[0], row[1] = row[1], row[0]

for row in rows:                       # 标签 1/0 -> 正面/负面
    row[1] = {"1": "正面", "0": "负面"}.get(row[1], row[1])

with open("out.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
```

## 2. 方案：大文件（流式，不占内存）

```python
import csv

LABEL = {"1": "正面", "0": "负面"}

with open("in.csv", newline="", encoding="utf-8") as fin, \
     open("out.csv", "w", newline="", encoding="utf-8") as fout:
    reader, writer = csv.reader(fin), csv.writer(fout)
    writer.writerow(next(reader))                 # 表头原样写出
    for row in reader:
        if len(row) < 2:
            continue                              # 跳过残缺行
        row[0], row[1] = row[1], row[0]
        row[1] = LABEL.get(row[1], row[1])
        writer.writerow(row)
```

## 3. 陷阱清单

| 坑 | 后果 | 对策 |
|---|---|---|
| `open(..., newline="")` 漏写 | Windows 下每行之间多空行 | 读写两侧都要加 |
| 大文件 `list(reader)` | 内存爆 | 逐行流式处理 |
| 编码猜错 | 中文乱码 / `UnicodeDecodeError` | 依次试 `utf-8`、`utf-8-sig`、`gbk` |
| 直接按下标改列 | 源列序和假设不符，静默改错列 | 先用表头名找下标，再改 |
| 用 `split(",")` | 字段内含逗号/引号直接崩 | 老实用 `csv` 模块 |

按表头定位列（更稳）：

```python
with open("in.csv", newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader)
    i_label = header.index("label")          # 按名字找，不写死下标
```

---

回到：[[cs/dev/python/index|Python 导航]]
