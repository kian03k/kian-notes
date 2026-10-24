---
tags: []
created: 2026-09-08
updated: 2026-10-24
status: ok
---

# kian-notes

个人知识库。**本文件既是总入口，也是全库唯一的规则来源**——目录规划与现实不一致时，以修正目录或修正本文档的方式保持同步，不允许长期共存两套说法。

## 目录总览

```txt
kian-notes/
├── README.md            # 本文件：总入口 + 结构规范
├── _inbox/              # 收件箱：碎片/未整理笔记，定期归类
├── cs/                  # 计算机技术主区
│   ├── ai/              # AI：图像处理基础 / mcp / env_setup(cuda)
│   ├── algorithm/       # 算法
│   ├── dev/             # 通用开发：cpp / python / java / web(vue) / android / git / architecture
│   ├── docs/            # 文档规范：md/ 语法 + template/ 笔记模板
│   ├── infra/           # 基础设施：docker / database(MySQL)
│   ├── os/              # 操作系统：linux / windows
│   └── tools/           # 开发工具：JetBrains / obsidian / 工具激活
├── network/             # 网络数通（一级主题，与 cs 同级）
│   ├── index.md         # 网络区导航
│   ├── 协议/            # 协议原理详解：OSPF / BGP / VXLAN-EVPN / RoCE / M-LAG / QoS
│   ├── 题库/            # 题库与备考：六份分级题库 + HCIP-811 索引
│   ├── 故障排查/        # 实际调测问题排查记录（ping -a 系列等）
│   └── Windows路由配置.md
└── English/             # 英语（保留一级目录，内容多了再划分子目录）
```

## 常用入口

- Python：[cs/dev/python/index.md](cs/dev/python/index.md)（语言基础 + 环境搭建）
- Git：[cs/dev/git/index.md](cs/dev/git/index.md)（配置 + 场景化操作）
- 开发环境：[Python 环境搭建](cs/dev/python/env_setup/Python%20Env%20Setup.md)
- Docker / MySQL：[cs/infra/docker](cs/infra/docker/MySQL/1.安装.md)
- Linux：[os/linux](cs/os/linux/linux常用命令.md)
- 数通导航：[network/index.md](network/index.md)（协议原理 / 题库 / 故障排查）
- 数通故障排查：[network/故障排查](network/故障排查/CE%20交换机%20ICMP%20快回导致%20ping%20-a%20失败分析.md)
- 写作规范与模板：[cs/docs/md](cs/docs/md)

---

## 结构规范

### 一、目录职责

| 目录 | 职责 | 备注 |
|------|------|------|
| `README.md` | 总入口 + 全库结构规范 | 结构变更时同步更新 |
| `_inbox/` | 收件箱：碎片、未定型、来源不明的笔记 | 不设子目录；攒 3–5 篇即清，清空为目标 |
| `cs/ai/` | AI：`图像处理基础/`、`mcp/`、`env_setup/`（cuda） | 新方向出现第一篇再建子目录 |
| `cs/algorithm/` | 算法学习与题解 | |
| `cs/dev/` | 通用开发：`cpp/` `python/` `java/` `web/` `android/` `git/` `architecture/` | |
| `cs/docs/` | 文档规范：`md/` 语法排版、`template/` 笔记模板 | |
| `cs/infra/` | 基础设施：`docker/`（容器部署）、`database/`（数据库知识） | 两者职责不同，别混淆 |
| `network/` | 网络数通资料 | **一级主题，与 `cs/` 同级**；厂商配置、协议、抓包分析等均归此 |
| `cs/os/` | 操作系统：`linux/` `windows/` | |
| `cs/tools/` | 开发工具：`JetBrains/`、`obsidian/`、`工具激活/` | |
| `English/` | 英语学习 | 保留独立一级目录 |

#### 目录粒度原则

**一个目录里不足 3 篇笔记，就不要单独建目录**，文件直接放在上级目录里。

理由：目录层级是为了「减少一次浏览的选项数量」，不是为了分类而分类。4 层目录里只躺 1 个文件（反例：`cs/os/windows/browser_apps/optimization_config/Q&A.md`），点进去还得记住路径，比平铺更难找。

