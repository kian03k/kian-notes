---
tags: [network, bgp, 面试题库]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# BGP 题库

> 45 道高频题，四级分层。原理细节见 [[BGP-原理详解]]。

**BGP 面试的规律**：基础题问"是什么"，进阶题问"为什么这么设计"，深挖题一定问 **选路顺序** 和 **RR 防环**。选路顺序答不上来基本就废了，其他都可以谈。

---

## L1 基础必答（16 题）

### 1. BGP 是什么协议，为什么需要它？

**答**：BGP 是**路径矢量**的域间路由协议，跑在 TCP 179 上。IGP 解决"域内怎么走最快"，BGP 解决"域间允许走哪、哪条更符合策略"。

**为什么要它**：① 互联网由无数 AS 组成，需要一个能承载百万级路由、支持策略控制的协议 ② IGP 扛不住这个规模（LSDB 会爆炸） ③ 需要 AS 级别的环路防护和策略表达。

### 2. BGP 四种报文？

Open（建邻居、协商能力）、Keepalive（保活）、Update（宣告/撤销路由）、Notification（报错断开）。

**加分点**：还有 Route-Refresh（软重置，属能力协商）。

### 3. BGP 的定时器？

Keepalive 默认 **60s**，Hold Time 默认 **180s**（3 个 Keepalive）。三个 Keepalive 没收到就断邻居。

**这就是 BGP 感知故障慢的根本原因**——最坏 180s 才发现对端挂了。

### 4. BGP 状态机？

`Idle → Connect → Active → OpenSent → OpenConfirm → Established`

**关键点**：**Active 不是"正在连接"，而是"连接失败了在重试"**。Connect 才是正在连。

### 5. 邻居一直 Active 是什么原因？

传输层不通。① 路由不可达（到对端地址没路由） ② 对端没配邻居 ③ ACL / 防火墙挡了 179 ④ 对端 AS 号配错 ⑤ 对端端口没监听。

**排查顺序**：`display bgp peer` → `display tcp status` → `ping -a 源地址 对端`。

### 6. iBGP 和 eBGP 的区别？

| | iBGP | eBGP |
|---|---|---|
| AS | 相同 | 不同 |
| TTL | 255 | **1**（要 max-hop 才能多跳） |
| Next-Hop | **不改** | **改为自己** |
| AS_Path | 不变 | 追加自己 AS |
| 传播 | 只传一次（水平分割） | 传所有 |

### 7. BGP 为什么跑在 TCP 上？

好处：不用自己实现重传、排序、确认、窗口，可靠性交给 TCP。
坏处：**TCP 半开问题**——一端重启，另一端可能还认为连接活着，要等 Hold Time 到期，期间路由继续通告但不通。

**加分点**：所以说"BGP 天然有黑洞风险"，需要 BFD 或调小 timer 兜底。

### 8. 什么是 AS？AS 号范围？

自治系统（Autonomous System），由单一机构管理、使用统一路由策略的网络集合。AS 号早期 2 字节（1–65535），现在 4 字节。

**私有 AS 号**：64512–65534（2 字节）、4200000000–4294967294（4 字节）。

### 9. BGP 的四大类路径属性？

- **公认必遵**：Origin、AS_Path、Next_Hop（必须带，不认识就报错）
- **公认自决**：Local_Pref、Atomic_Aggregate（可带可不带）
- **可选过渡**：Aggregator、Community（不认识也要传下去）
- **可选非过渡**：MED、Cluster_List、Originator_ID（不认识就丢）

### 10. 什么是 Next-Hop 属性？iBGP 为什么会有坑？

Next-Hop 是"到达这条路由的下一跳地址"。eBGP 会把 Next-Hop 改为自己，**iBGP 不改**。

**坑**：AS 边界路由器从 eBGP 学到的路由，传给 iBGP 邻居时下一跳还是外部地址；内部路由器没有到那个地址的路由 → 路由"可用但不通"。

