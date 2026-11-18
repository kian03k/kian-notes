---
tags: [python, 脚本, 音视频]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# 调用 FFmpeg（subprocess）

> **适用场景**：批量转音频格式、视频掐头去尾、从视频抽音频。
> Python 本身不处理音视频，靠 `subprocess` 拼命令行调 FFmpeg / ffprobe。

**统一原则：用列表传参** `["ffmpeg", "-i", path, ...]`，别用字符串拼接——免去转义地狱，路径带空格也不会崩。

## 1. 方案：批量转 MP3

```python
subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(src),
    "-codec:a", "libmp3lame", "-b:a", "320k",
    str(tmp),                     # 先写临时文件 unsure_x.mp3
])
```

**模式：先写临时文件，成功后再 `rename` 成目标名。** 这样中途中断只会留下 `unsure_` 前缀的残留文件，不会污染正式产物；下次运行还能靠"目标已存在就跳过"避免重复转换。

## 2. 方案：视频掐头去尾（无损）

```python
total = float(subprocess.run(
    ["ffprobe", "-i", src, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
    stdout=subprocess.PIPE, text=True).stdout)

subprocess.run([
    "ffmpeg", "-i", src, "-ss", str(start), "-to", str(total - end),
    "-c", "copy",                 # 不重新编码：快、无损
    "-fflags", "+genpts",         # 关键：重写时间戳，防播放器时间轴错乱
    dst,
])
```

> `-c copy` 要求切点在关键帧上，否则开头可能花屏或黑屏。对精度要求高时去掉 `copy` 重新编码。

## 3. 方案：抽音频的两种策略

| 策略 | 命令 | 特点 |
|---|---|---|
| 原样复制 | `-vn -acodec copy` | 快、无损，编码随源（mp4→aac） |
| 重编码 MP3 | `-vn -q:a 0 -map a` | 通用，耗时、有损（`-q:a 0` 为最高音质） |

## 4. 常用参数速记

| 参数 | 作用 |
|---|---|
| `-y` | 覆盖输出，不询问 |
| `-hide_banner -loglevel error` | 静音日志，只留错误 |
| `-b:a 320k` | 音频码率 |
| `-c copy` | 流复制，不转码 |
| `-vn` | 丢掉视频轨 |
| `-ss` / `-to` | 起始 / 结束时间 |

## 5. 陷阱清单

| 坑 | 后果 | 对策 |
|---|---|---|
| 字符串拼命令 | 路径含空格/中文直接失败 | 列表传参 |
| 直接写目标文件 | 中断留下损坏的正式产物 | 先写临时文件再 rename |
| 不检查 `returncode` | 转换失败也当成成功 | `subprocess.run(..., check=True)` |
| 未装 FFmpeg | `FileNotFoundError` | 启动前 `shutil.which("ffmpeg")` 检测 |
| Windows 下用 `ffmpeg` 简名 | 找不到可执行文件 | 传绝对路径或用 `shutil.which` 解析 |

---

回到：[[cs/dev/python/index|Python 导航]]
