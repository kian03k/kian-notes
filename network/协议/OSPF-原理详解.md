---
tags: [network, ospf, 路由协议]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# OSPF 原理详解

> 从邻居建立到 SPF 计算的完整链路，覆盖状态机、LSA、区域、特殊区域与常见故障现象。配套题库见 [[OSPF-题库]]。

## 一、OSPF 的本质

OSPF 是**链路状态（Link-State）**协议，和 RIP 这类距离矢量协议的根本区别：

| | 距离矢量（RIP） | 链路状态（OSPF） |
|---|---|---|
| 路由器知道什么 | 邻居告诉我的距离和方向 | **全网的拓扑**（谁连谁、链路代价） |
| 交换内容 | 整张路由表 | 链路的"描述"（LSA） |
| 收敛 | 慢，逐跳传播，有环路风险 | 快，各自算 SPF，无环路（区域内） |
| 资源消耗 | 内存小、CPU 小 | 内存大（LSDB）、CPU 有峰值（SPF） |

一句话：**OSPF 让每台路由器都拿着一张完全相同的地图（LSDB），自己算出最短路径树。** 所以 OSPF 收敛后，同区域内所有路由器的 LSDB 必须完全一致，这是排障的核心判据。

## 二、五种报文

| 报文 | 全称 | 作用 | 发往 |
|---|---|---|---|
| Hello | — | 发现/维持邻居、选举 DR/BDR | 组播 224.0.0.5 |
| DD (DBD) | Database Description | 交换 LSDB 摘要（LSA 的 Header） | 单播（点到点阶段） |
| LSR | Link State Request | 请求缺失的完整 LSA | 单播 |
| LSU | Link State Update | 携带完整 LSA，泛洪用 | 单播 / 组播 224.0.0.5、.6 |
| LSAck | Link State Ack | 确认收到 LSU（可靠泛洪机制） | 单播 / 组播 |

**224.0.0.5** = AllSPFRouters，所有 OSPF 路由器监听。
**224.0.0.6** = AllDRouters，只有 DR/BDR 监听（DR 用 .6 把 LSU 泛洪给其他 DR/BDR）。

> 追问点：为什么 OSPF 需要 LSAck？因为 IP 不可靠，OSPF 自己在传输层上做了**可靠泛洪**：每个 LSU 都要被确认，没确认就重传（重传间隔默认 5s）。

## 三、邻居状态机（重点，必考）

正常顺序：`Down → Init → 2-Way → ExStart → Exchange → Loading → Full`

| 状态 | 含义 | 卡在这里说明什么 |
|---|---|---|
| **Down** | 没收到任何 Hello | 链路不通 / 接口没使能 OSPF / area 不一致 / 认证失败 |
| **Attempt** | 只在 NBMA 网络出现，主动发 Hello 未收到回应 | NBMA 下邻居没配或地址错 |
| **Init** | 收到对方 Hello，但**对方的邻居列表里没有我** | **单向通信**：光纤收发接反、ACL 单向过滤、单向链路 |
| **2-Way** | 双方 Hello 里都有对方 | 稳定状态（非 DR/BDR 之间停留在此是正常的） |
| **ExStart** | 协商主从（Master/Slave）和 DD 序列号 | **MTU 不一致**（最常见）、Router ID 冲突 |
| **Exchange** | 互发 DD 报文，交换 LSDB 摘要 | DD 报文被丢弃（MTU、分片问题） |
| **Loading** | 发 LSR 请求缺失的 LSA | LSA 请求不到（MTU、单播不通） |
| **Full** | 双方 LSDB 完全同步 | 目标状态 |

**关键判断口诀**：

- 卡 **Init** → 看**单向**（收得到发不出）
- 卡 **ExStart/Exchange** → 看 **MTU**（华为默认接口 MTU 1500，如果一端改了 9000 就会卡）；`display ospf interface` 两边对比
- 卡 **2-Way** → 若是 DR/BDR 之间的邻居才是故障；普通路由器之间 2-Way 是设计如此
- **Full 了但没路由** → LSDB 有但 SPF 没算出 / 路由被过滤 / 区域或汇总问题

> Init 状态的技术细节：Hello 报文里带着"我见过的邻居 Router ID 列表"。A 收到 B 的 Hello 但 B 的列表里没有 A → A 认为只是"听到"了 B，进入 Init（单向发现）。

## 四、DR / BDR 选举

