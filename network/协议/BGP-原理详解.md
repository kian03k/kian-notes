---
tags: [network, bgp, 路由协议]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# BGP 原理详解

> AS 之间的路径矢量协议：状态机、报文、属性、选路、RR 与生产环境常见问题。配套题库见 [[BGP-题库]]。

## 一、BGP 的定位

| 维度 | OSPF / ISIS | BGP |
|---|---|---|
| 类型 | 链路状态（IGP） | **路径矢量**（EGP） |
| 目标 | 域内**最优路径**、快速收敛 | 域间**策略可控**、稳定、海量路由 |
| 规模 | 几十到几千条 | 百万条（全球路由表） |
| 收敛 | 秒级 | 分钟级 |
| 核心诉求 | 快 | **稳，不能乱翻** |

一句话：**OSPF 解决"怎么走最快"，BGP 解决"允许走哪、走哪条更符合策略"。** 所以 BGP 的一切设计都偏向稳定与可控，而不是快。

## 二、四种报文

| 报文 | 作用 | 频率 |
|---|---|---|
| **Open** | 建邻居，协商版本、AS 号、Hold Time、能力（MP-BGP、Route-Refresh、4 字节 AS） | 一次 |
| **Keepalive** | 保活 | 默认 **60s**（Hold Time 的 1/3） |
| **Update** | 宣告路由 / 撤销路由，携带路径属性 | 按需 |
| **Notification** | 报错并断邻居 | 出错时 |
| （Route-Refresh） | 请求对端重发路由（软重置用） | 按需，属能力协商 |

**Hold Time 默认 180s**，Keepalive 60s。三个 Keepalive 没收到就断邻居 —— 这就是 BGP 感知故障慢的根本原因（实测最坏 180s 才断）。

**TCP 端口 179**，BGP 跑在 TCP 上：
- 好处：不用自己做重传、排序、确认
- 坏处：**TCP 半开连接问题**——一端重启后，另一端可能还认为连接活着（要等 Hold Time 到期），造成路由黑洞

## 三、状态机（必考）

`Idle → Connect → Active → OpenSent → OpenConfirm → Established`

| 状态 | 做什么 | 卡在这里的常见原因 |
|---|---|---|
| **Idle** | 初始态，等待 Start 事件 | 没有可用路由到对端 / 配置未完成 |
| **Connect** | 发起 TCP 连接（SYN_SENT） | 连接被拒、路由不可达 |
| **Active** | TCP 连接**失败**，等待重试 | **最常见的"连不上"**：对端没配邻居、ACL 挡了 179、路由不可达、AS 号错 |
| **OpenSent** | 已发 Open，等对端 Open | 对端不可达 / 版本或能力不匹配 |
| **OpenConfirm** | 收到 Open，等 Keepalive | 认证失败、Hold Time 协商失败 |
| **Established** | 邻居建立，开始交换路由 | 目标状态 |

**关键认知：`Active` 不是"正在努力连接"，而是"连接失败了在等重试"。** 很多人看到 Active 以为是进行中，其实是坏消息。真正进行中的是 Connect。

排障口诀：
- 一直 **Active/Connect** → 传输层问题（路由、ACL、端口、认证）
- 能到 **OpenSent** 然后掉 → 是 BGP 层问题（AS 号、认证、Router ID 冲突）
- 到 **Established** 但没有路由 → 是策略问题（filter、next-hop、同步）

## 四、iBGP vs eBGP（核心区别）

| | iBGP | eBGP |
|---|---|---|
| AS 号 | 相同 | 不同 |
| 默认 TTL | 255 | **1**（需 `peer ebgp-max-hop` 才能多跳） |
| Next-Hop | **不修改** | **改为自己** |
| AS_Path | 不变 | 追加自身 AS 号 |
| 环路防止 | 靠 RR / 全互联 + 水平分割 | AS_Path |
| 路由传播 | **只传给自己的 iBGP 邻居一次**（水平分割） | 传给所有 eBGP 邻居 |

