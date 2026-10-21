---
tags: [network, mlag, 高可用, 数据中心]
created: 2026-10-21
updated: 2026-10-21
status: ok
---

# M-LAG 与高可用组网

> 双归接入的三种做法（堆叠/VRRP/M-LAG）取舍、M-LAG 原理与配置、脑裂与双主检测、Eth-Trunk 细节。配套题库见 [[交换与高可用-题库]]。

## 一、服务器双归的三种方案

| 方案 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| **堆叠（iStack/CSS）** | 两台设备合成一台逻辑设备，**控制面统一** | 配置简单、管理单点 | 升级要整堆重启；控制面故障影响两台；**跨框链路成瓶颈** |
| **VRRP** | 两台独立设备，网关虚拟化，**主备** | 标准协议、跨厂商 | **备机闲置**（浪费一半带宽）；切换秒级；上行需要 STP 防环 |
| **M-LAG** | 两台独立设备，**控制面独立、数据面双活** | **双活跑满带宽**；单台升级不断业务；故障域隔离 | 配置复杂；有脑裂风险；需要 peer-link |

**现在的数据中心主流是 M-LAG**，原因：带宽利用率 100%（不是主备）、单机可独立升级（不用整堆重启）、故障域小。

## 二、M-LAG 核心概念

```
        ┌──────── Spine ────────┐
        │                       │
   ┌────┴────┐             ┌────┴────┐
   │  Leaf1  │═══ peer-link ═══│  Leaf2  │
   │ (Primary)│             │(Secondary)│
   └────┬────┘             └────┬────┘
        │  Eth-Trunk (跨设备)    │
        └──────────┬────────────┘
              服务器（双网卡）
```

| 概念 | 说明 |
|---|---|
| **DFS Group** | 动态交换服务组，M-LAG 的基本管理单元（`dfs-group 1`）。一对设备一个组 |
| **peer-link** | 两台 M-LAG 设备之间的**直连链路**（通常用 Eth-Trunk 聚合多条）。传递协议报文、同步表项、转发跨设备流量 |
| **M-LAG 接口** | 面向服务器/下联设备的**跨设备 Eth-Trunk**。物理上分布在两台设备上，逻辑上是一个 Eth-Trunk |
| **Primary / Secondary** | 主备角色，**只影响协议处理和控制面**，数据面是**双活**的。主设备负责处理协议报文、同步表项 |
| **双主检测（MAD）** | peer-link 断了以后，两台都认为自己是主 → 需要额外链路检测，防止双主 |

**关键认知：M-LAG 的"主备"不是流量主备，是控制面主备。** 数据面两台都在转发，这是它比 VRRP 强的地方。

## 三、peer-link 与 M-LAG 接口的区别（必考）

| | peer-link | M-LAG 接口 |
|---|---|---|
| 连到哪 | 两台 M-LAG 设备之间 | 下联服务器 / 上联设备 |
| 作用 | 传协议报文、同步 MAC/ARP、**跨设备转发** | 承载业务流量，双活 |
| 是否跑业务流量 | **会**（跨设备流量走这里） | 是 |
| 带宽要求 | **要高**（跨设备流量都走它） | 按业务需求 |
| 常见错误 | 带宽不足导致跨设备流量拥塞 | 成员口数量/速率不一致 |

**跨设备流量的典型场景**：服务器双归两个 Leaf，如果服务器从 Leaf1 进来、目的地在 Leaf2 侧（或上行只走 Leaf2），流量必须走 peer-link。所以 **peer-link 带宽要按"最坏情况全走一台"来规划**。

## 四、M-LAG 建立流程

1. **配置 DFS Group**：`dfs-group 1`，配 `priority`（大者为主）
2. **配置 peer-link**：`peer-link` 接口（通常是 Eth-Trunk）
3. **配置 M-LAG 接口**：`eth-trunk` 下 `mode lacp-static` + `trunkport`，然后 `dfs-group 1 m-lag 1`
4. **协商**：两台交换 DFS Group 信息，选举主备，同步表项
5. **M-LAG 接口 Up**：两端成员口都 Up 后才 Up

