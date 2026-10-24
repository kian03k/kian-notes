---
tags: []
created: 2026-09-08
updated: 2026-10-13
status: ok
---

# kian-notes

个人知识库。总入口 + 目录总览，详细规则见 [cs/docs/结构规范.md](cs/docs/结构规范.md)。

## 目录总览

```txt
kian-notes/
├── README.md            # 本文件：总入口索引
├── _inbox/              # 收件箱：碎片/未整理笔记，定期归类
├── cs/                  # 计算机技术主区
│   ├── ai/              # AI（env_setup / model / practice 按需建）
│   ├── algorithm/       # 算法（新建）
│   ├── dev/             # 通用开发：cpp / python / web / git / java / architecture
│   ├── docs/            # 文档规范：md/ 语法 + template/ 笔记模板 + 结构规范
│   ├── infra/           # 基础设施：docker / MySQL
│   ├── os/              # 操作系统：linux / windows
│   └── tools/           # 开发工具：JetBrains / 工具激活
├── network/             # 网络数通（一级主题，与 cs 同级，数通资料归此）
│   ├── index.md         # 网络区导航（协议 / 题库 / 故障排查）
│   ├── 协议/            # 协议原理详解：OSPF / BGP / VXLAN-EVPN / RoCE / M-LAG / QoS / 华为设备
│   ├── 题库/            # 题库与备考：总览 + 六份分级题库 + HCIP-811 索引
│   ├── 故障排查/        # 实际调测问题排查记录（ping -a 系列等）
│   └── Windows路由配置.md
└── English/             # 英语（保留，内容多了再划分子目录）
```

## 常用入口

- 开发环境：[Python 环境搭建](cs/dev/python/env_setup/Python%20Env%20Setup.md)
- Docker / MySQL：[cs/infra/docker](cs/infra/docker/MySQL/1.安装.md)
- Linux：[os/linux](cs/os/linux/linux常用命令.md)
- 数通导航：[network/index.md](network/index.md)（协议原理 / 面试题库 / 故障排查）
- 数通故障排查：[network/故障排查](network/故障排查/CE%20交换机%20ICMP%20快回导致%20ping%20-a%20失败分析.md)
- 写作规范与模板：[cs/docs](cs/docs/结构规范.md)

## 核心规则速览（详见结构规范）

1. **资源**：图片存放在所在目录的 `assets/<笔记名>/`，相对路径引用，由 Obsidian 插件 Custom Attachment Location 自动落位。
2. **index**：某二级主题笔记数 **超过 12 篇** 时创建该主题的 `index.md` 导航页，在此之前靠目录浏览。
3. **归档**：手动执行，在各主题目录内建 `_archive/` 子目录存放过时内容，不建全局归档目录。
4. **收件箱**：未定型的碎片先进 `_inbox/`，每周归类一次；禁止"未命名/temp/fragments"类文件留在正式目录。