**解决**：`peer x.x.x.x next-hop-local`。

### 11. Local_Pref 和 MED 分别管什么？

- **Local_Pref**（本地优先级）：控制**出向**流量，只在 iBGP 内传，默认 100，**大者优**
- **MED**：告诉**相邻 AS** 从哪个入口进来，控制**入向**流量，默认 0，**小者优**

**一句话**：我要出去用 Local_Pref，请你从这进来用 MED。

### 12. Community 有什么用？

给路由打标记（32 位，可打多个），用于：① 做策略（按标记过滤/改属性） ② 控制传播范围。

**几个公认 Community**：`no-export`（不传出本 AS）、`no-advertise`（不传给任何邻居）、`internet`（可传全网）。

### 13. AS_Path 的两个作用？

① **防环**：收到含自己 AS 号的路由直接丢弃 ② **选路**：长度短的优先。

**还能干什么**：AS_Path prepend（重复自己的 AS 号，让路径看起来更长）来影响入向流量。

### 14. 什么是路由黑洞？BGP 里怎么产生？

路由黑洞 = 控制面有路由、数据面转发不通。

BGP 里的经典场景：BGP 宣告了一条路由，但 IGP 里没有到达 Next-Hop 的路径。数据包到边界路由器后查不到下一跳，被丢弃。

**排查**：先确认 IGP 里到 Next-Hop 有路由，再看 FIB 里有没有这条。

### 15. BGP 为什么收敛慢？

① Hold Time 180s，故障感知慢 ② 路径矢量逐跳传播，一次变化要传遍全网 ③ 默认不开启增量更新优化 ④ 大规模路由表下 CPU 和内存压力。

**优化**：BFD、调小 timer、Route-Refresh、BGP GR（优雅重启）、Add-Path。

### 16. BGP 的 `network` 和 `import-route` 有什么区别？

- **`network`**：必须是**路由表里已存在且精确匹配**的路由，Origin 为 **i**
- **`import-route`**：从其他协议引入，Origin 为 **?**

**答法**：`network` 更精确安全（指定的才发）；`import-route` 会引入一大堆，必须配 filter-policy。

---

## L2 进阶（16 题）

### 17. 完整讲一遍 BGP 选路顺序

按优先级（逐条比较，分出胜负就停）：

1. **Local_Pref 大者优**
2. **本地始发**（自己 network / import 的）
3. **AS_Path 短者优**
4. **Origin 小者优**（i > e > ?）
5. **MED 小者优**
6. **eBGP 优于 iBGP**
7. **到 Next-Hop 的 IGP 开销小者优**
8. Cluster_List 短者优
9. Router ID 小者优
10. 对等体地址小者优
11. （最后）老路由优先，避免震荡

**答题建议**：别死背 13 条，讲骨架——"先策略（Local_Pref → 本地始发 → AS_Path → Origin → MED），再拓扑（eBGP vs iBGP → IGP 开销 → Router ID），最后求稳定"。然后补充"如果面试官要细节，我可以逐条说"。

### 18. 为什么 Local_Pref 排在 AS_Path 前面？

因为 Local_Pref 是**本地管理员的意图表达**，优先级必须高于客观路径长度。管理员说"我就要从这条出口出去"，即使 AS_Path 更长也要走——这才是策略路由的意义。

### 19. MED 为什么默认不跨 AS 传播？

MED 是"相邻 AS 之间的建议"，设计上只在一个 AS 边界有意义。如果跨 AS 传播，远端 AS 的 MED 会干扰本 AS 的选路，造成不可控。

**`compare-different-as-med`** 可以打开，但生产慎用（容易出意外）。

### 20. 什么是 BGP 路由反射器（RR）？为什么需要？

iBGP 的水平分割规定"从 iBGP 邻居学到的路由不再传给其他 iBGP 邻居"，导致 n 台设备要 n(n-1)/2 条邻居，规模一大没法维护。