**配置示例（华为 CE）**：

```
# Leaf1
dfs-group 1
 priority 150
 #
interface Eth-Trunk0
 mode lacp-static
 peer-link 1

interface Eth-Trunk10
 mode lacp-static
 dfs-group 1 m-lag 1
 trunkport 400GE1/0/1
 trunkport 400GE1/0/2

# Leaf2
dfs-group 1
 priority 100
 #
interface Eth-Trunk0
 mode lacp-static
 peer-link 1

interface Eth-Trunk10
 mode lacp-static
 dfs-group 1 m-lag 1
 trunkport 400GE1/0/1
 trunkport 400GE1/0/2
```

**注意编号一致性**：两台的 **M-LAG 接口编号必须相同**（都是 Eth-Trunk10），否则协商失败。这是最常见的配置错误。

## 五、脑裂与双主检测（MAD）

**问题场景**：peer-link 断了（比如中间的光纤被挖断），两台 Leaf 无法通信：

- 两台都认为对方挂了
- 两台都变成 Primary
- 服务器双归，**两台的 MAC/ARP 表不一致** → 流量可能从两边同时进来，网关重复应答 → **网络混乱**

**双主检测的三种方式**：

| 方式 | 原理 | 优缺点 |
|---|---|---|
| **BFD** | 通过管理网/独立链路跑 BFD，检测对端是否活着 | 快（毫秒级），推荐 |
| **管理网 Ping** | 通过带外管理网互相 ping | 简单但慢（秒级） |
| **Eth-Trunk 成员口检测** | 借助下联服务器的链路间接判断 | 不可靠，不推荐 |

**检测到双主后怎么办**：通常配置为 **Secondary 设备将 M-LAG 接口 Error-Down**（隔离一台），保证只有一台转发，避免混乱。这叫 **MAD 保护动作**。

**恢复**：peer-link 恢复后，两台重新协商，Error-Down 的接口自动恢复。

## 六、M-LAG 与 STP

**M-LAG 组网下 STP 的定位**：

- M-LAG 接口本身**不需要 STP**（逻辑上是一个 Eth-Trunk，无环）
- 但 **peer-link 上要配 STP 保护**（防止 M-LAG 设备和外部交换机形成环）
- 常见做法：peer-link 上 `stp disable` 或配 `stp edged-port`，同时 M-LAG 口配 `stp root-protection` / `loop-protection`

**关键点**：**M-LAG 不依赖 STP 防环，但如果外部还有二层环路，STP 仍然要工作。** 别以为上了 M-LAG 就能关 STP。

## 七、Eth-Trunk（链路聚合）细节

### 两种模式

| | 手工模式（manual） | LACP 模式（static） |
|---|---|---|
| 协商 | 不协商，强制聚合 | 通过 LACPDU 协商 |
| 成员口状态 | 只要物理 Up 就参与转发 | 要协商成功才参与 |
| 故障检测 | 只能靠物理状态（光口断开才发现） | LACP 超时能发现"物理 Up 但逻辑不通" |
| 推荐 | 老设备兼容 | **生产推荐** |

**LACP 关键参数**：

- **活动/备份模式**：`max active-linknumber` 限制活动链路数（比如 8 条里只有 4 条转发，其余备份）
- **LACP 优先级**：`lacp priority` 小的接口优先成为活动口
- **系统优先级**：决定 LACP 主从（`lacp system-priority` 小者为主）
- **超时时间**：短超时 3s，长超时 90s（默认）

### 成员口的约束（常考）

**所有成员口必须一致**：

- 速率、双工
- **VLAN 配置**（允许通过的 VLAN 列表）
- MTU
- 端口类型（access/trunk）
- QoS 配置

**不一致的后果**：成员口无法加入 Eth-Trunk，或者加入后不转发（`Unselect` 状态）。排障看 `display eth-trunk 10` 的 `Status` 列。

### 负载分担模式

```
load-balance src-dst-mac       # 源目 MAC（二层场景）
load-balance src-dst-ip        # 源目 IP（三层场景，推荐）
load-balance src-dst-ip l4-src-port l4-dst-port   # 五元组
```

