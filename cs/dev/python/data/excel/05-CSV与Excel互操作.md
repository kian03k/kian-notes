---
tags: [python, csv, excel]
created: 2026-11-19
updated: 2026-11-19
status: ok
---

# CSV 与 Excel 互操作：长数字与乱码

> **适用场景**：Python 导出的 CSV 交给别人，对方用 Excel 双击打开——长编号变成 `1.63E+09`、中文变成 `鏌ヨ鏉′欢`。
> 这是 Excel 打开 CSV 的两个默认行为（自动猜类型 + 按本地编码解析）导致的，两侧都要治。

## 1. 问题一：长数字变科学计数法

**现象**：`1376703203`、`221010422249` 这类编号，双击打开后显示成 `1.3767E+09`。

**原因**：Excel 打开 CSV 时会自己猜每列的数据类型，10 位以上的数字被当数值处理。

- 15 位以内：底层值没丢，只是显示成科学计数法，看起来像被截断了；
- **超过 15 位：精度真丢**（`221010422249` → `2.2101E+11`），这是 Excel 双精度浮点的上限，事后无法还原。

### 方案 A：用导入向导，把列指定为文本（最规范）

**不要双击打开 CSV。** 步骤：

1. Excel → 菜单「数据」→「从文本/CSV」；
2. 选中文件 → 导入；
3. 预览窗口里逐列点表头，把需要完整保留的列的类型设为**文本**；
4. 点「加载」。

| 列 | 示例值 | 设为 |
|---|---|---|
| 序号 | `1` | 整数 |
| 客户编号 | `100000000001` | ✅ 文本 |
| 时间戳 | `1762771483` | ✅ 文本 |
| 金额 | `1995.24` | 数字（保留小数） |

> 判据：凡是**超过 10 位的编号类数字**（订单号、ID、手机号、时间戳）一律设文本。

### 方案 B：导出时把长数字写成字符串 + 强制引号

如果对方只会双击，只能在生成端解决：让长数字字段变成**带引号的字符串**。

```python
import csv

LONG_COLS = {1, 4, 6}   # 需要保精度的列索引，从 0 开始

with open("in.csv", encoding="utf-8-sig", newline="") as fin, \
     open("out.csv", "w", encoding="utf-8-sig", newline="") as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)   # 非数字字段自动加引号
    for row in reader:
        writer.writerow([str(v) if i in LONG_COLS else v for i, v in enumerate(row)])
```

**关键点**：不要自己拼 `f'"{cell}"'`。那样 `csv.writer` 会认为值本身就含引号，按 RFC 4180 再转义一层，最终单元格内容变成 `"221010422249"`（引号成了字面字符）。正确做法是把值转成 `str`，让 `writer` 的 `QUOTE_NONNUMERIC` 决定加不加引号——字符串会被加引号，`int`/`float` 不加。

| 写法 | 结果 |
|---|---|
| `csv.writer(f)`（默认 `QUOTE_MINIMAL`） | 纯数字字符串不加引号 → Excel 仍转科学计数法 |
| `f'"{cell}"'` + 默认 writer | 多一层引号，单元格内容带引号字符 |
| **值转 `str` + `QUOTE_NONNUMERIC`** | ✅ 长数字加引号，Excel 识别为文本 |

### 已经打开且格式错了怎么办

选中有问题的列 → 菜单「数据」→「从表格/区域」→ 在 Power Query 里把该列数据类型改成**文本** → 「关闭并加载」。本质是重新导入一遍。

### 有效性对比

| 方法 | 原理 | 结论 |
|---|---|---|
| 导入时把列设为文本 | Excel 明确知道是文本 | ✅✅✅ 首选 |
| 导出时加引号 | Excel 把引号内容当文本 | ✅✅ 适合对方只能双击 |
| 手动改单元格格式 | 值已按数值解析，精度已丢 | ❌ 无效 |
| 双击打开后再改 | 同上 | ❌ 无效 |

## 2. 问题二：中文乱码

**原因**：文件是 UTF-8，Excel 双击时按系统本地编码（中文 Windows 是 GBK）解析，UTF-8 的中文字节被当 GBK 解释就成了 `鏌ヨ鏉′欢`。

