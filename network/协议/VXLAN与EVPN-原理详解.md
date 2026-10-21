---
tags: [network, vxlan, evpn, 数据中心]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# VXLAN 与 EVPN 原理详解

> 数据中心大二层为什么用 VXLAN、EVPN 五种路由类型、集中式与分布式网关的取舍、BUM 流量处理。配套题库见 [[VXLAN-EVPN-题库]]。

## 一、为什么需要 VXLAN

传统 VLAN 撑不住现代数据中心的四个痛点：

| 痛点 | 具体问题 |
|---|---|
| **VLAN 数量不够** | 12 位 VLAN ID，最多 4094 个。云环境里每个租户多个网段，根本不够分 |
| **大二层需要打通** | 虚拟机迁移要求迁移前后**在同一二层域**（IP 不变），但物理上跨了汇聚层 |
| **STP 浪费链路** | 大二层靠 STP 防环，一半链路被阻塞，带宽利用率低 |
| **租户隔离不足** | 不同租户共用 VLAN 空间，容易冲突 |

**VXLAN 的解法**：把二层帧**封装进 UDP/IP** 里，用 **24 位 VNI** 做租户标识（1600 万，够用），三层网络承载二层流量。

## 二、VXLAN 封装格式

```
外层以太头 | 外层 IP 头 | UDP 头 (dst 4789) | VXLAN 头 (8B) | 原始以太帧
```

**VXLAN 头 8 字节**：

| 字段 | 长度 | 说明 |
|---|---|---|
| Flags (I bit) | 8 bit | I=1 表示 VNI 有效 |
| Reserved | 24 bit | 保留 |
| **VNI** | **24 bit** | 租户/VXLAN 标识，0–16777215 |
| Reserved | 8 bit | 保留 |

**关键角色**：

- **VTEP**（VXLAN Tunnel End Point）：封装/解封装的设备，通常是 Leaf 交换机
- **VNI**：虚拟网络标识，一个 VNI = 一个二层域（类似一个大 VLAN）
- **NVE**：VTEP 的软件实体，华为叫 NVE 接口

**端口号 4789**（IANA 标准）。早期有的厂商用 8472（Linux 内核默认），互通时要确认。

### 为什么用 UDP 而不是直接 IP

1. NAT/防火墙友好（UDP 有端口号，可以做五元组哈希）
2. 复用成熟的内核 UDP 栈（软件 VTEP 场景）
3. 外层 IP + UDP 头提供足够的熵，让 underlay 的 ECMP 能均匀负载

**ECMP 哈希因子**（常考）：默认五元组（源IP、目的IP、源端口、目的端口、协议）。VXLAN 场景下内层五元组被封装在外层里面，**交换机默认看不到内层**，所以同一对 VTEP 之间的所有流量会走同一条链路——这是 VXLAN 负载不均的经典问题。解决：交换机开启 **内层哈希**（基于内层 MAC/IP/端口做哈希）。

## 三、Underlay 与 Overlay

| 层 | 说明 | 技术 |
|---|---|---|
| **Underlay** | 物理网络，负责"把封装好的包送到对端 VTEP" | Spine-Leaf、eBGP/OSPF、ECMP |
| **Overlay** | 逻辑网络，VTEP 之间的隧道 | VXLAN 隧道、EVPN 控制面 |

**为什么 Underlay 常用 eBGP 而不是 OSPF**（高频考点）：

1. **规模扩展性好**：OSPF 大区域 LSDB 会膨胀，BGP 只传前缀
2. **策略控制强**：可以用 AS_Path、Community 精细控制
3. **收敛可控**：BGP 的故障域更小，不会一抖动全网 SPF 重算
4. **天然支持 ECMP**：多路径等价，`maximum-load-balancing` 配置简单
5. **Spine-Leaf 天然适合**：每台 Leaf 一个独立 AS 号（eBGP），Leaf 之间不建邻居，拓扑清晰

**典型 AS 号规划**：Spine 用 65000，Leaf 用 65001–65xxx，或者 Spine 统一 AS、Leaf 各自 AS（推荐，收敛更快、防环更清晰）。

## 四、EVPN 是什么

**EVPN**（Ethernet VPN）= 用 **BGP 的 MP-BGP 扩展** 来传递二层/三层信息，替代 VXLAN 的"泛洪学习"。

**没有 EVPN 的 VXLAN（Flood and Learn）**：
- 数据面学习：MAC 地址靠**泛洪 + 源 MAC 学习**（像传统交换机）
- 问题：BUM 流量必须泛洪到所有 VTEP，控制面不可控，无法做策略

**有了 EVPN**：
- 控制面：BGP 直接**通告 MAC/IP 和 VTEP 的对应关系**，不需要泛洪学习
- 数据面：VXLAN 只负责转发（也可以保留数据面学习作为补充）
- 好处：**ARP 抑制、MAC 快速收敛、多活、路由可控**

**EVPN 的 AFI/SAFI**：AFI=25（L2VPN），SAFI=70（EVPN）。所以配置里能看到 `address-family l2vpn evpn`。

