---
tags: [network, ospf, 面试题库]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# OSPF 题库

> 45 道高频题，按四级分层。每题给「标准答法 + 追问 + 加分点」。原理细节见 [[OSPF-原理详解]]。

**刷题策略**：L1 必须秒答（不打磕巴），L2 要能讲两分钟，L3 讲到自己做过的场景，L4 记结论和关键数字。

---

## L1 基础必答（18 题，要秒答）

### 1. OSPF 是什么协议，和 RIP 有什么区别？

**答**：OSPF 是链路状态协议，每台路由器收集全网链路信息组成 LSDB，用 SPF 算法自己算最短路径树；RIP 是距离矢量，只靠邻居告诉的距离，逐跳收敛。

**三个关键差异**：① OSPF 知道全网拓扑，RIP 只知道距离和方向 ② OSPF 收敛快、无环路，RIP 有环路风险（靠水平分割等机制治） ③ OSPF 用组播、支持分层区域，RIP 最多 15 跳、规模受限。

**追问**：那 OSPF 有什么缺点？→ 内存占（LSDB）、有 SPF 计算峰值、配置比 RIP 复杂。

### 2. OSPF 的五种报文？

Hello（发现邻居、选 DR）、DD（交换摘要）、LSR（请求）、LSU（携带完整 LSA）、LSAck（确认）。**加分点**：OSPF 自己实现可靠泛洪，靠 LSAck。

### 3. OSPF 邻居状态机有几个状态？

`Down → Init → 2-Way → ExStart → Exchange → Loading → Full`（NBMA 多一个 Attempt）。

### 4. 邻居一直卡在 Init 是什么原因？

**单向通信**：收到对方 Hello，但对方 Hello 的邻居列表里没有我。常见原因：光纤收发接反、单向 ACL、单向链路故障、一端是静默接口。

**追问**：怎么验证？→ 两端 `display ospf peer` 对比；抓包看 Hello 源地址和邻居列表。

### 5. 卡在 ExStart 是什么原因？

**MTU 不一致**（最常见）。ExStart 阶段协商主从和 DD 序列号，MTU 不同会导致 DD 报文被判错。

**答法**：两边 `display interface` 对比 MTU；应急可以 `ospf mtu-ignore`，但根因还是要统一 MTU。其次是 Router ID 冲突。

### 6. 邻居停在 2-Way 算正常吗？

**看角色**：DROther 之间停在 2-Way 是**正常的**（本来就是设计如此）；DR/BDR 和其他路由器之间必须是 Full，如果不是就是故障。

### 7. 为什么要选 DR/BDR？

广播网络上 n 台路由器全互联是 n(n-1)/2 个邻接关系，LSDB 同步和泛洪开销大。引入 DR 后只需 2n-2，且由 DR 代表网段生成 Type-2 LSA。

### 8. DR 怎么选出来的？会抢占吗？

先比优先级（默认 1，0 不参选），再比 Router ID（大者胜）。**不抢占**——DR 选出后，新来的高优先级设备不会顶掉它，除非 DR 失效。

**加分点**：这也是为什么生产环境要手工规划 Router ID 和 dr-priority。

### 9. BDR 有什么用？

DR 的备份。DR 挂了 BDR 立即接替，不用重新选举，避免收敛空窗。

### 10. OSPF 有哪几种 LSA？

Type1 Router（拓扑）、Type2 Network（广播网段，DR 产生）、Type3 Summary（区域间网段）、Type4 ASBR Summary（ASBR 位置）、Type5 AS External（外部路由）、Type7 NSSA External。

**记忆锚**：1/2 管拓扑，3/4 管区域间，5/7 管外部。

### 11. Type-3 LSA 是谁产生的？

ABR。它把本区域的 Type-1/2 算出来的路由，以 Type-3 的形式通告到其他区域。**注意 Type-3 描述的是"网段"，不是拓扑**，所以跨区域是距离矢量行为。

### 12. Type-4 有什么用？

告诉其他区域"ASBR 在哪里"。因为 Type-5 只带外部路由和 ASBR 的 Router ID，其他区域不知道这个 Router ID 怎么到达，所以需要 Type-4 指路。

### 13. ASBR 和 ABR 的区别？

ABR：接口跨多个区域（且至少一个连 Area 0），负责区域间路由。ASBR：引入外部路由的路由器。**一台设备可以同时是 ABR 和 ASBR**。

### 14. 为什么要分区域？

① 限制 LSDB 规模 ② 把拓扑变化挡在区域内，减少全网 SPF ③ 便于分层设计和汇总。

### 15. Stub 区域有什么特点？

不收 Type-4、Type-5（外部路由），ABR 下发一条默认路由代替。适合末端区域（只有一台出口）。

