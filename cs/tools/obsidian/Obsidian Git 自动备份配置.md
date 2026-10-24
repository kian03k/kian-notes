---
tags: [obsidian, git, 插件配置, 备份]
created: 2026-10-24
updated: 2026-10-24
status: ok
---

# Obsidian Git：关掉自动备份，改纯手动

> 结论：**自动备份对个人知识库是负收益**。它把"什么时候该提交"的决定权交给了定时器，代价是隐私文件和二进制大文件随时可能被推上去，而且提交历史会被切成大量无意义的"vault backup"碎片。

## 一、先搞清三个"自动"不是一回事

很多人以为关掉自动保存就完事了，其实有三个独立开关：

| 配置键 | 作用 | 默认值 |
| --- | --- | --- |
| `autoSaveInterval` | 每隔 N 分钟自动 **commit**（本地） | 30 |
| `autoPushInterval` | 每隔 N 分钟自动 **push**（到远程） | 180 |
| `autoBackupAfterFileChange` | **文件一改就触发** commit+push | true |
| `autoPullInterval` | 每隔 N 分钟自动 **pull** | 180 |
| `autoPullOnBoot` | 打开 vault 时自动 pull | true |

三个都关，才是真的静默：

```json
"autoSaveInterval": 0,
"autoPushInterval": 0,
"autoPullInterval": 0,
"autoPullOnBoot": false,
"autoBackupAfterFileChange": false
```

> 只关 `autoSaveInterval` 不够——`autoBackupAfterFileChange` 是另一条独立的触发路径，改一个文件它就备份一次，比定时器还频繁。

## 二、为什么要关

真实踩过的坑：

1. **大文件被自动推走**：一次往 `_inbox/` 放了 41MB 的 docx，Obsidian Git 三分钟内自动 commit+push，文件直接进了 GitHub 历史。后来要清掉，得 `reset` + `force push` + `gc`，`.git` 从 47MB 才缩回 9.6MB。
2. **隐私文件风险**：`.gitignore` 里排除了 `随记/`，但只要规则被误改或失效，下一次自动 `add -A` 就会把它带上——**你根本没机会看一眼暂存区**。
3. **提交历史被切碎**：一天几十个 "vault backup: 2026-10-24 21:34:21"，想找"哪次改了什么"完全无从下手。
4. **冲突无人处理**：自动 pull 遇到本地未提交改动会失败，弹窗一闪而过，很容易忽略。

手动提交反而更清楚：改完一批 → 看一眼 `git status` → 写一句人话的 commit message。

## 三、怎么关

### 方式一：设置界面（推荐）

`设置 → 第三方插件 → Obsidian Git`，把这几项改成 0 / 关闭：

- Backup → **Auto backup interval** → `0`
- Backup → **Backup after file change** → 关
- Commit-and-push → **Auto push interval** → `0`
- Pull → **Auto pull interval** → `0`
- Pull → **Auto pull on boot** → 关

### 方式二：直接改配置文件

文件：`.obsidian/plugins/obsidian-git/data.json`

改完**必须重启 Obsidian**（或在设置里先禁用插件再启用）。因为插件在运行时会把内存里的配置写回这个文件，不重启的话你的修改会被覆盖。

## 四、关掉之后怎么手动操作

命令面板（`Ctrl + P`）里搜 `Obsidian Git`：

| 命令 | 作用 | 使用场景 |
| --- | --- | --- |
| **Commit all changes** | 全部暂存并提交（不推送） | 本地存档一个阶段 |
| **Commit and push** | 提交并推到远程 | 最常用 |
| **Pull** | 拉取远程更新 | 换机器前先拉 |
| **Create backup** | 一键 commit + push | 相当于原来的自动备份，改成手动触发 |
| **Open source control view** | 左侧栏打开改动列表 | 提交前逐项检查 |

习惯建议：**一个任务做完就 Commit and push 一次**，message 写清楚改了什么。比每天几十个 "vault backup" 有用得多。

## 五、几个容易忽略的点

- **关掉自动备份 ≠ 关掉 git**。插件仍在，只是不再自己触发。手动命令全部可用。
- **`.gitignore` 仍然重要**。手动 `git add -A` 一样会把未忽略的文件全加进去，所以忽略规则不能省。
- **配合 `.git/info/exclude` 双保险**。它在 `.git` 目录里，不参与版本控制，别人删不掉也 pull 覆盖不了，能挡住自己误 `add` 隐私文件。
- **换机器时记得先 Pull**。自动 pull 关了，就没有人替你拉最新代码了。
- **提交前养成看 diff 的习惯**。`Open source control view` 面板能看到每个文件改了什么，比盲提交安全。

## 六、我的推荐配置

| 场景 | 建议 |
| --- | --- |
| 个人知识库、单人维护 | **全关**，纯手动（本文配置） |
| 多人协作、需要频繁同步 | 只开 `autoPullInterval`（如 30 分钟），commit/push 保持手动 |
| 练手仓库、不在乎历史 | 全开无所谓 |

个人库最大的价值是"每一版都值得留"，而不是"每五分钟存一次"。