**为什么需要 DR**：广播网络（以太网）上若 n 台路由器全互联，邻接关系是 n(n-1)/2；引入 DR 后只需 2n-2（所有非 DR 只和 DR/BDR 建立 Full）。同时 DR 负责代表整个广播网段生成 Type-2 LSA，避免每台路由器都描述这个网段。

**选举规则**（顺序不可颠倒）：

1. 比较接口 **DR 优先级**（0–255，默认 1，**0 表示不参选**）
2. 优先级相同比 **Router ID**（大者胜）
3. **不抢占**：DR 一旦选出，除非它失效，否则新加入的高优先级路由器不会抢占（这点和 BGP 不同）

BDR 是亚军的角色，DR 挂掉后 BDR 立即接替（不用重新选举），这是为了快速收敛。

**DR 与其他路由器的邻接状态**：

- DR ↔ BDR：Full
- DR ↔ DROther：Full
- DROther ↔ DROther：**2-Way**（不建立邻接，这是正常的，很多人误判为故障）

**两个排障点**：

- 想让某台设备当 DR：配 `ospf dr-priority 255`，**但必须重启 OSPF 进程或等 DR 失效**才生效（不抢占）
- 抓到 DR 不是预期的设备：常见于 Router ID 未手工规划，靠接口地址自动选举导致不确定

## 五、区域（Area）设计

**为什么要分区域**：单区域时任何一条链路变化都会让所有路由器重算 SPF，LSDB 也会无限膨胀。区域把拓扑变化**挡在区域内**，区域间的路由靠 ABR 汇总传递。

| 区域 | 特点 |
|---|---|
| **骨干区域 Area 0** | 必须有，所有非骨干区域必须直连 Area 0（否则要用虚链路） |
| **普通区域** | 标准区域，收所有类型 LSA |
| **Stub 区域** | 不收 Type-4、Type-5（外部路由），用默认路由出去。适合末端区域 |
| **Totally Stub** | 进一步不收 Type-3（区域间路由），只有一个默认路由。**收敛最好、LSDB 最小** |
| **NSSA** | Stub 的变体，允许自己引入外部路由（Type-7），但**不收**其他区域的 Type-5 |
| **Totally NSSA** | NSSA + 过滤 Type-3 |

**路由器角色**：

- **IR**（Internal Router）：所有接口在同一区域
- **ABR**（Area Border Router）：接口跨多个区域，**且至少一个连 Area 0**（华为要求）
- **ASBR**（AS Boundary Router）：引入外部路由的路由器

**Type-7 转 Type-5**：NSSA 区域内的 ASBR 产生 Type-7 LSA，由 ABR 转换成 Type-5 泛洪到其他区域（转换者 = Router ID 最大的 ABR）。

## 六、LSA 类型（必须背）

| 类型 | 名称 | 谁产生 | 泛洪范围 | 内容 |
|---|---|---|---|---|
| **1** | Router LSA | 每台路由器 | 本区域内 | 自己的链路、接口、代价、邻居 |
| **2** | Network LSA | DR | 本区域内 | 广播网段的子网掩码 + 连着哪些路由器 |
| **3** | Summary LSA | ABR | 区域内（除源区域） | 区域间的**网段**路由 |
| **4** | ASBR Summary LSA | ABR | 区域内 | 告诉别人"ASBR 在哪" |
| **5** | AS External LSA | ASBR | 全 AS（除 Stub/NSSA） | 外部路由（其它协议引入的） |
| **7** | NSSA External LSA | NSSA 内的 ASBR | 仅 NSSA 内 | 外部路由（NSSA 版本） |

记忆锚点：**1、2 描述拓扑（谁连谁），3、4 描述区域间（网段和 ASBR），5、7 描述外部。**

> 追问点：Type-1 的链路类型有四种：Point-to-Point、Transit（连到 DR 的网段）、Stub（末梢网段，只有自己）、Virtual Link。

## 七、SPF 计算过程

1. 以自己为根，把 LSDB 里的 Type-1 当成图的节点和边
2. 用 Dijkstra 算出到每个节点（路由器/网段）的最短路径
3. 把最短路径树上的叶子网段装进路由表
4. 候选下一跳：树上的邻居地址；开销 = 沿途出接口 cost 之和

**开销（Cost）计算**：`cost = 参考带宽 / 接口带宽`，华为默认参考带宽 `100 Mbps`。

| 接口 | 默认 cost |
|---|---|
| 10M | 10 |
| 100M | 1 |
| 1000M | 1 |
| 10G | 1 |
| 400G | 1 |

**默认参考带宽是 100M，导致 100M 以上的接口 cost 全是 1**——千兆和万兆等价，选路会变随机。生产环境必须改：