**追问**：Totally Stub 呢？→ 进一步不收 Type-3，只有一条默认路由，LSDB 最小、收敛最快。

### 16. NSSA 是什么？

Stub 的变体：**不收**其他区域的 Type-5，但**允许自己引入**外部路由（以 Type-7 形式）。用于"末端区域但有外部路由要注入"的场景。

**追问**：Type-7 怎么出去？→ 由 ABR 转成 Type-5（转换者是 Router ID 最大的 ABR）。

### 17. OSPF 的 cost 怎么算？

`cost = 参考带宽 / 接口带宽`，华为参考带宽默认 100Mbps，取整，最小为 1。

**坑**：默认参考带宽 100M，导致百兆以上接口 cost 全是 1，千兆和万兆等价。必须改 `bandwidth-reference`。

### 18. OSPF 支持 IPv6 吗？

支持，但用的是 OSPFv3（RFC 5340），是独立进程，不是 OSPFv2 的扩展。OSPFv3 用链路本地地址（FE80::/10）建邻居，Router ID 仍然是 32 位。

---

## L2 进阶（15 题，能讲两分钟）

### 19. 讲一下 OSPF 完整的建邻居过程

1. 接口使能 OSPF 后，周期性发 Hello（默认 10s），收到对端 Hello 进入 Init
2. 双方 Hello 里都有对方 → 2-Way
3. 广播网络先选 DR/BDR（等 40s，即 Dead Interval）
4. ExStart：协商主从（Router ID 大的是 Master），确定 DD 序列号
5. Exchange：互发 DD 摘要
6. Loading：发 LSR 请求自己没有的 LSA，对方用 LSU 回复
7. Full：LSDB 同步完成

**加分点**：DR 选举要等 40s，所以新接入一台路由器到 Full 一般要 40s 左右，这是正常现象，不是故障。

### 20. LSDB 同步完成后，路由是怎么算出来的？

以自己为根，把 Type-1 LSA 当作图的边（节点是路由器和网段），跑 Dijkstra，算出到每个节点的最短路径；把树上的叶子网段写进路由表，下一跳取树上第一个邻居，cost 是沿途出接口之和。

**追问**：Type-2 起什么作用？→ 描述广播网段（虚拟节点），SPF 计算时把它当作一个"伪节点"，这样同一网段内 n 台路由器不用两两建边。

### 21. OSPF 怎么防环？

**区域内**：SPF 算法本身无环（最短路径树）。
**区域间**：靠**区域结构**——所有非骨干区域必须通过 Area 0 互通，ABR 不会把从一个非骨干区域学到的 Type-3 再传回另一个非骨干区域（除非经过 Area 0）。这是防环的核心。
**外部路由**：Type-5 由 ASBR 产生，靠 Type-4 指路，也没有环（因为外部路由是单向注入）。

### 22. 为什么要规定非骨干区域必须直连 Area 0？

区域间路由是**距离矢量**行为（Type-3 只带网段和 cost，不带拓扑），如果允许非骨干区域之间直接互通，就失去了 Area 0 这个"中转枢纽"，可能形成环路。所以规则是：**区域间流量必须经过 Area 0**。

### 23. 虚链路（Virtual Link）是什么，什么时候用？

在 ABR 之间通过一个**穿越区域（Transit Area）**建立的逻辑链路，本质是让一个区域"看起来"连到了 Area 0。

**使用场景**：① 区域没有直连 Area 0（拓扑限制） ② 修复被分割的 Area 0。

**代价**：虚链路的路径不进 LSDB 路由计算（只是逻辑连接），运维复杂，**设计上应尽量避免**。

**加分点**：说"这是补救手段，正常设计不该用"——面试官会觉得你有设计思维。

### 24. 区域间路由汇总怎么做？在哪做？

在 **ABR** 上做 `abr-summary`，把连续网段汇总成一条 Type-3。作用是**减少其他区域的 LSDB 和路由表**。

**追问**：外部路由汇总呢？→ 在 ASBR 上做 `asbr-summary`。

**加分点**：汇总要保证明细网段连续；汇总后如果明细里有不可达的，会产生黑洞，需要配 `suppress` 或保证明细完整。

### 25. OSPF 认证有哪几种？

区域认证和接口认证（接口优先）；方式有简单认证（明文）和 MD5 / HMAC-SHA256（加密）。

**现象**：认证失败邻居卡在 Down，`display ospf error` 里能看到认证失败计数。

### 26. `network` 和接口下 `ospf enable` 有什么区别？

`network` 是在进程里声明"哪些接口属于哪个区域"，匹配接口地址；`ospf enable` 是直接在接口下使能，更精确、更清晰。

