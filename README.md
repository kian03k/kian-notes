---
tags: [index]
created: 2026-09-08
updated: 2026-11-15
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
│   ├── 题库/            # 题库与备考：分级题库 + HCIP-811 索引 + 考点速查
│   ├── 故障排查/        # 实际调测问题排查记录（ping -a 系列等）
│   └── Windows路由配置.md
└── English/             # 英语（保留一级目录，内容多了再划分子目录）
```

## 常用入口

- Python：[cs/dev/python/index.md](cs/dev/python/index.md)（七层：语言基础 / 数据处理 / 文件操作 / 网络 / 桌面界面 / 日志异常 / 环境交付）
- Git：[cs/dev/git/index.md](cs/dev/git/index.md)（全链路教程 + 配置 + 场景化操作）
- 开发环境：[Python 环境搭建](cs/dev/python/env/setup/Python%20Env%20Setup.md)
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

**目录层级按语义需要决定，不用篇数卡。** 一个目录里只躺 1 篇也完全可以，只要它确实是一个独立分类；反过来，为了「凑够 3 篇」把不相干的内容塞进同一个桶，比空壳目录更糟。

唯一要避免的是**纯为分类而分类的深嵌套**——4 层目录里只躺 1 个文件（反例：`cs/os/windows/browser_apps/optimization_config/Q&A.md`），点进去还得记住路径，比平铺更难找。判断依据是「这个目录名能不能当检索词」，不是「这个桶里够不够几篇」。

例外：按「工具」或「职能」天然独立的目录（`tools/obsidian/`、`docs/template/`、`xxx/assets/`）即便只有 1 篇也合理。

例外二：**分类目录一律允许先建后长**。按技术方向或场景划分的子目录（如 `dev/python/excel/`、`dev/python/packaging/`）即使当前只有 1 篇也可以建——它承担的是长期分类锚点的作用，新笔记直接落进去即可。

以 `cs/dev/python/` 为例（**六个顶层分类，按「处理的是什么对象」划分**）：

```txt
python/
├── index.md      # 索引（我要干什么 → 看哪篇）
├── guide/        # 语言本身怎么写
│   ├── 01~04     # 主干，按序读（速查/函数进阶/面向对象/循环跳出）
│   └── advanced/ # 进阶深化（装饰器与 wraps / 参数传递 / 迭代器协议）
├── data/         # 打开某种内容 → 解析 → 改写 → 出图
│   ├── index.md  # 18 篇，超 12 篇阈值，自带子索引
│   ├── pandas/   # 表格数据处理（01~06 连号）
│   ├── excel/    # Excel / CSV 文件读写
│   ├── text/     # 字符串与正则
│   ├── charts/   # 出图
│   ├── media/    # 音视频处理（FFmpeg）
│   └── serialization/ # pickle 与压缩
├── files/        # 对文件本身动手（改名/去重/体积/监听）
│   └── paths/    # 路径与文件系统操作（pathlib / 遍历 / 建删目录 / 定位资源）
├── web/          # 跟浏览器和 HTTP 打交道（Flask / 抓取 / 反检测）
├── gui/          # 桌面窗口：控件、布局、长任务进度反馈
├── quality/      # 出错时看得见、运行时扛得住
│   ├── logging/    # 日志接入（00 总览 + 01~04）
│   └── exceptions/ # 异常处理
└── env/          # 从装环境到打包交出去
    ├── setup/      # 环境搭建（Windows / WSL2 / Linux）
    └── packaging/  # 打包分发
```

判断标准是「这篇该放哪个桶」，而不是「这个桶够不够 3 篇」。

### 二、index.md 触发条件

- 某个**二级主题**目录（如 `cs/dev/`、`cs/infra/`、`network/` 的子目录）下笔记数**超过 12 篇**时，创建该目录的 `index.md` 导航页。
- 12 篇以内靠目录浏览即可，不为索引而索引。
- `index.md` 只做链接导航（按子目录或主题分组），不写长篇内容。
- 计数口径：目录树内所有 `.md`，不含 `assets/` 资源、不含 `_archive/`、不含 `index.md` 自身。
- **当前已建索引**：`cs/dev/python/`（53 篇）、`cs/dev/git/`（20 篇）、`cs/ai/图像处理基础/`（10 篇，自带完整学习路线）、`network/`。接近阈值的：`network/题库/`（10 篇）、`network/协议/`（8 篇）。

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

### 七、标签规范

**标签只做文件夹做不到的事。** 当前 120 篇用 44 个标签，平均每篇不到 2 个，分三层。

#### 1. 领域标签（英文小写，与目录对应）

`network` `python` `docker` `git` `mysql` `linux` `windows` `ai` `web` `cpp` `java` `android` `markdown` `obsidian` `jetbrains` `algorithm` `architecture` `english` `personal` `inbox`

价值在于**跨目录聚合**：`#docker` 能一次捞出 `infra/docker/` 三个子目录加 `infra/database/` 里沾容器的笔记，`#mysql` 能同时命中 `infra/database/MySQL/` 和 `infra/docker/MySQL/`。单目录内独一份的领域标签（如 `#cpp`）属于可接受的冗余。