例外：按「工具」或「职能」天然独立的目录（`tools/obsidian/`、`docs/template/`、`xxx/assets/`）不受此限，即便只有 1 篇也合理。

### 二、index.md 触发条件

- 某个**二级主题**目录（如 `cs/dev/`、`cs/infra/`、`network/` 的子目录）下笔记数**超过 12 篇**时，创建该目录的 `index.md` 导航页。
- 12 篇以内靠目录浏览即可，不为索引而索引。
- `index.md` 只做链接导航（按子目录或主题分组），不写长篇内容。
- 计数口径：目录树内所有 `.md`，不含 `assets/` 资源、不含 `_archive/`、不含 `index.md` 自身。
- **当前已建索引**：`cs/dev/git/`（13 篇）、`cs/dev/python/`（13 篇）、`cs/ai/图像处理基础/`（10 篇，自带完整学习路线）、`network/`。接近阈值的：`network/题库/`（9 篇）、`network/协议/`（8 篇）。

### 三、资源（图片/附件）规则

1. **位置**：图片存放在**笔记所在目录**的 `assets/<笔记名>/` 子目录下，与笔记同目录树、紧贴存放。
2. **引用**：一律使用相对路径，如 `![](assets/1.安装/img1.png)`。禁止绝对路径、禁止 `file://`。
3. **自动化**：由 Obsidian 插件 **Custom Attachment Location** 落位，配置 `./assets/${noteFileName}`，并开启：
   - Automatically rename attachment folder（笔记改名时同步重命名资源目录）
   - 链接自动更新
   - Obsidian 内置"附件默认存放路径"不要同时启用子文件夹方案，避免两套规则冲突。
4. **命名**：规则约束资源目录（必须为 `assets/<笔记名>`），图片文件名不强制（时间戳名可保留）。
5. **层级**：资源目录只允许一层，禁止 `assets/A/B/` 式嵌套。
6. **例外**：跨笔记复用的通用图（logo、示意图）可放根目录 `attachments/`，出现时再建。

### 四、命名规范

1. 笔记文件名以**中文**为主，全库统一；避免中英混用（专有名词除外，如 CUDA、WSL2）。
2. 禁止 `未命名`、`新建文件`、`temp`、`test`、`fragments` 等占位名进入正式目录——未定型的进 `_inbox/`。
3. 同一主题的系列笔记可用编号前缀表达顺序，如 `1.安装.md`、`2.版本切换.md`、`Q&A.md`（沿用 infra 现有风格）。
4. 目录名用小写英文（`dev/`、`infra/`），笔记名用中文。

### 五、归档规则

1. **手动执行**：归档由库主人手动判断和操作，不设全局 `archive/` 目录。
2. **子集内归档**：过时内容移入**所在主题目录内**的 `_archive/` 子目录，保留原有层级，例如 `cs/dev/web/_archive/`。
3. 归档时在笔记 frontmatter 加 `archived: YYYY-MM-DD`，并在文首加一行归档原因。
4. `_archive/` 内的笔记**不计入** index.md 的 12 篇阈值。
5. 参考触发标准（自行判断）：技术栈过时、被新笔记完全取代、内容长期失效。

### 六、收件箱规则

1. 一切"现在没想好放哪"的内容先进 `_inbox/`，宁可进收件箱也不要在正式目录留碎片。
2. **处理节奏**：攒到 3–5 篇就清一次。不要等"每周"，也不要攒到几十篇——单篇处理成本低，成批处理反而要重新回忆当时的上下文。
3. **清一次的动作**：先搜关键词看有没有同主题 → 有就**追加**进已有笔记，没有才新建（新建时至少加一条 `[[双链]]`）→ 确认无引用后删除原件。
4. **从公司电脑搬来的资料，入库前必做脱敏检查**：删除内部文档编号（`EKB` / `DOC` / `EDOC` / `topic`）、内网域名与链接、项目代号、客户名称、真实 IP 与设备序列号。能在外网直接访问的公开链接可以保留。
5. `_inbox/` 内不建子目录，保持浅平。