**答法**：功能上等价，但 `ospf enable` 可读性好、不易配错（`network` 的通配符容易写错把不该加的接口加进去）。新项目优先用接口使能。

### 27. OSPF 怎么和 BFD 联动？为什么要联动？

默认 Hello 10s / Dead 40s，链路故障至少要 40s 才能感知，太慢。BFD 可以毫秒级检测链路故障，通知 OSPF 立即断邻居重算。

**配置**：接口下 `ospf bfd enable`，全局配 BFD 会话参数。

**加分点**：BFD 只做检测，不做路由；检测到故障后由 OSPF 自己处理。两个协议解耦。

### 28. OSPF 的 Hello 定时器不一致会怎样？

邻居建不起来，卡在 Down。Hello 参数（Hello Interval、Dead Interval、Area ID、认证、Stub 标志、网络掩码）必须完全一致。

### 29. 为什么 OSPF 的 Dead Interval 默认是 Hello 的 4 倍？

4 个周期没收到 Hello 才判定邻居失效，容忍偶发丢包（组播 Hello 可能丢一个）。这个比例是经验值。

### 30. OSPF 支持哪些网络类型？

Broadcast（以太网，选 DR）、Point-to-Point（PPP/HDLC，不选 DR）、NBMA（帧中继，手工配邻居）、Point-to-Multipoint（按 P2P 处理）、P2MP 非广播。

**追问**：为什么 P2P 不选 DR？→ 只有两台设备，不需要 DR 减少邻接关系。

### 31. 什么情况下 OSPF 会频繁重算 SPF？

链路抖动、接口 flapping、LSA 频繁变化、大区域拓扑不稳定。

**优化手段**：`spf-schedule-interval`（SPF 计算抑制）、`lsa-generation-interval`（LSA 产生抑制）、BFD + 合理抑制、分区减小影响范围。

### 32. OSPF 路由和 BGP 路由谁优先？

默认 OSPF 的优先级（preference）是 10，BGP 是 255（华为），所以**OSPF 优先**。但可以通过 `preference` 命令调整，或者用 `route-policy` 控制。

**注意**：这里说的是"不同协议间的优先级（管理距离）"，和 BGP 内部的选路是两回事。

### 33. 一台路由器同时跑 OSPF 和 BGP，怎么做路由互引？

两个方向：
- **OSPF → BGP**：BGP 里 `import-route ospf 1`，或用 `network` 宣告
- **BGP → OSPF**：OSPF 里 `import-route bgp`，**必须配 `route-policy` 过滤**，否则会把几十万条 BGP 路由灌进 IGP，直接把设备打挂

**加分点**：BGP 引入 IGP 一定要过滤 + 打 tag（`tag 100`），防止路由回馈形成环。

---

## L3 深挖（8 题，讲自己的实战）

### 34. 你遇到过 OSPF 邻居起不来的问题吗？怎么定位的？

**答题框架**：现象 → 分层排查 → 根因 → 解决。

例：割接后发现两台设备邻居一直 2-Way。
1. `display ospf peer` 看状态 2-Way
2. `display ospf interface` 看两边 dr-priority 都是 0（有人为了"不参与选举"全配了 0）
3. 结果：没有 DR，所有路由器都是 DROther，互相只到 2-Way
4. 解决：恢复其中一台的优先级为默认值，重启 OSPF 进程，邻居恢复 Full

**加分点**：说出"dr-priority 0 是为了避免某台低性能设备当 DR 的常见做法，但全配 0 就没人当 DR 了"——这是真踩过坑才知道的。

### 35. 两个区域之间不通，但邻居都是 Full，怎么查？

1. **确认 ABR 有没有生成 Type-3**：`display ospf lsdb summary` 看目标网段的 LSA 在不在
2. **确认区域类型**：如果是 Stub/Totally Stub，本来就不收 Type-3，只有默认路由
3. **确认区域结构**：非骨干区域之间不能直接互通，必须经过 Area 0
4. **确认汇总**：`abr-summary` 配错会漏掉网段
5. **确认过滤**：`filter-policy export` 可能把这个网段过滤了

### 36. OSPF 的 LSDB 太大怎么办？

① 区域划分（把末端区域做成 Stub/Totally Stub）② ABR 上做区域间汇总 ③ ASBR 上做外部路由汇总 ④ 用 `filter-policy` 过滤不需要的路由 ⑤ 增大 `lsa-generation-interval` 减少频繁泛洪。

### 37. OSPF 和 ISIS 怎么选？

| | OSPF | ISIS |
|---|---|---|
| 标准化 | IETF，厂商中立 | ISO，但被广泛实现 |
| 扩展性 | 大网络时 LSA 泛洪压力大 | TLV 结构扩展性好，超大网络（运营商骨干）更常用 |
| 部署 | 企业/数据中心主流 | 运营商骨干主流 |
| 收敛 | 快 | 快（PRC 部分路由计算，更快） |

