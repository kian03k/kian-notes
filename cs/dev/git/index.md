---
tags: [git, index]
created: 2026-10-24
updated: 2026-11-16
status: ok
---

# Git · 导航

> `cs/dev/git/` 目录索引。三层结构，各答一个问题：
> **guide/** —— 想系统学，从 0 到全链路按序读；
> **notes/** —— 想查原理、机制、规范，按主题查；
> **case-library/** —— 已经做错了，按症状救急。

## 教程（`guide/`，按序读）

| 章节 | 解决什么 |
| --- | --- |
| [[01-环境与身份配置]] | 安装、user.name/email、换行符策略、SSH 多账号、`.gitignore` |
| [[02-仓库与远程连接]] | 本地有无仓库 × 远端空/非空的四种情形，remote 与首次推送 |
| [[03-分支模型与日常循环]] | `main` / `wip` / `feature` 职责划分、提交规范、pull 策略 |
| [[04-同步主干与冲突解决]] | merge 与 rebase 的判定规则、冲突现场处理、安全强推 |
| [[05-合并发布与版本标记]] | PR 流程、三种合并方式选择、标签与快照 |
| [[06-大文件与LFS]] | LFS 接入、历史迁移、证书问题 |
| [[07-故障恢复]] | reflog、误操作恢复、工作区重置、强推边界 |
| [[08-开源协作Fork模式]] | 给别人的项目提 PR：fork、upstream、review 迭代 |

## 知识记录（`notes/`，按主题查）

| 笔记 | 内容 |
| --- | --- |
| [[rebase与merge]] | 两者改写的到底是历史还是内容；私有/共享分支的判定与取舍 |
| [[git标签]] | 轻量 vs 附注、推送、回到某版本、标签与分支的区别 |
| [[git-lfs]] | 指针机制、LFS 走 HTTPS 而 SSH 只负责 Git、历史迁移、自签证书 |
| [[ssh密钥与多账号]] | ed25519 与 RSA 对比；一把公钥只能绑一个账号，多账号 config 隔离 |
| [[git配置位置及命令解释]] | 全局 / 仓库级配置文件在哪，各配置项含义 |
| [[WSL2 + Git 项目规范化管理指南]] | 开源协议选择、仓库命名、GitHub 体积限制、WSL2 目录规划 |
| [[gitignore常见问题]] | 已跟踪文件加进 `.gitignore` 为什么无效，正确做法 |
| [[Git Detects Changes]] | 文件未改却显示已修改——权限、换行符等假阳性排查 |
| [[行分割符修复]] | CRLF / LF 混用导致整个文件 diff 的处理 |
| [[VSCODE配合GIT]] | 用 VS Code 做日常 Git 操作的配置 |

## 场景急救（`case-library/`，按症状查）

| 笔记 | 症状 |
| --- | --- |
| [[误在main分支开发，需同步至dev]] | 提交错分支了，把提交搬到正确的分支 |
| [[分支错乱恢复]] | 本地与远端指向不一致，用 `branch -f` + `force-with-lease` 重建 |

## 高频操作速查

| 目的 | 命令 |
| --- | --- |
| 撤销暂存（不丢改动） | `git restore --staged <file>` |
| 撤销工作区改动（**会丢**） | `git restore <file>` |
| 把提交搬到新分支 | `git branch <new> && git reset --hard HEAD~<n> && git switch <new>` |
| 看某次提交改了什么 | `git show <hash>` |
| 临时保存当前改动 | `git stash` / `git stash pop` |
| 找回误操作的提交 | `git reflog` → `git reset --hard HEAD@{n}` |
| 强推用哪个 | `git push --force-with-lease`（不用 `--force`） |
| 当前分支落后多少 | `git branch -vv` |

> 危险操作前先 `git status` 确认，或先 `git stash` 兜底。
