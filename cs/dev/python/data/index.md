---
tags: [python, index]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# data/ · 数据与内容处理

> 六条线共 18 篇：表格 → 表格文件 → 文本 → 出图 → 音视频 → 序列化。前五条遵循同一个套路——**打开某种载体的内容 → 解析 → 改写 → 输出**；序列化是它们的逆操作（对象 ↔ 字节）。
> 上级索引：[[cs/dev/python/index|Python 索引]]

## pandas/ — 表格数据处理

六篇连号，从数据结构到性能优化。用 pd 处理表格，用 np 理解底层。

| 笔记 | 内容 |
| --- | --- |
| [[01-DataFrame创建基础]] | DataFrame 是什么、创建方式、属性、loc/iloc 访问行 |
| [[02-三剑客merge-concat-groupby]] | merge 拼列、concat 拼行、groupby 汇总；陷阱与模板 |
| [[03-逐行遍历itertuples]] | 必须循环时最快的方式，与 iterrows / 向量化的性能对比 |
| [[04-Excel多Sheet读写]] | ExcelWriter 一次写多 Sheet，保留原文件全部 Sheet 只改部分 |
| [[05-NaN与np-pd关系]] | np/pd 分工、`pd.isna` vs `np.isnan`、numpy 最小子集 |
| [[06-str.contains向量化匹配]] | 多型号子串匹配从 apply 改向量化，提速 180 倍的完整案例 |

## excel/ — Excel 与 CSV 文件

| 笔记 | 内容 |
| --- | --- |
| [[01-Excel读写]] | openpyxl / pandas 选型，读分算分写回，按列对号入座 |
| [[02-CSV读写]] | DictReader/Writer、大文件流式处理、编码坑 |
| [[03-openpyxl合并单元格]] | 合并单元格的数据归属、`centerContinuous` 跨列居中 |
| [[04-CSV列重排与映射]] | 换列序、改标签取值、大文件流式处理（不依赖 pandas） |
| [[05-CSV与Excel互操作]] | 长数字变科学计数法、中文乱码：导出端与 Excel 端双向治理 |

## text/ — 文本与正则

| 笔记 | 内容 |
| --- | --- |
| [[01-字符串清理]] | rstrip/strip 取舍、去前后缀、split 切分、隐藏空白字符 |
| [[02-正则速查与替换]] | sub / findall / split / subn、元字符速查、文本清洗 |
| [[03-正则匹配对象]] | 捕获组、命名组、`groupdict()`、判空规范 |
| [[04-正则切分配置块]] | 非贪婪 + 前瞻断言切分结构化配置块（完整验证过的模式） |

## charts/ — 出图

| 笔记 | 内容 |
| --- | --- |
| [[01-matplotlib出图]] | 中文字体与负号设置、折线/柱状、无界面服务器 savefig |

## media/ — 音视频处理

| 笔记 | 内容 |
| --- | --- |
| [[01-调用FFmpeg]] | 批量转 MP3、视频截取无损、抽音频、参数速记 |

## serialization/ — 序列化

| 笔记 | 内容 |
| --- | --- |
| [[01-pkl与gzip]] | `.pkl.gz` 本质、gzip.open 自动解压、自动检测压缩状态、**pickle 安全边界** |

## 串起来看

一条典型链路：`excel/01` 读原始表 → `pandas/02` 拼表汇总 → `text/02` 清洗字段 → `charts/01` 出图。
每一步都可以单独用，按需跳转即可。