### 方案 A：导出用 `utf-8-sig`

```python
with open("out.csv", "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f).writerows(rows)
```

`utf-8-sig` 在文件头写入 BOM，Windows 的 Excel 见到 BOM 就按 UTF-8 解析。

> 用普通 `utf-8`（无 BOM）保存，双击仍然乱码。这是最常见的一种「我明明存的是 UTF-8」。

### 方案 B：导入时指定编码

同问题一的导入向导：进入后把**文件原始格式**设为 `65001: Unicode (UTF-8)`，分隔符逗号，再把长数字列设文本，「关闭并加载」。一次导入同时解决乱码和科学计数法。

### 方案 C：`.txt` + 导入

数据存成 `.txt`（UTF-8），Excel 走「数据 → 从文本/CSV」导入并指定 UTF-8。最保险，但多一步手工。

## 3. 方案：导出模板（两个问题一次解决）

```python
import csv

rows = [
    ["序号", "客户编号", "合同号", "类型", "上行流量(kbyte)", "上行带宽(kbit/s)", "上行包数"],
    [1, "100000000001", "", "全部", 1762771483, 163219, 1995249028],
    [2, "100000000002", "", "全部", 1627506726, 150695, 1457129844],
]

with open("result.csv", "w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f, quoting=csv.QUOTE_NONNUMERIC).writerows(rows)
```

- `encoding="utf-8-sig"` → 双击不乱码；
- 长编号写成字符串 + `QUOTE_NONNUMERIC` → 双击不转科学计数法。

pandas 版本同理：

```python
df["客户编号"] = df["客户编号"].astype(str)
df.to_csv("result.csv", index=False, encoding="utf-8-sig")
```

> ⚠️ pandas 的 `to_csv` **没有**直接对应 `QUOTE_NONNUMERIC` 的开关，`quoting=csv.QUOTE_NONNUMERIC` 会把所有非数字列都加引号（通常无妨）。要精细控制就退回标准库 `csv` 逐行写。

## 4. 哪些字段必须设文本

| 字段 | 设文本 | 原因 |
|---|---|---|
| 身份证号 | ✅ | 18 位，超 15 位精度必丢 |
| 手机号 | ✅ | 11 位，显示 `1.37E+10` 很误导 |
| 订单号 / 流水号 | ✅ | 可能超 15 位，或有前导 0（`007` 会变 `7`） |
| 时间戳（秒） | ✅ | 10 位，显示成科学计数法 |
| 金额 | ❌ | 用数字格式保留小数 |
| 序号 | ❌ | 小整数无影响 |

## 5. 陷阱清单

| 陷阱 | 后果 | 正解 |
|---|---|---|
| 双击打开 CSV | 类型猜测 + 编码猜测同时发生，两坑齐现 | 走导入向导 |
| 用 `utf-8` 而非 `utf-8-sig` 导出 | Excel 双击乱码 | `encoding="utf-8-sig"` |
| 手动 `f'"{cell}"'` 加引号 | 单元格内容真的带引号 | 值转 `str` + `QUOTE_NONNUMERIC` |
| 把 `.txt` 改后缀成 `.csv` | 编码不变，照样乱码 + 科学计数法 | 用导入向导指定编码 |
| 15+ 位数字进 Excel 再导回 | 精度已丢，导回来是错的 | 从一开始就当文本处理，不经过数值 |
| 记事本「另存为 UTF-8」 | 无 BOM，Windows Excel 仍按 GBK | 存 `UTF-8 with BOM`，或干脆走导入 |

## 6. 速查

> 生成端：`encoding="utf-8-sig"` + 长编号存字符串 + `QUOTE_NONNUMERIC`。
> 接收端：别双击，走「数据 → 从文本/CSV」，编码选 65001，长编号列设文本。

---

回到：[[cs/dev/python/index|Python 导航]]

> 相关：Python 侧的 CSV 读取与流式处理见 [[02-CSV读写]]，列序与取值改写见 [[04-CSV列重排与映射]]，pandas 批量读写多 Sheet 见 [[04-Excel多Sheet读写]]。