**iBGP 的水平分割规则**：从 iBGP 邻居学到的路由，**不会再传给其他 iBGP 邻居**。这是为了防环（因为 iBGP 内部没有 AS_Path 变化）。后果是 n 台 iBGP 路由器需要 n(n-1)/2 条连接——所以才需要 **RR（路由反射器）**。

**eBGP 的 TTL=1** 意味着 eBGP 邻居必须直连（或配 max-hop）。这是设计上的约束，避免跨多跳建 eBGP 邻居带来的复杂性。

## 五、Update 报文与路径属性

**Update 报文结构**：
```
Withdrawn Routes Length
Withdrawn Routes（撤销的网段）
Total Path Attribute Length
Path Attributes（属性）
NLRI（Network Layer Reachability Information，宣告的网段）
```

**四大类属性**：

| 类别 | 含义 | 属性 |
|---|---|---|
| 公认必遵 | 每条路由都必须带，不认识就报错 | Origin、AS_Path、Next_Hop |
| 公认自决 | 可以不带，不认识也能处理 | Local_Pref、Atomic_Aggregate |
| 可选过渡 | 可以不认识，但要传给邻居 | Aggregator、Community |
| 可选非过渡 | 不认识就丢弃，不传 | MED、Cluster_List、Originator_ID |

**重点属性逐个说**：

| 属性 | 作用 | 关键细节 |
|---|---|---|
| **Origin** | 路由来源 | i（IGP，最优先）> e（EGP）> ?（Incomplete，重分布来的）。**几乎不影响实际选路**，因为基本都是 ? 或 i |
| **AS_Path** | 经过的 AS 列表 | 防环（看到自己的 AS 就丢弃）+ 选路（**短优先**）。可做 AS_Path 过滤、AS_Path  prepend 影响入向选路 |
| **Next_Hop** | 下一跳 | eBGP 改为自己；iBGP 不改 → **这是 iBGP 的经典坑**：eBGP 边界学到的路由传给 iBGP 邻居时下一跳还是外部地址，内部路由器不可达 → 需要 `peer next-hop-local` |
| **Local_Pref** | 本地优先级，**只在 iBGP 内传** | 默认 100，**大者优**。用于"我要从哪个出口出去"，是控制**出向**流量的主武器 |
| **MED**（Multi-Exit Discriminator） | 告诉**相邻 AS** 从哪个入口进来 | 默认 0，**小者优**。用于控制**入向**流量，但只在相邻 AS 之间有效，跨 AS 会丢 |
| **Community** | 路由标记（32 位，可多个） | 用于打标签做策略、控制传播范围（no-export、no-advertise、internet） |
| **Originator_ID / Cluster_List** | RR 专用防环 | 见下节 |

> Local_Pref 控制出向，MED 控制入向 —— 记住这一句：**"我要出去"用 Local_Pref，"请从这进来"用 MED**。

## 六、BGP 选路规则（华为 13 条，必背顺序）

优先级从高到低，**逐条比较，一旦分出胜负就停**：

1. **优选 Local_Pref 最大** 的路由
2. **优选本地始发**（自己 network 宣告 / import 引入）的路由
3. **优选 AS_Path 最短**
4. **优选 Origin 最小**（i > e > ?）
5. **优选 MED 最小**
6. （华为）优选 **eBGP** 优于 iBGP
7. 优选**到 Next_Hop 的 IGP 开销最小**
8. （华为）优选 **Cluster_List 最短**
9. （华为）优选 **Router ID 最小**的对等体宣告的路由
10. 优选 **对等体地址最小** 的路由
11. （华为）优选 **本地优先级最高的对等体**（peer 上配的 priority）
12. 优选**较短 Cluster_List** 的（部分实现）
13. 优选**较老**的路由（避免震荡）

**面试答法**（不要背 13 条，讲骨架）：

> 先看策略类的：Local_Pref → 本地始发 → AS_Path → Origin → MED；再看拓扑类的：eBGP 优于 iBGP、IGP 开销、Router ID；最后是稳定性的：老路由优先。核心思想是**先策略后拓扑最后求稳定**。

**两个常被追问的点**：

