---
tags: [python, index]
created: 2026-10-24
updated: 2026-11-15
status: ok
---

# Python · 导航

> `cs/dev/python/` 目录索引。体系化教程在 `guide/`，日志专题在 `logging/`，具体问题按主题归入 `data/`、`packaging/`，环境搭建在 `env_setup/`。

## guide/ — 体系化教程

按 `01`→`06` 顺序读。

| 笔记 | 内容 |
| --- | --- |
| [[Python基础概述]] | 基础思维导图总览，先建立全局印象 |
| [[01-速查手册]] | 语法速查，日常翻得最多 |
| [[02-函数进阶]] | 递归、高阶函数、闭包、装饰器、深浅拷贝 |
| [[03-面向对象]] | 类、继承、多态、类方法、属性、魔术方法 |
| [[04-数据处理]] | Excel、CSV、正则、异常、numpy、matplotlib |
| [[05-Flask入门]] | 从 Hello World 到前端 + 数据库 + 图表全链路 |
| [[06-实用脚本模式]] | 常见自动化脚本套路 |

## logging/ — 日志专题

自成体系，从 [[00-总览]] 的场景索引进入。

| 笔记 | 内容 |
| --- | --- |
| [[00-总览]] | 场景索引、30 秒核心概念、选型铁律 |
| [[01-快速上手]] | 单文件脚本 basicConfig 三步接入、format 占位符速查 |
| [[02-标准框架]] | 多模块项目 setup_logging()、getLogger(__name__) 原理、4 代方案演进 |
| [[03-进阶配置]] | 日志轮转、控制台/文件分级、模块级控级、dictConfig、远程采集 |
| [[04-特殊场景手册]] | 异常记录姿势、日志重复输出、旧方案迁移、单测 mock |

## data/ — 数据处理

`04-数据处理` 的深水区，按需查阅。

| 笔记 | 内容 |
| --- | --- |
| [[openpyxl 合并单元格]] | 合并单元格的数据归属、`centerContinuous` 跨列居中 |
| [[正则切分配置块]] | 非贪婪 + 前瞻断言切分设备配置块 |

## packaging/ — 打包分发

| 笔记 | 内容 |
| --- | --- |
| [[pyinstaller]] | 打包成独立可执行文件 |

## env_setup/ — 环境搭建

| 笔记 | 平台 / 场景 |
| --- | --- |
| [[Python Env Setup for wsl2]] | WSL2 + Miniconda + PyCharm |
| [[Python Env Setup]] | 虚拟机 Linux（Ubuntu/CentOS）+ Anaconda + Python 3.12 |
| [[python 编辑环境创建]] | Conda 环境管理与开发配置（精简版） |
| [[常用命令]] | conda 常用命令 |
| [[windows版卸载anaconda]] | Windows 下彻底卸载 Anaconda |

## 读法建议

- **零基础起步**：`guide/Python基础概述` 看图建立框架 → `01` 速查 → `02`~`03` 补语法深度
- **要干活**：直接跳 `04-数据处理` 和 `06-实用脚本模式`；遇到具体问题再查 `data/`
- **要接日志**：脚本看 `logging/01`，项目直接抄 `logging/02` 的 setup_logging()
- **配环境**：Windows 开发选 `Python Env Setup for wsl2`，纯 Linux 服务器选 `Python Env Setup`
- **要交付**：`packaging/pyinstaller` 打独立可执行文件
