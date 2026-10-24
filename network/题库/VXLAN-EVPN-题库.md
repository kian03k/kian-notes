---
tags: [network, vxlan, evpn, 面试题库]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# VXLAN / EVPN 题库

> 35 道题。原理细节见 [[VXLAN与EVPN-原理详解]]。

**这个方向的面试规律**：先问"为什么用 VXLAN"，再问"EVPN 五种路由类型"，最后问"分布式网关怎么转发"。**能把这三点讲成一条线的人，基本就过了。**

---

## L1 基础必答（12 题）

### 1. 为什么需要 VXLAN？VLAN 有什么问题？

四个痛点：① VLAN ID 只有 4094 个，云环境不够用 ② 虚机迁移要求同二层域，物理上跨了汇聚层 ③ 大二层靠 STP 防环，一半链路浪费 ④ 租户隔离不足。

**VXLAN 的解法**：二层帧封装进 UDP/IP，用 **24 位 VNI**（1600 万）做标识，三层网络承载二层流量。

### 2. VXLAN 的封装格式？

```
外层以太头 | 外层 IP 头 | UDP 头(4789) | VXLAN 头(8B) | 原始帧
```

VXLAN 头 8 字节：Flags(8) + Reserved(24) + **VNI(24)** + Reserved(8)。

**封装开销**：外层以太 14 + IP 20 + UDP 8 + VXLAN 8 = **50 字节**（不含外层 VLAN Tag 和 FCS）。这就是为什么 VXLAN 场景 MTU 要设 1550 或更大。

### 3. VNI 是多少位？能有多少个？

**24 位，16777216 个**（0–16777215）。这是 VXLAN 相对 VLAN（12 位 4094 个）最大的优势。

### 4. VTEP 是什么？

VXLAN Tunnel End Point，封装/解封装 VXLAN 报文的设备，通常是 Leaf 交换机（也可以是服务器上的软件 VTEP）。

**关键**：VTEP 的 IP 地址必须在 Underlay 里三层可达。

### 5. VXLAN 用什么端口？为什么用 UDP？

**UDP 4789**（IANA 标准），早期 Linux 内核用 8472。

用 UDP 的原因：① NAT/防火墙友好（有端口号） ② 复用成熟 UDP 栈 ③ 外层 IP+UDP 提供熵，让 Underlay 的 ECMP 能负载均衡。

### 6. Underlay 和 Overlay 分别是什么？

- **Underlay**：物理网络，负责把封装好的包送到对端 VTEP（Spine-Leaf、eBGP/OSPF、ECMP）
- **Overlay**：逻辑网络，VTEP 之间的 VXLAN 隧道

**一句话**：Underlay 是"路"，Overlay 是"路上的车"。

### 7. EVPN 是什么？

用 **MP-BGP 扩展**（AFI 25 / SAFI 70）来传递二层/三层信息，替代 VXLAN 的泛洪学习。

**解决问题**：没有 EVPN 时，MAC 地址只能靠泛洪 + 源 MAC 学习（像传统交换机）；有了 EVPN，BGP 直接通告"MAC 在哪个 VTEP 后面"，控制面可控、能做策略、能快速收敛。

### 8. EVPN 有几种路由类型？

五种：Type-1（A-D，快速收敛/水平分割）、Type-2（MAC/IP，**最核心**）、Type-3（IMET，BUM 隧道）、Type-4（ES，DF 选举）、Type-5（IP Prefix，三层路由）。

### 9. Type-2 路由携带什么？

MAC、IP（可选）、VNI、Next-Hop（对端 VTEP 地址）、ESI。

**一句话**：**"MAC X（IP Y）在我这个 VTEP 后面"**。

### 10. Type-3 是干什么的？

**IMET**（Inclusive Multicast Ethernet Tag），通告"我这个 VNI 存在，我的 VTEP 地址是这个"。

**作用**：让源 VTEP 知道 BUM 流量该复制给谁。**没有 Type 3，BUM 流量发不出去。**

### 11. Type-5 和 Type-2 的区别？

- **Type-2**：通告 **MAC + IP**（主机级），用于二层互通和 ARP 抑制
- **Type-5**：通告 **IP 前缀**（网段级），用于跨 VNI 三层转发、引入外部路由

**规模大的时候用 Type-5 汇总，减少表项。**

### 12. 什么是 BUM 流量？

Broadcast（广播）、Unknown unicast（未知单播）、Multicast（组播）。VXLAN 里这三类要特殊处理——因为没有泛洪域，必须显式复制或走组播。

---

## L2 进阶（13 题）

### 13. VXLAN 怎么处理 BUM 流量？三种方式

| 方式 | 做法 | 优缺点 |
|---|---|---|
| **头端复制**（Ingress Replication） | 源 VTEP 自己复制 N 份单播给每个对端 VTEP | 简单，最常用；VTEP 多时复制开销大 |
| **组播**（PIM-SM） | Underlay 跑组播，所有 VTEP 加入同一组播组 | 大规模效率高；运维复杂 |
| **EVPN 组播** | Type-3 通告 + 组播隧道 | 兼顾 |

