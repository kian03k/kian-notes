---
tags: [git, index]
created: 2026-10-24
updated: 2026-10-24
status: ok
---

# Git · 导航

> `cs/dev/git/` 目录索引。日常用法在根层，场景化操作在 `case-library/`。

## 基础与配置

| 笔记 | 内容 |
| --- | --- |
| [[git配置位置及命令解释]] | 全局 / 仓库级配置文件在哪，各配置项含义 |
| [[VSCODE配合GIT]] | 用 VS Code 做日常 Git 操作的配置 |
| [[Git Detects Changes]] | 文件未改却显示已修改——权限、换行符等假阳性排查 |
| [[行分割符修复]] | CRLF / LF 混用导致整个文件 diff 的处理 |
| [[gitignore常见问题]] | 已跟踪文件加进 `.gitignore` 为什么无效，正确做法 |
| [[WSL2 + Git 项目规范化管理指南]] | WSL2 环境下的仓库结构与提交规范 |

## 场景化操作（`case-library/`）

| 笔记 | 适用场景 |
| --- | --- |
| [[ssh_init]] | 从零生成 SSH key 并配置到 GitHub |
| [[完整Git协作开发流程]] | 分支模型、PR、合并的完整协作流程 |
| [[本地无git仓库，远端为空]] | 全新项目推到远端空仓库 |
| [[本地有git仓库，远端为空]] | 已有项目关联到远端空仓库 |
| [[误在main分支开发，需同步至dev]] | 改错了分支，把提交搬到正确分支 |

## 高频操作速查

| 目的 | 命令 |
| --- | --- |
| 撤销暂存（不丢改动） | `git restore --staged <file>` |
| 撤销工作区改动（**会丢**） | `git restore <file>` |
| 把提交搬到新分支 | `git branch <new> && git reset --hard HEAD~<n> && git switch <new>` |
| 看某次提交改了什么 | `git show <hash>` |
| 临时保存当前改动 | `git stash` / `git stash pop` |

> 危险操作前先 `git status` 确认，或先 `git stash` 兜底。