RR 打破水平分割：Client 只和 RR 建邻居，RR 把学到的路由反射给其他 Client。

### 21. RR 怎么防环？

两个属性：

- **Originator_ID**：反射时打上**原始路由器**的 Router ID。收到含自己 Originator_ID 的路由 → 丢弃
- **Cluster_List**：反射时追加 RR 的 Cluster ID。收到含自己 Cluster ID 的路由 → 丢弃（防多 RR 之间的环）

### 22. RR 的三种对等体关系，路由怎么传？

- **从 Client 学到** → 传给所有 Client + 所有非 Client（eBGP 也传）
- **从非 Client 学到** → **只传给 Client**（不传给其他非 Client）
- **从 eBGP 学到** → 传给所有

**记忆**："Client 是亲儿子，非 Client 是外人，外人的话只告诉亲儿子。"

### 23. 多台 RR 怎么配？Cluster ID 要注意什么？

- 同一 Cluster 内两台 RR 做冗余，Client 同时连两个 RR
- **多台 RR 必须手工配同一个 Cluster ID**，否则 Cluster_List 防环失效
- 默认 Cluster ID 用 RR 的 Router ID，会导致两台 RR 认为自己是不同 Cluster

### 24. 什么是 BGP 联盟（Confederation）？和 RR 比哪个好？

**联盟**：把一个大 AS 拆成多个子 AS（Sub-AS），内部跑 eBGP，对外看起来还是一个 AS。

| | RR | 联盟 |
|---|---|---|
| 配置复杂度 | 简单 | 复杂（要配子 AS） |
| 对邻居的影响 | 无 | 需要所有设备支持 |
| 现状 | **主流** | 基本没人用了 |

**答法**：现在都用 RR，联盟是历史方案。

### 25. BGP 路由聚合要注意什么？

① `aggregate` 默认会带 Atomic_Aggregate 属性 ② **可能产生环路**：如果聚合点在 AS 边界，聚合后的 AS_Path 会变短甚至为空，需要 `as-set`（用 `{}` 记录明细的 AS 号） ③ `detail-suppressed` 只发聚合不发明细，可能漏掉明细里的部分可达性 ④ 聚合前要确认明细网段连续。

### 26. 前缀列表和 ACL 的区别？BGP 过滤用哪个？

**ACL 只能匹配网络地址和通配符，无法精确匹配掩码长度**。比如 `10.0.0.0/8` 和 `10.0.0.0/24` 在 ACL 里难区分。

**`ip ip-prefix`** 可以写 `10.0.0.0 8 less-equal 24`（匹配 /8 到 /24 的所有前缀），这才是 BGP 过滤的正确工具。

### 27. BGP 怎么做入向和出向的流量控制？

- **出向（我要从哪出去）**：改 **Local_Pref**（在 import 方向改）、或用 `preferred-value`（华为私有，只在本机生效，优先级最高）
- **入向（请从哪进来）**：AS_Path prepend、发 Community 让对端改 Local_Pref、改 MED（仅相邻 AS 有效）

### 28. 什么是 BGP GR（Graceful Restart）？

设备重启（控制面重启）时，转发面保持，邻居不立即断，等设备恢复后重新同步路由，避免重启期间路由全撤导致业务中断。

**关键点**：需要邻居也支持（能力协商），并且转发面真的没断（硬件转发）。

### 29. BGP 的 Add-Path 是什么？

默认 BGP 对同一目的只选**一条最优**路由发给邻居。Add-Path 允许发**多条**路径，让邻居有更多备份选择，加快收敛、支持多路径负载。

**场景**：RR 场景下，Client 只收到 RR 选的一条，如果这条路径故障要等 RR 重新收敛。Add-Path 可以让 RR 发多条。

### 30. eBGP 为什么要配 `ebgp-max-hop`？