**现在主流是头端复制**（配合 EVPN 的 Type-3 知道对端列表）。

### 14. EVPN 怎么实现 ARP 抑制？

1. 虚机 A 发 ARP 请求
2. Leaf1 学到 A 的 ARP，通过 **Type-2（带 IP）** 通告出去
3. 其他 Leaf 收到，在本地建立 **ARP 代理表**
4. 其他虚机 ARP 请求 B 时，Leaf **本地直接应答**，不泛洪

**效果**：ARP 广播被彻底压制，这是 EVPN 最大的价值之一。

### 15. 集中式网关和分布式网关的区别？

| | 集中式 | 分布式 |
|---|---|---|
| 网关位置 | 专用设备（Border/Spine） | **每台 Leaf 都是网关** |
| 东西向流量 | **绕行网关** | **Leaf 直连 Leaf** |
| 扩展性 | 网关是瓶颈 | 水平扩展好 |
| 配置量 | 少 | 大（每台 Leaf 配所有 VNI 网关） |
| 现状 | 早期方案 | **主流** |

### 16. 什么是任播网关？为什么要网关 MAC 统一？

分布式网关下，**同一个 VNI 的所有 Leaf 配同一个网关 IP 和同一个网关 MAC**。

**为什么 MAC 必须统一**：虚机迁移前网关 MAC 是 `X`，迁移后如果网关 MAC 变成 `Y`，虚机的 ARP 缓存里还是 `X`，流量就发不出去了。

### 17. 对称 IRB 和非对称 IRB 的区别？

- **对称 IRB**：进入 Leaf 用 VNI_A 查表，出方向用 **L3 VNI** 封装；出口 Leaf 用 L3 VNI 解封装再转发。**两端都用 L3 VNI**，所以叫"对称"
- **非对称 IRB**：进入 Leaf 用 VNI_A 封，出口 Leaf 解封后**本地再路由一次**。出口 Leaf 需要知道所有 VNI 的三层信息

**现状**：对称 IRB 是标准做法，表项压力小。

### 18. 讲一下同 VNI 内二层互通的完整流程

1. A 发 ARP 请求 B
2. Leaf1 有 EVPN 代理 ARP 表，**本地应答**
3. A 发数据帧给 Leaf1
4. Leaf1 查 MAC 表，发现 B 在 Leaf2 后面 → 封装 VXLAN（外层 dst = Leaf2 的 VTEP IP）
5. Underlay 三层转发到 Leaf2
6. Leaf2 解封装，查本地 MAC 表，转发给 B

### 19. 讲一下跨 VNI 三层互通的完整流程

1. A 判断目的 IP 不在同网段，发给网关 MAC
2. Leaf1 收到，查 VNI_A 的三层转发表
3. 查路由表，下一跳是 Leaf2（通过 Type-5 或 Type-2 的 IP 学到）
4. 封装：**外层 VNI 用 L3 VNI**（对称 IRB），内层目的 MAC 是 Leaf2 的网关 MAC
5. Leaf2 收到，用 L3 VNI 解封装，查本地表
6. 找到 C 在 VNI_C，转发给 C

### 20. 为什么 Underlay 常用 eBGP 而不是 OSPF？

① 规模扩展好（只传前缀，LSDB 不膨胀） ② 策略可控（AS_Path、Community） ③ 故障域小 ④ ECMP 支持好 ⑤ 和 EVPN 天然配套 ⑥ AS 号天然防环。

### 21. 什么是 ESI？

**Ethernet Segment Identifier**，标识"一台服务器/一个 CE 通过多条链路连到多个 PE"的这组链路。ESI 相同 = 同一条"以太段"。

用于：① 多归场景的水平分割 ② DF 选举（Type-4） ③ 快速收敛（Type-1）。

### 22. 什么是 DF 选举？为什么需要？

服务器双归到两个 Leaf，如果两个 Leaf 都把 BUM 流量发给服务器，服务器收到两份。

**DF（Designated Forwarder）**：从多个 PE 里选一个负责向该 ES 转发 BUM 流量。选举基于 Type-4 路由（按 VTEP IP 大小）。

### 23. EVPN 的水平分割规则？

- 同 ESI 的成员之间**不互相转发**（防止服务器收到重复流量）
- 靠 Type-1（A-D 路由）实现：收到同 ESI 的 A-D 路由，就知道对端和我连的是同一台服务器，不往那边转

### 24. VXLAN 场景下 ECMP 负载不均是什么原因？

默认 ECMP 哈希用**外层五元组**。VXLAN 封装后，同一对 VTEP 之间的所有流量外层五元组都相同 → 哈希结果固定 → 全走同一条链路。

**解决**：交换机开启**内层哈希**（用内层 MAC/IP/端口的熵做哈希）。

### 25. VXLAN 的 MTU 问题怎么解决？

封装开销 50 字节（外层以太 14 + IP 20 + UDP 8 + VXLAN 8），所以：
- 如果物理 MTU 是 1500，内层最大只能 1450
- 解决：Underlay MTU 设为 **1550 或 9000**（Jumbo 帧），或调整虚机 MTU