```
ospf 1
 bandwidth-reference 400000    # 参考带宽 400Gbps
```

改完 400G 接口 cost = 1，100G = 4，25G = 16，这样 SPF 才有区分度。**这是数据中心里一个很实在的坑**，很多人不知道。

> 注意：`bandwidth-reference` 只影响**本设备**计算 LSA 里的 cost，全区域必须统一配置，否则代价语义混乱。

## 八、认证

| 类型 | 说明 |
|---|---|
| 区域认证 | 在 `area x` 下配，区域内所有接口生效 |
| 接口认证 | 在接口下配，优先级高于区域认证 |
| 简单认证 | 明文密码（不安全） |
| MD5 / HMAC-SHA256 | 加密摘要（推荐） |

**认证失败的典型现象**：邻居卡在 Down，`display ospf error` 里能看到 `Authentication failure` 计数增长。

## 九、常用配置（华为）

```
ospf 1 router-id 1.1.1.1
 area 0.0.0.0
  network 10.0.0.0 0.0.0.255
  authentication-mode hmac-sha256 cipher xxx
 area 0.0.0.1
  stub no-summary            # Totally Stub
#
interface GigabitEthernet0/0/0
 ospf enable 1 area 0
 ospf cost 10                 # 手工指定代价
 ospf mtu-ignore              # 忽略 MTU 检查（应急用，不建议长期）
 ospf dr-priority 255
 ospf timer hello 10
 ospf bfd enable              # BFD 联动快速检测
```

**注意 `ospf enable` 与 `network` 的区别**：华为支持接口下 `ospf enable` 精确控制参与 OSPF 的接口，比 `network` 声明更清晰，新项目优先用这种。

## 十、排障命令速查

```
display ospf peer                        # 邻居状态
display ospf peer brief                  # 邻居简表
display ospf interface                   # 接口参数（area、cost、DR、定时器）
display ospf lsdb                        # LSDB 全量
display ospf lsdb router 2.2.2.2         # 指定 LSA 详情
display ospf routing                     # OSPF 算出的路由
display ospf error                       # 错误统计（认证失败、MTU、Hello 参数不一致都在这）
display ospf brief                       # 进程概览（Router ID、区域、SPF 次数）
reset ospf process                       # 重启进程（会断邻居，慎用）
```

**排障顺序建议**：`error 统计` → `peer 状态` → `interface 参数对比` → `lsdb 对比` → `routing 表`。先看错误计数能省一半时间。

## 十一、常见故障与根因

| 现象 | 根因 | 定位方法 |
|---|---|---|
| 邻居卡 Init | 单向通信（收得到发不出） | 对端 `display ospf peer` 看有没有我；查 ACL 和光模块收发 |
| 邻居卡 ExStart | MTU 不一致 | 两边 `display interface` 看 MTU；临时 `ospf mtu-ignore` 验证 |
| 邻居卡 2-Way | 双方都是 DROther（正常）或 DR 优先级全为 0 | 检查 `dr-priority` 是否为 0 |
| 邻居 Full 但无路由 | 路由过滤、区域不匹配、汇总错误 | `display ospf routing` 看有没有；`display ip routing-table` 对比 |
| 路由频繁震荡 | 链路闪断 / SPF 频繁重算 | `display ospf brief` 看 SPF 次数增长；上 BFD + 合理抑制 |
| 区域间不通 | 非骨干区域没有直连 Area 0 | 检查区域拓扑，需要虚链路的话配置 `vlink-peer` |
| CPU 高 | 大区域 LSDB 大、频繁 SPF | 分区、汇总、STUB 化 |

## 十二、设计要点（面试加分）

1. **Router ID 必须手工规划**，不要靠自动选举——否则 DR 选举结果不可控，排障时也难看
2. **改 `bandwidth-reference`**，否则高速链路 cost 全为 1
3. **区域划分**：接入层往上的汇聚做 ABR，末端区域做成 Totally Stub 或 Totally NSSA 减小 LSDB
4. **汇总在 ABR 上做**（`abr-summary`），外部路由汇总在 ASBR 上做（`asbr-summary`）
5. **BFD 联动**：默认 Hello 10s / Dead 40s，故障感知太慢；数据中心改用 BFD（毫秒级）或调小 Hello/Dead（但会增加 CPU）

## 参考

- RFC 2328（OSPFv2）、RFC 5340（OSPFv3）
- 华为 S 系列交换机产品文档 · OSPF 配置指南
