---
tags: [linux, 命令, 基础]
created: 2026-04-22
updated: 2026-10-24
status: ok
---

# Linux 常用命令

## 文件与目录

| 命令 | 作用 | 常用写法 |
| --- | --- | --- |
| `cd` | 切换目录 | `cd /etc`；`cd ..` 回上级；`cd` 或 `cd ~` 回主目录 |
| `pwd` | 显示当前所在路径 | `pwd` |
| `ls` | 列出目录内容 | `ls`；`ls -l` 详情；`ls -a` 含隐藏文件 |
| `ll` | 等价于 `ls -l`（多数发行版预置的别名） | `ll` |
| `touch` | 新建空文件 | `touch index.js` |
| `mkdir` | 新建目录 | `mkdir src`；`mkdir -p a/b/c` 递归创建 |
| `rm` | 删除文件 | `rm index.js` |
| `rm -r` | 递归删除目录 | `rm -r src` |
| `mv` | 移动 / 重命名 | `mv index.html src/`；`mv a.txt b.txt` 为重命名 |
| `cp` | 复制 | `cp a.txt b.txt`；`cp -r src dest` 复制目录 |

> 注意 `mv` 的写法：目标若是**已存在的目录**，直接写目录名即可（`mv index.html src/`）；原文示例 `mv index.html src index.html` 多写了一个源文件，会把两个路径都当成源。

## 终端操作

| 命令 | 作用 |
| --- | --- |
| `clear` | 清屏 |
| `reset` | 重新初始化终端（输出错乱、显示异常时用） |
| `history` | 查看命令历史 |
| `help` | 查看帮助（多数命令也支持 `--help`） |
| `exit` | 退出当前 shell |
| `#` | 注释，`#` 之后的内容不执行 |

> `clear` 只是把内容顶出可视区，`reset` 才是真正重置终端状态——两者别混用。

## 其他记录

### 关闭占用某端口的进程

```bash
sudo fuser -k 5000/tcp
```

### `/tmp` 会自动清空

系统重启、会话断开（如 VS Code 重连）都会自动清空 `/tmp` —— 重进后看不到之前的安装包不是误删，是机制如此。