**排障**：`ping -s 1472 -f` 测试（1472 + 28 = 1500）。VXLAN 场景要按 1550 测。

---

## L3 深挖（7 题）

### 26. EVPN 控制面和数据面分别做什么？

- **控制面**：BGP EVPN 通告 MAC/IP（Type-2）、BUM 隧道（Type-3）、ES（Type-4）、前缀（Type-5）
- **数据面**：VXLAN 封装转发

**关键**：可以只开控制面（不数据面学习，纯 BGP 学 MAC），也可以两者都开（BGP 优先，数据面兜底）。

### 27. 为什么分布式网关要配 L3 VNI？

对称 IRB 需要：进入 Leaf 用 VNI_A 查表，出方向用 **L3 VNI** 封装。L3 VNI 是专门用于三层转发的 VNI，所有 VNI 共用它（或每个租户一个）。

**好处**：出口 Leaf 只需要知道 L3 VNI，不需要知道所有 VNI 的三层信息。

### 28. EVPN 的 Type-1 有什么用？

① **快速收敛**：链路故障时，A-D 路由快速撤销，其他 PE 立即切换，不用等 MAC 老化 ② **水平分割** ③ **别名（Aliasing）**：多路径负载

**这是"EVPN 收敛比传统二层快"的关键机制。**

### 29. 大规模 EVPN 网络怎么优化？

① 用 Type-5 汇总前缀，减少 Type-2 数量 ② 分层 RR ③ 控制 MAC 表规模（限制 VTEP 数量） ④ BUM 流量用组播而不是头端复制 ⑤ 合理规划 VNI（不要一人一 VNI）。

### 30. 智算网络用 VXLAN 吗？

**参数面不用**：① 全是三层可达地址，没有大二层需求 ② RoCE 对时延敏感，封装开销是负担 ③ 三层 eBGP + ECMP 更简单 ④ MTU 开销让 RoCE 帧更容易超限。

**业务面/管理面看需求**：需要多租户隔离和虚机迁移时用。

**这个回答能立刻区分出是不是真做过智算。**

### 31. VXLAN 和 VLAN 能不能混用？

可以，常见做法：
- **VLAN 作为本地接入**：服务器接 Leaf 的 Access 口用 VLAN，Leaf 内部映射到 VNI
- **VNI 作为跨 Leaf 传输**

**映射关系**：`VLAN ↔ BD（Bridge Domain）↔ VNI`，一条链路。

### 32. EVPN 邻居为什么通常用 iBGP，而 Underlay 用 eBGP？

- **Underlay**：Spine-Leaf 之间用 eBGP，收敛快、故障域小、天然防环
- **Overlay（EVPN）**：所有 Leaf 之间要互相通告 MAC/IP，用 iBGP 全互联（配 RR）更合适，因为它们是"同一个逻辑网络"

**两层独立**：EVPN 邻居在 `l2vpn-family evpn` 下，Underlay 在 `ipv4-family unicast` 下。

---

## L4 场景题（3 题）

### 33. 客户说"同一个 VNI 的两台虚机不通"，怎么查？

1. `display vxlan vni` → 两端 VNI 是否一致
2. `display nve` → VTEP 状态、隧道是否 up
3. `display vxlan tunnel` → 隧道列表有没有对端
4. **Underlay 是否可达**：`ping -a VTEP源地址 VTEP对端地址`
5. `display bgp evpn routing-table type 2` → 对端 MAC 有没有学到
6. `display mac-address` → 本地 MAC 表
7. 检查 VNI 与 BD 的绑定、端口是否加入 BD

### 34. "跨 VNI 不通"怎么查？

在上一题基础上加：
① `display bgp evpn routing-table type 5` 看有没有 IP 前缀路由 ② L3 VNI 是否配置 ③ 网关 IP/MAC 是否两端一致 ④ 虚机的网关是否指向正确 ⑤ 检查是否有 ACL 拦截。

### 35. VXLAN 环境下的排障顺序（通用套路）

```
物理层/Underlay（三层可达）
  → VTEP/NVE 隧道（up）
    → VNI 映射（一致）
      → EVPN 路由（Type-2/3/5 齐全）
        → MAC/ARP 表（学到）
          → 端口/BD 绑定（正确）
            → 策略/ACL（放行）
```

**这个顺序的价值**：从底层往上，每一层都有明确判据，不会乱查。面试时说出这个顺序，比背十个命令有用。

---

## 速记卡

- VNI：24 位，1600 万；端口 4789；封装开销 50 字节
- 五种路由：1 快速收敛/水平分割，2 MAC/IP，3 BUM 隧道，4 DF 选举，5 IP 前缀
- Type-2 = "MAC 在哪个 VTEP 后面"
- 分布式网关：任播网关（同 IP 同 MAC）+ 对称 IRB + L3 VNI
- BUM 三方式：头端复制（主流）/ 组播 / EVPN 组播
- ECMP 不均 → 开内层哈希
- 智算参数面不用 VXLAN
- Underlay 用 eBGP，Overlay（EVPN）用 iBGP