## 五、EVPN 五种路由类型（核心中的核心）

| 类型 | 名称 | 作用 | 关键字段 |
|---|---|---|---|
| **Type 1** | Ethernet Auto-Discovery（A-D） | 快速收敛、**水平分割**、别名（Aliasing） | ESI、Ethernet Tag |
| **Type 2** | MAC/IP Advertisement | **通告 MAC/IP → VTEP 的映射**（最核心） | MAC、IP、VNI、下一跳、ESI |
| **Type 3** | Inclusive Multicast Ethernet Tag（IMET） | 通告"我这个 VNI 存在"，用于 **BUM 流量** 的隧道建立 | VNI、源 IP（VTEP 地址） |
| **Type 4** | Ethernet Segment | **多归场景（ESI）的 DF 选举** | ESI、源 IP |
| **Type 5** | IP Prefix | 通告 **IP 前缀路由**（三层），用于跨 VNI 的三层转发 | IP 前缀、网关 IP |

### Type 2 详解（最常考）

Type 2 携带：
- **MAC 地址**（必须）
- **IP 地址**（可选，带 IP 才能做 ARP 抑制）
- **VNI**（标识属于哪个虚拟网络）
- **Next-Hop**（对端 VTEP 的地址，即"这个 MAC 在哪个 VTEP 后面"）
- **ESI**（多归场景，标识这条链路属于哪个 ES）

**一条 Type 2 = "MAC X（IP Y）在我这个 VTEP 后面"**。所有 Leaf 收到后就知道转发时该封哪个 VTEP 的隧道。

**ARP 抑制**：Leaf 学到本地虚机的 ARP 后，通过 Type 2 通告出去，其他 Leaf 收到后**在本地建立 ARP 代理表**。之后其他虚机 ARP 请求本地的代理就能应答，**不用泛洪到全网**。这是 EVPN 最大的价值之一——ARP 广播被彻底压制。

### Type 3 与 BUM 流量

BUM = Broadcast / Unknown unicast / Multicast。

**VXLAN 处理 BUM 的三种方式**：

| 方式 | 说明 | 适用 |
|---|---|---|
| **头端复制**（Ingress Replication） | 源 VTEP 自己复制 N 份，分别单播给每个对端 VTEP | 最常用，简单，不需要组播 |
| **组播**（PIM-SM） | Underlay 跑组播，所有 VTEP 加入同一个组播组 | 大规模、BUM 流量多时效率高，但运维复杂 |
| **EVPN 组播**（Type 3 + 组播） | IMET 通告 + 组播隧道 | 结合方案 |

**Type 3 的作用**：告诉其他 VTEP "我这个 VNI 存在，我的 VTEP 地址是这个"。这样源 VTEP 就知道该复制给谁。**没有 Type 3，BUM 流量发不出去**。

### Type 4 与 DF 选举（多归场景）

**ESI**（Ethernet Segment Identifier）：标识"一台服务器/一个 CE 通过多条链路连到多个 PE"的这组链路。ESI 相同 = 同一条"以太段"。

**水平分割需求**：服务器双归到两个 Leaf（Leaf1、Leaf2），如果 Leaf1 收到广播，通过 VXLAN 传给 Leaf2，Leaf2 又通过物理链路发给服务器 → 服务器收到两份。所以需要**水平分割**：同 ESI 的成员之间不互相转发（Type 1 和 Type 4 配合实现）。

**DF（Designated Forwarder）选举**：从多个 PE 里选一个负责**向该 ES 转发 BUM 流量**，避免重复。选举基于 Type 4 路由（按 VTEP IP 大小）。

### Type 5 与三层转发

Type 5 通告 **IP 前缀**（不是 MAC），用于：
- **跨 VNI 的三层转发**
- **外部路由引入**（把数据中心外的路由带进来）
- 大规模场景下替代 Type 2 的 IP 通告（减少表项）

## 六、集中式网关 vs 分布式网关

### 集中式网关

所有 VNI 的三层网关都在**一台（或一对）专用设备**上（通常是 Border/Spine）。

```
Leaf1（VNI 100）──┐
                  ├─→ Spine/GW（所有网关）→ 外部
Leaf2（VNI 200）──┘
```

- 优点：网关集中，策略好管，表项少
- 缺点：**东西向流量绕行**（Leaf1 到 Leaf2 必须经过网关），网关成为瓶颈和单点；横向扩展差

### 分布式网关（现在的主流）

**每台 Leaf 都是网关**，VNI 的网关地址配置在每台 Leaf 上（**任播网关**，同一个 IP/MAC 在所有 Leaf 上）。

```
Leaf1（网关 IP + 网关 MAC）── 直接 VXLAN ── Leaf2（同一个网关 IP/MAC）
```

- 优点：**东西向流量直接 Leaf 到 Leaf**，不绕行；水平扩展好
- 缺点：配置量大（每台 Leaf 都要配所有 VNI 的网关）；需要 **对称 IRB** 保证路径一致

**对称 IRB（Symmetric IRB）** —— 分布式网关的标准做法：