**哈希不均的经典问题**：同一对 IP 之间的流量**永远走同一条成员链路**（哈希结果固定）。如果只有一两条大流量，其他链路闲置。这就是为什么 VXLAN 场景要开内层哈希。

## 八、堆叠（iStack / CSS）要点

虽然现在主流是 M-LAG，但堆叠仍然常见（尤其接入层和华为 S 系列）。

| 项 | 说明 |
|---|---|
| **主/备/从** | 主设备管理整个堆叠，备设备待命，从设备转发 |
| **堆叠优先级** | 大者优先当主（`stack slot 0 priority 200`） |
| **堆叠口** | 专用堆叠卡 或 业务口（`stack-port`） |
| **堆叠 ID** | 每台成员设备唯一，冲突会导致堆叠建立失败 |
| **分裂（Split）** | 堆叠链路断 → 变成两台独立设备 → **双主**，需要 MAD 检测 |
| **MAD 检测** | 直连检测 / 代理检测（通过上游设备） |

**堆叠 vs M-LAG 怎么选**（面试常问）：

- 接入层、设备少、配置要简单 → 堆叠
- 核心/汇聚、要大带宽、要单机升级、要故障隔离 → M-LAG
- **智算场景基本都是 M-LAG**，因为要独立升级、双活满带宽、故障域小

## 九、VRRP 要点（对比用）

- 虚拟 IP + 虚拟 MAC（`00-00-5E-00-01-{VRID}`）
- 优先级大者为主（默认 100，可配 1–254，255 是 IP 拥有者）
- **抢占**：默认开启（和 OSPF DR 相反）
- **上行链路联动**：`vrrp vrid 1 track interface xxx reduced 30` —— 上行断了主动降优先级，让备机接管（避免"网关在但出不去"）
- 现在的替代方案：**VRRP + BFD**、或者直接 **M-LAG + 任播网关**

## 十、五种高可用技术对比总表

| 技术 | 层级 | 主备/双活 | 收敛速度 | 典型场景 |
|---|---|---|---|---|
| **STP/RSTP** | 二层防环 | 阻塞备份 | 秒级（RSTP） | 传统接入 |
| **Eth-Trunk** | 链路聚合 | 双活（带宽叠加） | 毫秒–秒 | 所有上行链路 |
| **堆叠** | 设备虚拟化 | 双活（跨框） | 秒级（主备切换） | 接入层 |
| **VRRP** | 网关冗余 | 主备 | 秒级（配 BFD 可到毫秒） | 三层网关 |
| **M-LAG** | 设备虚拟化 | **双活** | 毫秒–秒 | 数据中心 Leaf |
| **BFD** | 故障检测 | — | 毫秒级 | 配合路由协议 |

## 十一、M-LAG 排障清单

| 现象 | 检查项 |
|---|---|
| M-LAG 建不起来 | ① 两台 DFS Group 编号/优先级 ② **M-LAG 接口编号是否一致** ③ peer-link 是否 Up ④ 成员口配置是否一致（VLAN/速率/MTU） |
| 一台全断 | 查 peer-link 状态；查双主检测是否触发 Error-Down |
| 流量只走一台 | 查 Eth-Trunk 负载分担模式；查 LACP 活动链路数 |
| 跨设备流量拥塞 | peer-link 带宽不足；考虑优化上行链路让流量本地转发 |
| 服务器网络时通时断 | 双主未检测到，两台都在应答 ARP；查 MAD 配置 |
| 升级一台业务中断 | M-LAG 接口是否配了 `m-lag graceful`（优雅升级） |

**排障命令**：

```
display dfs-group 1              # DFS Group 状态、主备角色
display dfs-group 1 m-lag        # M-LAG 接口状态
display eth-trunk 10             # 成员口状态、负载分担
display lacp peer                # LACP 对端信息
display stp brief                # STP 状态
display mac-address              # MAC 表（对比两台是否一致）
```

## 参考

- 华为 CloudEngine 产品文档 · M-LAG 配置指南
- IEEE 802.3ad（LACP）、IEEE 802.1AX