#### 2. 技术点子标签（`父/子` 形式）

- 数通：`network/bgp` `network/ospf` `network/vxlan` `network/evpn` `network/mlag` `network/roce` `network/qos` `network/ssh` `network/vrrp` `network/icmp` `network/ecmp`
- AI：`ai/opencv` `ai/pytorch` `ai/resnet` `ai/yolo`
- 其他：`web/vue` `java/maven` `python/flask`

规则：
- **只在同一技术点跨目录出现时才建**（如 `network/bgp` 同时命中 `协议/BGP-原理详解` 和 `题库/BGP-题库`）。
- **打了子标签就不再打父标签**。Obsidian 里 `tag:#network` 会自动带出所有 `network/*` 子标签（官方 0.10.3 起的行为），父标签重复打等于白占位置。
- 子标签引用时写全路径：`tag:#network/bgp`。

#### 3. 属性标签（中文，横切所有目录）

| 标签 | 含义 | 用途 |
|------|------|------|
| `踩坑` | 亲自排查/踩过并解决了 | 这是最值钱的一类，将来再遇到能直接复用 |
| `速查` | 命令、语法、参数清单 | 集中一处备查 |
| `题库` | 考试、面试题 | 与 `network/*` 正交 |
| `安装配置` | 装完就废的环境搭建 | 标记出来，将来批量评估哪些该归档 |
| `归档` | 旧版本内容，留档备查 | 配合 `_archive/` 使用 |
| `index` | 导航页 | 快速定位所有索引入口 |

#### 明确不打的标签

- **关键词**（`轮廓`、`loss曲线`、`迭代器`、`参数传递`）：全文搜索就能命中，打标签是重复劳动，还多一份维护成本。
- **同义词**（`排障`/`故障排查`、`OOP`/`面向对象`、`yolo`/`YOLO`）：一条概念只允许一个写法。
- **状态**（`draft`/`ok`）：用 frontmatter 的 `status` 字段，不要和标签双份维护。

#### 常用检索写法

| 目的 | 搜索框输入 |
|------|-----------|
| 某领域全部（含子标签） | `tag:#network` |
| 某个具体技术点 | `tag:#network/bgp` |
| 交集 | `tag:#python tag:#速查` |
| 排除 | `tag:#踩坑 -tag:#归档` |
| 找会过期的笔记 | `tag:#安装配置` |
| 表格化浏览 | Bases 里新建 base，用 tags 条件过滤 |

### 八、外部文档整理规范

> 对话记录、旧笔记、公司电脑搬来的资料落库时的固定流程。跟小柯说「按 README 第八节来」即可。

**1. 先校验，再落库。** 外部文档默认不可信，逐条核对技术结论，错误就地改正。

- 校验优先级：**实测 > 官方文档/标准 > 其他笔记交叉印证 > 个人经验**。
- 改动处用 `> 修正：原稿称 X，实测为 Y` 标注，保留可追溯性。
- 无法验证的内容标「未验证」，不与已验证内容并列陈述。
- 代码片段必须能跑，语法错误与 API 误用一律修掉。

**2. 归位。** 按第二节目录职责落位。

- 先搜关键词查重，同主题**追加**到已有笔记，不新建。
- 目录按「这个桶名能不能当检索词」判断，不按篇数判断。
- 落库后从 `_inbox/` 删除原件；新笔记至少加一条 `[[双链]]`。

**3. 行文。** 正式、书面化。

- 不保留对话口气（"非常好的问题""👏""稳如老狗"）。
- 结论先行，一段话讲清一个问题。
- 不用比喻做技术解释。
- 删掉排比、感叹、重复强调，只留有操作价值的信息。