eBGP 默认 TTL=1，意味着邻居必须直连。用 LoopBack 建 eBGP 邻居（多跳）时，必须配 `ebgp-max-hop 2`（或更大）。

**注意**：这是安全设计——限制 eBGP 只在直连间建立，避免跨多跳的复杂性。

### 31. BGP 邻居建立不起来，怎么一步步排查？

1. `display bgp peer` → 看状态（Active/Connect = 传输层；OpenSent = BGP 层）
2. `display tcp status` → 看 179 端口有没有连接
3. `ping -a 源地址 对端地址` → **必须指定源**，因为 BGP 用 connect-interface 指定的地址发起
4. 检查 ACL / 防火墙
5. 检查 AS 号、认证、Router ID 冲突
6. `display bgp error` 看错误统计

### 32. BGP 起来了但没有路由，怎么查？

① `display bgp routing-table peer x.x.x.x received-routes` 看对端发了什么 ② `display bgp routing-table peer x.x.x.x advertised-routes` 看我发了什么 ③ 检查 route-policy / filter-policy ④ 检查 Next-Hop 是否可达 ⑤ 检查 `display ip routing-table` 里有没有入选（可能被其他协议抢了）。

---

## L3 深挖（9 题）

### 33. 为什么不建议用 BGP 传 IGP 该传的东西？

① BGP 收敛慢（分钟级），IGP 是秒级 ② BGP 路由表大，设备资源压力大 ③ IGP 的拓扑信息更完整（BGP 只传前缀） ④ 故障感知慢。

**正确分工**：DC 内部用 OSPF/ISIS 或 eBGP（小规模），BGP 只做出口和 EVPN 控制面。

### 34. 数据中心用 eBGP 做 Underlay 有什么好处？

① 规模扩展好（只传前缀，LSDB 不膨胀） ② 策略可控 ③ 故障域小 ④ ECMP 支持好 ⑤ 和 EVPN 天然配套（同一个 BGP 进程） ⑥ AS 号规划清晰，天然防环。

**追问**：AS 号怎么规划？→ 每台 Leaf 一个独立 AS（或几台一个），Spine 统一 AS；或者 Spine 每台独立 AS。关键是**同一台设备不接收含自己 AS 号的路由**，天然防环。

### 35. BGP 邻居频繁震荡怎么处理？

① 查底层：接口有没有闪断、光模块误码 ② `display logbuffer` 看有没有 TCP 重传 ③ 开 BFD 快速感知 ④ 配 `dampening`（路由惩罚） ⑤ 检查 CPU/内存是否打满导致 Keepalive 超时。

**加分点**："BGP 震荡十有八九是底层链路问题，别急着改 BGP 参数"——这是实战经验。

### 36. BGP 的 TCP 半开问题怎么发现和避免？

**发现**：一端重启，另一端 `display bgp peer` 还是 Established，但路由不通；`display tcp status` 看连接状态异常。

**避免**：① 开 BFD ② 调小 keepalive/hold（如 10/30） ③ `peer valid-ttl-hops` 校验 TTL。

### 37. 什么是 BGP 的 `preferred-value`？和 Local_Pref 的区别？

`preferred-value` 是**华为私有**属性，**只在本机生效，不传给任何邻居**，优先级比 Local_Pref 更高（在选路最前面）。

**用途**：本机强制选某条路，不影响别人。

### 38. 大规模 BGP 网络怎么做路由收敛优化？

① BFD ② 调小 timer ③ BGP GR ④ Add-Path ⑤ 路由聚合减少条目 ⑥ 分层 RR（一级 RR → 二级 RR） ⑦ 前缀抑制/抖动抑制 ⑧ 硬件转发 + 大表项。

### 39. BGP 路由策略配错了会导致什么后果？怎么防？

**后果**：① 路由泄漏（把不该发的发出去） ② 路由黑洞（该发的没发） ③ 环路。