- 进入 Leaf 时：VNI_A → 查三层表 → 出方向用 **VNI_B** 封装（源 VTEP 的 L3 VNI）
- 出 Leaf 时：用 VNI_B 解封装，再查表转发到 VNI_B 的本地端口
- 关键：**两端都用 L3 VNI**，所以叫"对称"

**非对称 IRB**：进入 Leaf 用 VNI_A 封，出 Leaf 解封后本地再路由一次。缺点：出 Leaf 需要知道所有 VNI 的三层信息，表项压力大，已经很少用。

**任播网关的两个关键点**：
1. **网关 MAC 全网统一**（否则虚机迁移后网关 MAC 变了，ARP 表失效）
2. **网关 IP 全网统一**（同一个 VNI 的所有 Leaf 配同一个网关 IP）

## 七、EVPN 转发流程（讲清楚这个就赢了）

**同 VNI 内二层互通**（虚机 A → 虚机 B，同网段）：

1. A 发 ARP 请求 B 的 MAC
2. Leaf1 有 EVPN 学到的代理 ARP 表（Type 2），**本地直接应答**（ARP 抑制）
3. A 发数据帧给 Leaf1
4. Leaf1 查 MAC 表，发现 B 的 MAC 在 Leaf2 后面 → 封装 VXLAN（外层 dst = Leaf2 的 VTEP IP）
5. Underlay 三层转发到 Leaf2
6. Leaf2 解封装，查本地 MAC 表，转发给 B

**跨 VNI 三层互通**（虚机 A → 虚机 C，不同网段）：

1. A 判断目的 IP 不在同网段，发给网关 MAC
2. Leaf1 收到，查三层转发（VNI_A 的网关）
3. 查路由表，下一跳是 Leaf2（通过 Type 5 或 Type 2 的 IP 学到）
4. 封装：**外层 VNI 用 L3 VNI**（对称 IRB），内层目的 MAC 是 Leaf2 的网关 MAC
5. Leaf2 收到，用 L3 VNI 解封装，查本地表，找到 C 在 VNI_C
6. 转发给 C

## 八、常见配置（华为 CE 系列）

```
# 1. Underlay
interface LoopBack0
 ip address 1.1.1.1 255.255.255.255
 
# 2. 开 EVPN 特性、定义 VNI
bridge-domain 100
 vxlan vni 100

# 3. NVE 接口（VTEP）
interface Nve1
 source 1.1.1.1
 vni 100 head-end peer-list protocol bgp

# 4. BGP EVPN 邻居
bgp 65001
 peer 2.2.2.2 as-number 65001
 peer 2.2.2.2 connect-interface LoopBack0
 #
 ipv4-family unicast
  undo peer 2.2.2.2 enable
 #
 l2vpn-family evpn
  policy vpn-target
  peer 2.2.2.2 enable
```

**注意**：EVPN 邻居通常用 **iBGP**（同一个 AS），Underlay 用 eBGP 或 OSPF。EVPN 邻居要 `undo peer enable` 掉 ipv4-family，否则会同时建 unicast 邻居。

## 九、排查思路

| 现象 | 检查项 |
|---|---|
| 隧道建不起来 | `display nve` 看 VTEP 状态；`display vxlan tunnel` 看隧道是否 up；Underlay 到对端 VTEP 地址是否可达 |
| MAC 学不到 | `display bgp evpn routing-table` 看 Type 2 有没有；`display mac-address` 看本地 MAC |
| 同 VNI 不通 | 检查 VNI 是否两端一致；`display vxlan vni`；隧道状态 |
| 跨 VNI 不通 | 检查 L3 VNI 配置；网关 IP/MAC 是否一致；Type 5 是否有 |
| BUM 不通 | `display bgp evpn routing-table` 看 Type 3；头端复制的 peer-list 是否全 |
| 流量不均 | 内层哈希是否开启；`display interface` 看各成员口流量 |
| ARP 抑制不生效 | Type 2 是否带 IP；`display arp` 看是否来自 EVPN |

## 十、智算场景要不要用 VXLAN（实战判断）

智算集群的**参数面**（GPU 梯度同步）**基本不用 VXLAN**，原因：

1. 参数面全是三层可达的地址，**没有大二层需求**
2. RoCE 对时延敏感，VXLAN 封装/解封装引入额外开销和抖动
3. 三层 eBGP + ECMP 更简单、更均匀，还少一层故障点
4. VXLAN 的 MTU 开销（+50 字节）会让 RoCE 的帧更容易超 MTU

参数面用**纯三层 IP 组网 + RoCE**，这是当前主流。

VXLAN 用在哪：**业务面 / 管理面 / 云平台的租户网络**（需要多租户隔离、虚机迁移）。

> 面试如果问"智算网络用 VXLAN 吗"，答"参数面不用，业务面看需求"——这个回答能立刻区分出你是不是真做过。

## 参考

- RFC 7348（VXLAN）、RFC 7432（EVPN）、RFC 8365（EVPN 对称 IRB）
- 华为 CloudEngine 产品文档 · VXLAN 配置指南