- **AS_Path 和 Local_Pref 谁先？** Local_Pref 先。所以同一台路由器上，Local_Pref 可以压过更短的 AS_Path。
- **MED 为什么不跨 AS 传？** MED 是"相邻 AS 之间的建议"，设计上只在一个 AS 边界有意义。如果跨 AS 传播，远端 AS 的 MED 会干扰本 AS 的选路，所以默认不传（`compare-different-as-med` 可打开，但慎用）。

## 七、路由反射器 RR

**为什么需要**：iBGP 水平分割导致必须全互联，n 台设备需要 n(n-1)/2 条邻居，规模一大就没法维护。

**RR 的做法**：选一台（或多台）做反射器，Client 只和 RR 建邻居，RR 把从 Client 学到的路由**反射**给其他 Client 和其他 iBGP 邻居，从而打破水平分割。

**两个防环属性**：

- **Originator_ID**：RR 反射时打上**原始路由器的 Router ID**。如果一台路由器收到自己 Originator_ID 的路由 → 丢弃（防环）
- **Cluster_List**：RR 反射时追加自己的 Cluster ID。收到含自己 Cluster ID 的路由 → 丢弃（防多 RR 之间的环）

**RR 的三种对等体**：

| 关系 | 从这学到的路由传给 |
|---|---|
| Client → | 所有 Client + 所有非 Client |
| 非 Client → | 只传给 Client（不传给其他非 Client） |
| eBGP → | 所有 |

**Cluster 设计要点**：

- 同一 Cluster 内多个 RR 做冗余（Client 同时连两个 RR）
- Cluster ID 默认用 RR 的 Router ID，多 RR 时要**手工配同一个 Cluster ID**，否则防环失效
- RR 不是必须成对，但要考虑单点故障

## 八、路由聚合与过滤

**聚合**：`aggregate` 会生成一条聚合路由，同时**默认携带 Atomic_Aggregate** 属性（表示"原始明细被聚合了，路径信息不完整"）。

```
bgp 65001
 aggregate 10.0.0.0 255.255.0.0 detail-suppressed    # 只发聚合，不发明细
 aggregate 10.0.0.0 255.255.0.0 suppress-policy xxx  # 抑制部分明细
```

**为什么聚合后可能出环**：如果聚合发生在 AS 边界，而明细路由的 AS_Path 里有本 AS 号，聚合后 AS_Path 会变短甚至为空，导致环路。解决：`as-set`（用 `{}` 记录所有明细的 AS 号）。

**常用过滤工具**：

| 工具 | 用途 |
|---|---|
| `filter-policy` | 过滤**路由表**（不发也不收） |
| `peer route-policy` | 对某个邻居做**入向/出向**策略（能改属性） |
| `peer filter-policy` | 对某个邻居做纯过滤（ACL/前缀列表） |
| `ip ip-prefix` | 前缀列表，比 ACL 精确（能匹配掩码长度） |
| `route-policy` | 组合条件 + 动作（permit/deny + 改属性） |

**前缀列表 vs ACL 的区别**（常考）：ACL 只能匹配网络地址和通配符，无法精确匹配掩码；`ip ip-prefix` 可以写 `10.0.0.0 8 less-equal 24`（匹配 10.0.0.0/8 到 /24 的所有前缀），这是 BGP 过滤的正确工具。

## 九、生产环境的六个真实坑

**1. Next-Hop 不可达（iBGP 经典坑）**
eBGP 边界路由器把路由传给 iBGP 邻居时，下一跳还是外部地址。如果内部路由器没有到那个地址的路由，路由就是"可用但不通"（valid 但不 best / best 但 forwarding 黑洞）。解决：`peer x.x.x.x next-hop-local`。

**2. TCP 半开（Half-Open）**
一端重启，另一端还认为 Established，期间路由继续通告但不通。解决：开 BFD、`peer timer` 调小、`peer valid-ttl-hops`。

**3. 路由震荡**
一条链路闪断闪通，BGP 反复撤销/加回，CPU 飙高。解决：`dampening`（惩罚机制）、BFD + `route dampening` 配合。

