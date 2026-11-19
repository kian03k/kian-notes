---
tags: [python, 脚本, 路径]
created: 2026-11-19
updated: 2026-11-19
status: ok
---

# pathlib 速查：替代 os.path 的全部写法

> **适用场景**：写路径处理脚本时，手上是 `os.path` 的老写法需要翻译成 `pathlib`，或者反过来读旧代码；需要拼路径、取文件名、比较两个路径是否指同一个文件。
> 结论先说：**新代码一律用 `pathlib.Path`**，`os.path` 只需能读懂。

## 1. 方案：对照表（`os.path` → `pathlib`）

| 功能 | `os.path` 写法 | `pathlib` 写法 | 说明 |
|---|---|---|---|
| 拼接路径 | `os.path.join("a", "b", "c")` | `Path("a") / "b" / "c"` 或 `Path("a", "b", "c")` | `/` 操作符更直观 |
| 规范化路径 | `os.path.normpath("a/../b")` | `Path("a/../b").resolve()` | `resolve()` 既规范化又消 `..` 又解析符号链接 |
| 获取绝对路径 | `os.path.abspath("foo")` | `Path("foo").absolute()` / `.resolve()` | `resolve()` 还会解析符号链接 |
| 获取文件名 | `os.path.basename("/a/b/c.txt")` | `Path("/a/b/c.txt").name` | 属性访问 |
| 获取目录名 | `os.path.dirname("/a/b/c.txt")` | `Path("/a/b/c.txt").parent` | 返回 `Path`，可链式 `p.parent.parent` |
| 分割扩展名 | `os.path.splitext("file.py")` | `Path("file.py").stem` / `.suffix` | `stem` 主名，`suffix` 扩展名 |
| 判断是否存在 | `os.path.exists(p)` | `Path(p).exists()` | |
| 是否文件 / 目录 | `os.path.isfile(p)` / `isdir(p)` | `.is_file()` / `.is_dir()` | |
| 是否绝对路径 | `os.path.isabs(p)` | `.is_absolute()` | |
| 文件大小 | `os.path.getsize(p)` | `.stat().st_size` | 字节数 |
| 修改时间 | `os.path.getmtime(p)` | `.stat().st_mtime` | 时间戳，`datetime.fromtimestamp()` 转 |
| 遍历目录 | `os.listdir("dir")` | `.iterdir()` 或 `.glob("*")` | 返回 `Path` 迭代器 |
| 递归遍历 | `os.walk()` | `.rglob("*.py")` | 见 [[02-文件匹配与遍历]] |
| 创建目录 | `os.makedirs("d/sub", exist_ok=True)` | `.mkdir(parents=True, exist_ok=True)` | 见 [[03-目录创建与清空]] |
| 创建空文件 | `open(p,"w").close()` | `Path(p).touch()` | |
| 读文本 | `open(p).read()` | `.read_text()` | **必须显式传 encoding，见陷阱** |
| 写文本 | `open(p,"w").write(s)` | `.write_text(s)` | 同上 |
| 读 / 写二进制 | `open(p,"rb").read()` | `.read_bytes()` / `.write_bytes()` | |
| 路径各部分 | `split` + `basename` | `.parts` | 元组，如 `('/home','user','doc.txt')` |
| 比较路径相同 | `normpath(a) == normpath(b)` | `p1.resolve() == p2.resolve()` | |
| 是否符号链接 | `os.path.islink(p)` | `.is_symlink()` | |
| 真实路径 | `os.path.realpath(p)` | `.resolve()` | |
| 公共前缀 | `os.path.commonpath(paths)` | 无直接对应，仍用 `os.path` | |

## 2. 方案：常用组合

```python
from pathlib import Path

# 拼路径 + 建目录
out = Path("output") / "2026" / "11"
out.mkdir(parents=True, exist_ok=True)

# 取主名与扩展名
p = Path("/data/report.tar.gz")
p.name      # report.tar.gz
p.stem      # report.tar   ← 只去掉最后一个后缀
p.suffix    # .gz          ← 同理
p.suffixes  # ['.tar', '.gz']   ← 要看全部用这个

# 换后缀
p.with_suffix(".csv")     # /data/report.tar.csv

# 读写（显式编码，见陷阱 1）
cfg = Path("config.json")
cfg.write_text('{"a": 1}', encoding="utf-8")
cfg.read_text(encoding="utf-8")
```