**防**：① 默认拒绝（route-policy 最后一条 deny） ② 变更前用 `display bgp routing-table peer x advertised-routes` 验证 ③ 灰度发布（先在一台上改） ④ 变更窗口 + 回滚预案。

### 40. 一个 AS 有两个出口，一条是专线一条是互联网，怎么做流量规划？

① **出向**：专线方向 Local_Pref 调高（150），互联网默认 100 ② **入向**：让对端改 Local_Pref（发 Community）或自己 AS_Path prepend ③ **备份**：专线故障时 Local_Pref 失效，自动走互联网 ④ **分流**：用 route-policy 按目的网段分（比如内网走专线，上网走互联网）。

### 41. EVPN 场景下 BGP 起什么作用？

EVPN 用 **MP-BGP（AFI 25 / SAFI 70）** 作为控制面，传递 MAC/IP 映射（Type-2）、BUM 隧道信息（Type-3）、ES 信息（Type-4）、IP 前缀（Type-5）。

**关键**：EVPN 邻居通常是 **iBGP**，Underlay 用 eBGP 或 OSPF。这两层 BGP 是独立的（不同 address-family）。

---

## L4 场景题（4 题）

### 42. 割接 BGP 邻居时怎么保证业务不中断？

① 确认有冗余路径（先看 `display bgp routing-table` 的备份路径） ② 用 **软重置**（`refresh bgp`）而不是 `reset bgp` ③ 如果是策略变更，先在测试环境验证 ④ 分批操作 ⑤ 改完立即 `display bgp routing-table peer ... advertised-routes` 验证 ⑥ 准备回滚。

### 43. 客户说"BGP 邻居是 Established，但业务不通"，你怎么查？

1. `display bgp routing-table` 看目标网段在不在、是不是 best
2. `display ip routing-table` 看有没有入选（可能被 IGP 或静态抢了）
3. `display fib 目标地址` 看转发面有没有
4. 如果路由有但不通 → 查 **Next-Hop 可达性**（IGP 里到 Next-Hop 有没有路）
5. 查 ACL / 策略 / 安全组
6. 分段抓包定位断点

**这个顺序的价值**：从控制面到数据面逐层收窄，每一步都有明确判据。

### 44. 两条链路，一条主用一条备份，怎么保证切换快？

① **BFD**（毫秒级检测） ② Local_Pref 拉开差距（主 150 / 备 100） ③ 或 AS_Path prepend 做备份 ④ 确保备份路径的下一跳 IGP 可达（否则切过去也不通） ⑤ 验证：手动 shutdown 主链路，测切换时间和业务影响。

### 45. 你怎么理解 BGP 的"策略优先于拓扑"？

BGP 选路的第一梯队是 Local_Pref、本地始发、AS_Path、MED——**全是人为可控的属性**，而 IGP 开销、Router ID 排在后面。

这意味着：**BGP 网络的行为主要由管理员的策略决定，而不是物理拓扑**。所以 BGP 排障时，"路由为什么走这条"的答案往往在策略配置里，而不是在链路带宽里。

**这句话能体现你理解 BGP 的设计哲学**，比背 13 条选路规则更有说服力。

---

## 速记卡

- 状态机：Idle → Connect → Active → OpenSent → OpenConfirm → Established（**Active = 失败重试**）
- Keepalive 60s / Hold 180s → 感知故障慢，必须配 BFD
- iBGP：TTL 255、不改 Next-Hop、不转发（水平分割）
- eBGP：TTL 1、改 Next-Hop、加 AS_Path
- 选路骨架：Local_Pref → 本地始发 → AS_Path → Origin → MED → eBGP>iBGP → IGP 开销 → Router ID → 老路由
- RR 防环：Originator_ID + Cluster_List
- Local_Pref 管出向，MED 管入向
- iBGP 必配 `next-hop-local`
- BGP 引入 OSPF 必须过滤 + 打 tag