**4. BGP 与 IGP 不同步（路由黑洞）**
BGP 宣告了路由，但内部 IGP 没有到达对端的路径。数据包到边界路由器后被丢弃。这是所有 BGP 排障必查项：**先确认 IGP 里到 Next-Hop 有路**。

**5. 收敛慢**
默认 Hold 180s，故障感知极慢。优化：
```
peer x.x.x.x bfd enable
peer x.x.x.x timer keepalive 10 hold 30
peer x.x.x.x connect-interface LoopBack0
```
注意调小定时器会增加 CPU，大规模时要权衡。

**6. 4 字节 AS 号兼容**
旧设备只支持 2 字节 AS（最大值 65535）。AS 号超过 65535 时，需要 4 字节 AS 能力协商，不支持的设备会看到 23456（AS_TRANS）。排查时看到 23456 就是这个问题。

## 十、常用配置（华为）

```
bgp 65001
 router-id 1.1.1.1
 peer 10.0.0.2 as-number 65002
 peer 10.0.0.2 description To-Core
 peer 10.0.0.2 ebgp-max-hop 2
 peer 10.0.0.2 connect-interface LoopBack0
 peer 10.0.0.2 bfd enable
 peer 10.0.0.2 timer keepalive 10 hold 30
 peer 10.0.0.2 route-policy RP-IN import
 peer 10.0.0.2 route-policy RP-OUT export
 #
 ipv4-family unicast
  network 192.168.1.0 255.255.255.0
  aggregate 10.0.0.0 255.0.0.0 detail-suppressed
  peer 10.0.0.2 enable
  peer 10.0.0.2 next-hop-local        # iBGP 场景
```

**注意 `network` 与 `import-route` 的区别**（高频考点）：
- `network`：必须是**路由表里已存在且精确匹配**的路由，Origin 为 **i**
- `import-route`：从其他协议引入，Origin 为 **?**
- `network` 更精确安全；`import-route` 会引入一大堆不想要的路由，必须配合 filter-policy

## 十一、排障命令速查

```
display bgp peer                          # 邻居状态
display bgp peer verbose                  # 详细（含 timer、能力协商）
display bgp routing-table                 # BGP 路由表
display bgp routing-table 10.1.1.0        # 单条路由详情（看属性）
display bgp routing-table peer x.x.x.x advertised-routes   # 我给对方发了什么
display bgp routing-table peer x.x.x.x received-routes     # 对方给我发了什么（需 soft-reconfig）
display bgp routing-table network          # 按网段查
display bgp error                          # 错误统计
display tcp status                         # 看 179 端口连接状态
reset bgp x.x.x.x                          # 硬重置（断邻居）
refresh bgp x.x.x.x import/export          # 软重置（需 Route-Refresh 能力）
```

**排障顺序**：`display bgp peer`（状态）→ `display tcp status`（连接）→ `ping -a 源地址 对端`（路由可达）→ `advertised-routes / received-routes`（策略）→ `display ip routing-table`（是否入选）。

**一个高频陷阱**：`ping` 通但 BGP 建不起来——因为 BGP 用**出接口地址**发起 TCP，而 `ping` 默认用出接口地址的源地址不同（尤其 LoopBack 建邻居时必须 `connect-interface`）。

## 十二、设计要点

1. **iBGP 用 LoopBack 建邻居**：`peer x.x.x.x connect-interface LoopBack0`，多路径冗余
2. **RR 至少两台**，同一 Cluster ID，Client 双连
3. **Next-Hop 处理**：iBGP 场景必须 `next-hop-local`，否则黑洞
4. **开 BFD**：BGP 默认感知太慢，生产必须加快速检测
5. **路由策略先严后松**：入向先收紧（只收想要的），出向再精细；默认拒绝
6. **聚合要防环**：跨 AS 聚合加 `as-set`
7. **别用 BGP 传 IGP 该传的东西**：数据中心内部用 OSPF/ISIS，BGP 只做 DC 出口和 EVPN 控制面

## 参考

- RFC 4271（BGP-4）、RFC 4456（RR）、RFC 1997（Community）、RFC 8092（Large Community）
- 华为 S 系列交换机产品文档 · BGP 配置指南