## 3. 方案：`absolute()` 与 `resolve()` 的区别

```python
p = Path("a") / "b" / ".." / "c" / "file.txt"

print(p)             # a/b/../c/file.txt
print(p.absolute())  # 绝对路径，但保留 .. —— 不去解析符号链接
print(p.resolve())   # 绝对路径 + 消除 .. + 解析符号链接
```

- `.absolute()`：只加前缀，**不消 `..`、不解析链接**；
- `.resolve()`：**比较路径、做安全检查时用它**。

```python
p1 = Path("a/b/../c/file.txt")
p2 = Path("a/c/file.txt")
p1 == p2                      # False —— 纯字符串比较
p1.resolve() == p2.resolve()  # True  —— 真实路径一致
```

## 4. 方案：`Path` 与 `PurePath`

- `Path`：操作系统感知，能碰文件系统（读写、判断存在）；
- `PurePath`：纯字符串层面的路径对象，不碰磁盘，适合跨平台路径逻辑（比如在 Linux 上算 Windows 风格路径）。

日常全用 `Path` 就行，`PurePath` 用得很少。

## 5. 方案：`os.path.normpath` 的行为（读旧代码用）

只做**语法**层面清理，不访问文件系统、不解析符号链接。

```python
import os
os.path.normpath("a/b//c/./d")     # a/b/c/d     合并重复分隔符 + 去 .
os.path.normpath("a/b/../c")       # a/c         消 ..
os.path.normpath("a/b/../../c")    # c           能上移就消，超出根就保留
os.path.normpath("/a/b/../../c")   # /c          不越过根
os.path.normpath("../../../a")     # ../../../a  无根可上移，.. 保留
os.path.normpath("")               # .           ← 空串变当前目录，容易踩
```

Windows 上还会把 `/` 统一成 `\` 并保留盘符：`normpath("C:\\a\\b\\..\\c")` → `C:\a\c`。

**`normpath` vs `realpath`**：前者只改字符串（不碰磁盘），后者会解析符号链接（要碰磁盘）。对应的 pathlib 版本分别是「没有等价物（`resolve()` 两者都做）」和 `resolve()`。

## 6. 陷阱清单

| 陷阱 | 后果 | 正解 |
|---|---|---|
| `read_text()` / `write_text()` 不传 encoding | **默认是 locale 编码，不是 UTF-8**。Windows 上是 GBK，读 UTF-8 文件直接 `UnicodeDecodeError` 或乱码 | 永远写 `encoding="utf-8"`（读别人给的旧文件才考虑 `gbk`） |
| 用 `.stem` 处理多个后缀的文件 | `report.tar.gz` 得到 `report.tar`，不是 `report` | 看全部后缀用 `.suffixes`，或 `name.split(".")[0]` |
| 直接用 `p1 == p2` 比较路径 | 含 `..`、大小写、符号链接时判不相等 | `p1.resolve() == p2.resolve()` |
| `.absolute()` 当 `.resolve()` 用 | 路径里还留着 `..`，后续拼接可能出错 | 要规范化用 `resolve()` |
| `Path("a") / "b"` 里混进绝对路径 | 右边是绝对路径时**直接替换**左边，`Path("/x") / "/y"` 得 `/y` | 拼接前确认各段都是相对的 |
| 用 `+` 拼路径字符串 | 不跨平台，缺分隔符时静默拼错 | 用 `/` 或 `os.path.join` |

## 7. 一句话速查

> 拼路径 `p / "sub"`；取名字 `.name`/`.stem`/`.suffix`；比较 `.resolve()`；读写必带 `encoding="utf-8"`；遍历 `.rglob()`。

---

回到：[[cs/dev/python/index|Python 导航]]　下一篇：[[02-文件匹配与遍历]]