**答法**：企业网和数据中心用 OSPF，运营商骨干用 ISIS。数据中心里 OSPF 和 eBGP 都能用，BGP 更适合大规模 Spine-Leaf。

### 38. 为什么数据中心 Spine-Leaf 更常用 BGP 而不是 OSPF？

① 规模：几百台 Leaf 时 OSPF 的 LSDB 和泛洪压力大，BGP 只传前缀 ② 策略：BGP 可以用 AS_Path / Community 精细控制 ③ 收敛域：BGP 故障域小，不会全网 SPF 重算 ④ ECMP 支持好 ⑤ 与 EVPN 天然配套（EVPN 本身就是 BGP 扩展）。

### 39. 什么是 OSPF 的 SPF 抑制？

链路频繁抖动时，SPF 会被反复触发算到 CPU 打满。抑制机制：SPF 计算间隔从初始值开始指数退避（比如 5s、10s、20s...到最大值），减少计算次数。

**配置**：`spf-schedule-interval 5 1000 10000`（初始 5s，最大 10s，hold 10s）。

### 40. OSPF 引入外部路由时为什么会环路？

如果 ASBR A 把外部路由引入 OSPF，ABR B 又把它引回 BGP 再引回 OSPF，路由可能被反复引入，AS_Path 被消耗掉后形成环。

**解决**：引入时打 tag，过滤时识别 tag 不再引入；或者用 route-policy 严格指定哪些路由可以引入。

### 41. OSPFv3 和 OSPFv2 的主要区别？

① OSPFv3 基于链路运行，不是基于网段（用链路本地地址建邻居） ② 认证不再内置，依赖 IPsec ③ 新增 LSA 类型（Type-8 Link LSA、Type-9 Intra-Area Prefix LSA） ④ 支持多实例（一个接口可跑多个 OSPFv3 进程，类似 VRF）。

---

## L4 场景题（4 题）

### 42. 割接时如何保证 OSPF 邻居不中断？

① 割接前确认有冗余路径 ② 调整 cost 让流量先切走，再操作 ③ 用 `stub-router` 临时把设备伪装成末端（让其他设备不经过它转发） ④ 分批操作，每次只动一台 ⑤ 准备好回滚配置。

### 43. 一台设备 OSPF 邻居全断了，怎么快速判断是设备问题还是链路问题？

① `display ospf error` 看错误类型（认证/MTU/Hello 参数） ② `display interface` 看接口是否 Up、有没有 CRC 增长 ③ `display logbuffer` 看有没有接口 down 的记录 ④ 如果所有邻居同时断，大概率是本设备问题（进程重启、CPU 打满、接口板故障），而不是所有链路同时坏。

**加分点**："所有邻居同时断"这个判断逻辑很实用，说明有系统化思维。

### 44. 客户现场不允许改 OSPF 参数（比如 cost），但要求流量走指定路径，怎么做？

① 用 `route-policy` + `filter-policy` 做路由过滤（不引入某条路由，就自然不走） ② 用 `nssa`/`stub` 区域类型改变路由来源 ③ 用 **静态路由 + 优先级调整** 覆盖 OSPF 路由（`preference` 改静态路由优先级低于 OSPF） ④ 用 PBR（策略路由）按源地址引流 ⑤ 最干净的办法：在 ABR 上用 `abr-summary` 加 `cost` 参数调整汇总路由的 cost。

### 45. 面试官问"你对 OSPF 的理解到什么程度"，怎么答？

**别背特性列表**，讲三层：

> 协议层我知道它怎么建邻居、怎么算路、怎么防环；工程层我知道实际组网怎么划分区域、怎么做汇总和特殊区域、哪些参数必须统一；运维层我踩过邻居卡在某个状态的坑，知道从 `display ospf error` 一路查到 LSDB 对比的顺序。

这个答法的价值：**把"知道"分成三层，说明你不是背书的**。

---

## 速记卡（考前扫一眼）

- 状态机：Down Init 2-Way ExStart Exchange Loading Full
- 卡 Init = 单向；卡 ExStart = MTU；卡 2-Way = 正常（DROther 之间）
- LSA：1 拓扑 / 2 网段 / 3 区域间 / 4 ASBR / 5 外部 / 7 NSSA
- DR 选举：优先级 → Router ID，**不抢占**
- 默认参考带宽 100M，必须改，否则高速口 cost 全是 1
- 默认 Hello 10s / Dead 40s，DR 选举等 40s
- 非骨干区域必须直连 Area 0
- BGP 引入 OSPF 必须过滤 + 打 tag
