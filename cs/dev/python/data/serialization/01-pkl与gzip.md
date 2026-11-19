---
tags: [python, 数据, 序列化]
created: 2026-11-19
updated: 2026-11-19
status: ok
---

# pkl 与 pkl.gz：序列化、压缩与安全

> **适用场景**：读别人（或自己以前）存下的 `.pkl` / `.pkl.gz` 数据文件；写一个能自动识别压不压缩的加载函数；排查「解压了但 `pickle.load` 还是报错」。
> 核心：`.pkl.gz` 只是「pickle 字节流 + gzip 压缩」，解压是中间步骤，目标是重建 Python 对象。

## 1. 本质：先解压（如果有），再反序列化

`.pkl.gz` 内部是 **gzip 头 + 压缩后的 pickle 字节流**，不是文本、不可直接看。

```txt
data.pkl.gz  =  gzip header  +  gzip(pickle bytes)
```

`gzip.open(path, "rb")` 返回的**已经是一个自动解压的文件对象**，不需要手动调任何解压函数——它内部做完了解压。所以下面两句等价：

```python
import gzip, pickle

with gzip.open("data.pkl.gz", "rb") as f:
    data = pickle.load(f)          # 推荐：流式，不整块读进内存

with gzip.open("data.pkl.gz", "rb") as f:
    data = pickle.loads(f.read())  # 也行：先解压成 bytes 再 loads
```

## 2. 方案：自动识别压缩状态的加载函数

```python
import gzip
import pickle
from pathlib import Path

def load_data(directory, filename, compressed=None):
    """读取 .pkl(.gz)。compressed=None 时先找 .pkl.gz，再找 .pkl。"""
    base = Path(directory) / filename

    if compressed is None:
        gz, plain = base.with_suffix(".pkl.gz"), base.with_suffix(".pkl")
        if gz.exists():
            path, compressed = gz, True
        elif plain.exists():
            path, compressed = plain, False
        else:
            raise FileNotFoundError(f"{base} 不存在（.pkl / .pkl.gz 都没有）")
    else:
        path = Path(f"{base}.pkl.gz" if compressed else f"{base}.pkl")

    opener = gzip.open if compressed else open
    with opener(path, "rb") as f:
        return pickle.load(f)
```

要点：

- 用 `Path.with_suffix()` 拼扩展名，别用字符串 `+`（`report.v2` 这类多点的名字会拼错）；
- 两种情况的打开模式都是 `"rb"`，不要写 `"rb" if compressed else "rb"` 这种两分支相同的判断；
- 打开器用变量切换（`opener = gzip.open if compressed else open`），比在两个分支里各写一遍 `with` 干净；
- 异常别一概吞掉返回 `None`。`FileNotFoundError`（找不到）、`pickle.UnpicklingError` / `EOFError`（文件损坏或没解压就交给 pickle）、`gzip.BadGzipFile`（扩展名是 `.gz` 但内容不是）要能区分，否则出问题只会看到 `None`，不知道是哪种。

## 3. 方案：手动解压的三种方式

```bash
# 1. 命令行：data.pkl.gz 消失，生成 data.pkl
gunzip data.pkl.gz        # 等价 gzip -d data.pkl.gz
```

```python
# 2. 代码里解压（不落中间文件）
import gzip, pickle
with gzip.open("data.pkl.gz", "rb") as f:
    data = pickle.load(f)
```

```bash
# 3. 只看不拆
gzip -l data.pkl.gz       # 压缩前后大小、压缩率
xxd -l 32 data.pkl       # 看魔数（注意：是解压后的 .pkl）
```

pickle 的二进制协议以 `\x80\x04`（协议 4）这类魔数开头。**必须先解压才能看到**——直接 `xxd` 一个 `.gz` 只会看到 `1f 8b`（gzip 魔数）。

## 4. 方案：验证能不能正常读

```python
import gzip, pickle

data = {"test": 123, "list": [1, 2, 3]}
with open("test.pkl", "wb") as f:
    pickle.dump(data, f)

with open("test.pkl", "rb") as fin, gzip.open("test.pkl.gz", "wb") as fout:
    fout.write(fin.read())

print(load_data(".", "test"))   # 自动命中 test.pkl.gz
```

## 5. 陷阱清单

| 陷阱 | 后果 | 正解 |
|---|---|---|
| **加载不可信来源的 pkl** | **pickle 反序列化会执行任意代码**，恶意文件可直接拿到你的权限 | 只读自己或可信方生成的文件；跨系统传数据用 JSON / CSV / Parquet |
| 对 `.pkl.gz` 直接 `pickle.load(open(..., "rb"))` | 读到的是 gzip 头，报 `UnpicklingError` | 先过 `gzip.open` |
| 对普通 `.pkl` 用 `gzip.open` | `BadGzipFile: Not a gzipped file` | 先判断扩展名或魔数 |
| `mode = "rb" if compressed else "rb"` | 冗余判断，掩盖了「两种格式都用二进制模式」这个事实 | 直接 `"rb"` |
| 异常一律 `return None` | 找不到文件和文件损坏分不清，排查靠猜 | 分类型 catch 并带路径信息 |
| 用字符串 `+ ".pkl.gz"` 拼名 | 名字含多点（`report.v2`）或已带后缀时拼错 | `Path.with_suffix()` |
| 把解压后的中间文件留在原地 | 磁盘翻倍，且下次自动检测先命中哪个不确定 | `gzip.open` 流式读，不落中间文件 |
| pickle 跨 Python 版本 / 跨库 | 类定义变了就读不出来（`AttributeError: module ... has no attribute ...`） | 存 dict / 基础类型，别 pickle 自定义类实例 |

## 6. 速查

| 问题 | 答案 |
|---|---|
| 解压的本质 | 把 gzip 压缩数据还原成原始 pickle 字节流 |
| 要手动解压吗 | 不用，`gzip.open` / `gzip.decompress` 都行，前者更省内存 |
| 怎么判断是不是有效 pickle | 解压后看开头是否 `\x80\x04` 一类协议魔数 |
| 为什么不直接 `gzip.decompress()` | `gzip.open` 返回文件对象，`pickle.load` 可直接流式读，不用整块进内存 |
| 能存自定义类实例吗 | 能，但换版本/改类定义后读不回来，长期存档不要这么干 |
| 有安全风险吗 | **有**。pickle 不是数据格式，是可执行指令流，不可信来源一律拒绝 |

---

回到：[[cs/dev/python/index|Python 导航]]

> 相关：日志里的异常堆栈记录见 [[04-特殊场景手册]]，数据表格的通用读写见 [[02-CSV读写]]。
