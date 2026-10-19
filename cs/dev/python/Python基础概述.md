---
tags: [python, 基础, 思维导图]
created: 2026-10-13
updated: 2026-10-13
status: draft
---

# Python 基础概述

> 一张 Python 基础知识体系的思维导图（微信导出图），用作学习路线索引与查漏补缺清单。

![Python 基础思维导图](assets/Python基础概述/python基础思维导图.png)

## 知识体系大纲

> 以下分支按导图主干整理，**细节以图为准**，后续可逐步展开成独立笔记。

- **基础语法**：变量与命名、数据类型（int/float/str/bool）、运算符、输入输出
- **流程控制**：条件分支（if/elif/else）、循环（for/while）、break/continue
- **数据结构**：列表、元组、字典、集合及其常用操作
- **函数**：定义与调用、参数（位置/默认/可变）、返回值、作用域、lambda
- **面向对象**：类与对象、属性与方法、继承、多态、魔术方法
- **模块与包**：import 机制、第三方库安装、`__name__` 作用
- **异常处理**：try/except/else/finally、raise、自定义异常
- **文件操作**：open 模式、读写、with 上下文管理、路径处理
- **常用标准库 / 第三方库**：os、sys、re、json、datetime、requests 等
- **高级特性**：推导式、迭代器与生成器、装饰器、闭包、上下文管理器

## 系列笔记（2026-10-15 从 `D:\Projects\Python\old` 提炼）

| 篇 | 内容 | 难度 |
| --- | --- | --- |
| [[01-速查手册]] | 变量/流程/数据结构/函数/推导式/内置函数/踩坑清单 | ★ |
| [[02-函数进阶]] | 递归 · 高阶函数 · 闭包 · 装饰器 · **深浅拷贝** | ★★★ |
| [[03-面向对象]] | 类/继承/多态 · classmethod/staticmethod · @property · `__new__` · 自定义异常 | ★★★ |
| [[04-数据处理]] | Excel(openpyxl) · CSV · 正则 · 异常 · numpy · matplotlib | ★★ |
| [[05-Flask入门]] | 路由/模板/JSON 接口 · pymysql CRUD · ajax + ECharts · 全链路项目 | ★★★ |
| [[06-实用脚本模式]] | 批量重命名 · 去重 · 目录体积 · watchdog · CSV 重排 · FFmpeg 调用 · 爬虫三件套 | ★★ |

> 另：`env_setup/`（Windows / WSL2 环境搭建）、`pyinstaller.md`（打包）。

## 待办

- [x] 逐分支补充细节笔记（2026-10-15 完成 5 篇，见上表）
- [ ] 迭代器 / 生成器 / 上下文管理器（3.x 高级特性，暂未成篇）
- [ ] asyncio 异步编程（需要时再补）
