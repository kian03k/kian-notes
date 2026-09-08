---
tags: [markdown, base64, 编码, 图片]
created: 2026-09-08
updated: 2026-09-08
status: ok
---

# 提取 Markdown 内嵌的 Base64 图片

> 把 md 文件里 `data:...;base64,...` 形式的内嵌图片还原为独立图片文件，并替换为相对路径引用。

## 背景 / 问题

知识库清理时发现三篇笔记（CUDA安装教程、中文输入法配置、windows版卸载anaconda）共 56 张图片以 base64 data URI 直接写在 md 里，导致：

- 单文件 1MB+，git diff 全是乱码，无法审查改动；
- Obsidian 渲染大文件卡顿；
- 图片无法被 `assets/<笔记名>/` 规则统一管理。

## Base64 是什么

一种**用文本承载二进制**的编码：每 3 个字节（24 bit）切为 4 组各 6 bit，每组映射到 64 个可打印字符（`A-Z a-z 0-9 + /`），不足 3 字节倍数时用 `=` 补位。

- 例：`Man` → `01001101 01100001 01101110` → 6 bit 分组 `19,22,5,46` → `TWFu`。
- 代价：体积膨胀 **4/3**（3 字节变 4 字符），所以内嵌 base64 的 md 都异常大。
- md 中的形态是 data URI：`![alt](data:image/png;base64,iVBORw0KG...)`，冒号后是 MIME 声明 + 分号 + `base64,` + 纯文本数据。

## 提取流程（Python）

```python
import re, base64

b64_re = re.compile(r"!\[([^\]]*)\]\(data:[^;()]+;base64,([A-Za-z0-9+/=]+)\)")
MAGIC = [("/9j/", ".jpg"), ("iVBOR", ".png"), ("R0lGOD", ".gif"), ("UklGR", ".webp")]

for m in b64_re.finditer(text):
    data = m.group(2)                        # 纯文本 base64
    ext = next((e for magic, e in MAGIC if data.startswith(magic)), ".bin")
    raw = base64.b64decode(data)             # 还原为原始字节流
    open(f"assets/{note}/img-01{ext}", "wb").write(raw)
```

四步：

1. **正则匹配**捕获 base64 文本（base64 字符集不含 `)`，所以正则可以安全地在第一个 `)` 处终止）；
2. **解码**：`base64.b64decode` 把文本还原为原始字节流——此时已经是一张完整的图片文件；
3. **魔数判型**：读字节流前几个字节判断格式，与声明的 MIME 无关（见下）；
4. **写文件 + 替换引用**为 `assets/<笔记名>/img-NN.<ext>` 相对路径。

## 踩坑记录

- **MIME 声明不可信**：本次三篇笔记全部声明为 `application/octet-stream`（"未知二进制"），实际是 jpeg/webp/png 混杂。判断格式唯一可靠的依据是**魔数**：
  - `FF D8 FF` → JPEG（base64 开头即 `/9j/`）
  - `89 50 4E 47` → PNG（base64 开头 `iVBOR`）
  - `47 49 46 38` → GIF（base64 开头 `R0lGOD`）
  - `52 49 46 46 ... 57 45 42 50` → WebP（base64 开头 `UklGR`）
- **魔数判型不等于看过图片**：只比对文件头几个字节，图片内容完全没有被读取或识别；`img-01` 等文件名只是顺序编号，原文的 alt 描述会原样保留在引用里。
- 判断"某篇笔记是否有内嵌图"用 `grep -c "data:application" *.md` 即可，有内嵌图的 md 文件体积会明显偏大（数百 KB 起）。

## 参考

- [RFC 4648（base64 规范）](https://datatracker.ietf.org/doc/html/rfc4648)
- 本库实践案例：`cs/ai/env_setup/cuda/CUDA安装教程.md`（34 张）、`cs/os/linux/env_setup/中文输入法配置.md`（21 张）
