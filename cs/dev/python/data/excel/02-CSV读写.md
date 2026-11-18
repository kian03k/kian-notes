---
tags: [python, csv]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# CSV 读写（标准库 csv）

> **适用场景**：不装 pandas 也要读写 CSV、逐行流式处理超大文件、只做简单的列重排/标签映射。
> **一句话**：小文件上 pandas 更省事；要流式、无依赖、细粒度控制就用标准库 `csv`。

## 1. 方案：读成字典列表（最常用）

```python
import csv

with open("StudentInfo.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [dict(r) for r in reader]         # [{'name':...,'email':...}, ...]
    print(reader.fieldnames)                 # 表头
```

为什么用 `DictReader`：按表头名取值 `r["email"]`，比 `r[3]` 抗列序变化。

## 2. 方案：写文件

```python
with open("out.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerows([["a", 1], ["b", 2]])
```

## 3. 方案：大文件流式处理

```python
with open("big.csv", newline="", encoding="utf-8") as fin, \
     open("out.csv", "w", newline="", encoding="utf-8") as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout)
    header = next(reader)                    # 先吃掉表头
    writer.writerow(header)
    for row in reader:                       # 一行一行过，不占内存
        writer.writerow(row)
```

## 4. 陷阱清单

| 坑 | 现象 | 对策 |
|---|---|---|
| 写文件忘了 `newline=""` | Windows 下每行之间多空行 | `open(..., newline="")` 必写 |
| 编码猜错 | 中文乱码 / `UnicodeDecodeError` | 依次试 `utf-8`、`utf-8-sig`（带 BOM）、`gbk` |
| `list(reader)` 读大文件 | 内存爆 | 改成逐行 for 循环 |
| 用 `split(",")` 代替 csv 模块 | 字段内有逗号/引号就崩 | 老实用 `csv.reader` |

> 中文 CSV 还有个高频来源：Excel 另存的 CSV 默认是 `gbk`（Windows 中文版），Linux/mac 上读会乱码。

---

上一篇：[[01-Excel读写]]　回到：[[cs/dev/python/index|Python 导航]]
