---
tags: [network, 故障排查, ECMP, M-LAG, VRRP]
created: 2026-10-13
updated: 2026-10-13
status: ok
---

# Spine ECMP 哈希不对称导致 ping -a 失败问题分析

> **文档定位**：实际调测问题排查记录
> **涉及设备**：6 台设备（2×USG 防火墙 HRP 主备 + 2×CE6855 Border Leaf M-LAG + 2×CE8865-4C Spine M-LAG）
> **核心结论**：Spine 默认路由有两条 ECMP 下一跳（BL-01 和 BL-02），ECMP 哈希基于源/目的 IP。`ping` 不带 `-a` 时源 IP 为出接口直连地址，哈希选中一台 BL，往返路径一致所以通；`ping -a 10.3.1.1` 改变了源 IP，哈希选中**另一台 BL**，去程走 BL-02 但回程经 M-LAG 共享网关可能回到 BL-01，路径不对称导致回程报文丢失。

**目录**

1. 问题现象
2. 拓扑与设备角色
3. 路由配置分析
4. 根因分析：ECMP 哈希不对称
5. 防火墙会话表证据
6. 与 ICMP 快回问题的区别
7. 解决方案
8. 总结

---

## 一、问题现象

从 Spine（SP-01，CE8865-4C）ping 防火墙 VRRP 虚拟 IP（10.2.2.2）时：

| 测试命令 | 结果 | 详情 |
| --- | --- | --- |
| `ping 10.2.2.2` | ✅ 通 | ttl=253，1ms，0% loss |
| `ping -a 10.3.1.1 10.2.2.2` | ❌ 不通 | Request time out，100% loss |
| 防火墙反向 ping Spine | ✅ 通 | FW 主动 ping 10.3.1.1 可以通 |

**关键疑问**：为什么 `ping` 能通但 `ping -a` 不通？且防火墙反向 ping 可以通？

---

## 二、拓扑与设备角色

### 2.1 设备清单（前 6 台）

| 设备 | IP | 型号 | 角色 | 关键接口 |
| --- | --- | --- | --- | --- |
| FW-Primary（FW-M） | 10.1.1.11 | USG 防火墙 | HRP 主（Active） | Vlanif30=10.2.2.3/28，VRRP VRID 100 VIP=10.2.2.2 |
| FW-Secondary（FW-S） | 10.1.1.12 | USG 防火墙 | HRP 备（Standby） | Vlanif30=10.2.2.4/28，VRRP VRID 100 备 |
| BL-01 | 10.1.1.21 | CE6855 | M-LAG Border Leaf | Vlanif30=10.2.2.1/28（公网→FW Trust），MAC 0000-5e00-01aa |
| BL-02 | 10.1.1.22 | CE6855 | M-LAG Border Leaf | Vlanif30=10.2.2.1/28（同 IP 同 MAC，M-LAG 双活网关） |
| SP-01 | 10.1.1.31 | CE8865-4C | M-LAG Spine | Vlanif300=10.3.1.1/24（公网管理网段） |
| SP-02 | 10.1.1.32 | CE8865-4C | M-LAG Spine | 与 SP-01 配对 |

### 2.2 关键互联拓扑

```text
          SP-01 (10.3.1.1)
           /              \
    100GE1/0/1         100GE1/0/2
     (10.2.1.10)       (10.2.1.14)
         /                  \
    BL-01 (10.2.1.9)    BL-02 (10.2.1.13)
      |    \              /    |
      |  Eth-Trunk100  Eth-Trunk100
      |  (m-lag 100)    (m-lag 100)
      |      \          /
      |     FW-M (VRRP Master)
      |     Vlanif30=10.2.2.3
      |     VRRP VIP=10.2.2.2
      |
    Eth-Trunk101 (m-lag 101)
         |
     FW-S (VRRP Standby)
     Vlanif30=10.2.2.4
```

### 2.3 BL ↔ FW 互联（双 Trunk 方案）

| BL 侧接口 | m-lag ID | 连接目标 | 承载 VLAN |
| --- | --- | --- | --- |
| Eth-Trunk100 | 100 | FW-M（HRP 主） | VLAN 30（Trust）、VLAN 31（Untrust） |
| Eth-Trunk101 | 101 | FW-S（HRP 备） | VLAN 30（Trust）、VLAN 31（Untrust） |

> BL-01 和 BL-02 的 Vlanif30 配置完全一致：IP=10.2.2.1/28、MAC=0000-5e00-01aa（M-LAG 双活网关）。

---

## 三、路由配置分析

### 3.1 SP-01 的公网路由表

SP-01 的默认路由有**两条 ECMP 下一跳**：

```text
0.0.0.0/0 → EBGP
    NextHop 10.2.1.9   (BL-01, via 100GE1/0/1)
    NextHop 10.2.1.13  (BL-02, via 100GE1/0/2)
```

> 这是问题的关键基础：Spine 到 FW VIP 10.2.2.2 的路径有两条等价路由，CE 交换机默认基于**源 IP + 目的 IP** 进行 ECMP 哈希选路。

### 3.2 BL-01 的公网路由表

```text
0.0.0.0/0       Static  → 10.2.2.2  (Vlanif30, FW VRRP VIP)
10.2.2.0/28     Direct  → Vlanif30   (10.2.2.1, 本机网关)
10.3.1.0/24     EBGP    → 10.2.1.10  (100GE1/0/1, 回 SP-01)
```

> BL 的默认路由指向 FW VRRP VIP 10.2.2.2；回 Spine 的路由通过 EBGP 学习。

### 3.3 FW-M 的路由配置

```text
10.3.1.0/24  Static  → next-hop 10.2.2.1  (Vlanif30, BL M-LAG 共享网关)
```

> FW 回 Spine 管理网段（10.3.1.0/24）的下一跳是 BL 的 M-LAG 共享地址 10.2.2.1。

### 3.4 FW 安全策略

```text
security-policy
 default packet-filter intrazone enable
 rule name test
  source-address 10.3.1.1 mask 255.255.255.255
  service icmp
  action permit
 rule name any
  action permit
```

> 安全策略全放通（any permit），不构成阻拦因素。

---

## 四、根因分析：ECMP 哈希不对称

### 4.1 `ping 10.2.2.2`（不带 -a）→ ✅ 通

```text
SP-01 发送：
  src = 10.2.1.10（出接口 100GE1/0/1 自动选源，与 BL-01 直连）
  dst = 10.2.2.2（FW VRRP VIP）
ECMP 哈希（src=10.2.1.10, dst=10.2.2.2）→ 选中 BL-01
去程：SP-01 → BL-01 → Vlanif30 → FW-M（10.2.2.2）
FW-M 收到后回复：
  src = 10.2.2.2, dst = 10.2.1.10
  10.2.1.10 属 BL 侧直连网段（10.2.1.8/30）→ BL 直接 ARP 转发回 SP-01
回程：FW-M → Vlanif30 → BL-01 → SP-01
```

**去程和回程都走 BL-01，路径对称，所以通。**

### 4.2 `ping -a 10.3.1.1 10.2.2.2`（带 -a）→ ❌ 不通

```text
SP-01 发送：
  src = 10.3.1.1（Vlanif300 管理网段，强制指定）
  dst = 10.2.2.2（FW VRRP VIP）
ECMP 哈希（src=10.3.1.1, dst=10.2.2.2）→ 选中 BL-02（不同源 IP → 不同哈希结果）
去程：SP-01 → 100GE1/0/2 → BL-02 → Vlanif30 → FW-M（10.2.2.2）
FW-M 收到后回复：
  src = 10.2.2.2, dst = 10.3.1.1
  10.3.1.1 非直连 → 查路由 → 10.3.1.0/24 → next-hop 10.2.2.1（BL M-LAG 共享网关）
  FW-M ARP 10.2.2.1 → M-LAG 共享 MAC 0000-5e00-01aa → 报文发往 BL-01 或 BL-02
回程：FW-M → Vlanif30 → BL-01（M-LAG MAC 表可能指向 BL-01）→ SP-01
      但去程走的是 BL-02，回程可能走 BL-01 → 路径不对称
```

**核心问题**：

1. **去程走 BL-02**（ECMP 哈希选中），但**回程可能走 BL-01**（M-LAG 共享网关的 MAC 表 / ARP 表可能指向 BL-01）；
2. 这种不对称路径导致回程报文在 M-LAG 转发过程中被丢弃或无法正确送达 SP-01；
3. FW 会话表中**没有** `10.3.1.1 → 10.2.2.2` 的会话记录（见下节），说明报文可能在去程或回程的 BL 侧被丢弃。

### 4.3 哈希选路示意图

```text
                        SP-01 (10.3.1.1)
                       /                    \
              100GE1/0/1                100GE1/0/2
              (→BL-01)                   (→BL-02)
                 /                          \
    ping（无-a）→ BL-01                BL-02 ← ping -a 10.3.1.1
    src=10.2.1.10                      src=10.3.1.1
    哈希选 BL-01 ✅                      哈希选 BL-02 ❌
                 \                          /
                  \---- FW-M (VIP 10.2.2.2) ----/
                        |
                   回程 ARP 10.2.2.1
                   M-LAG MAC → 可能回到 BL-01
                   去程 BL-02 ≠ 回程 BL-01 → 不对称
```

---

## 五、防火墙会话表证据

在 FW-M 上执行 `display firewall session table all`，关键会话：

```text
ICMP  VPN: public --> public  10.2.1.10:4324 --> 10.2.2.2:2048
```

| 会话 | 含义 | 对应测试 |
| --- | --- | --- |
| `10.2.1.10 → 10.2.2.2` | `ping` 不带 -a 的会话 | ✅ 存在（源 = SP-01 出接口 IP） |
| `10.3.1.1 → 10.2.2.2` | `ping -a 10.3.1.1` 的会话 | ❌ **不存在** |

> **`ping -a` 在 FW 上没有创建会话**，说明报文要么没有到达 FW，要么到达后回程被丢弃。结合 ECMP 哈希分析，最可能的原因是去程走 BL-02、回程经 M-LAG 共享网关回到 BL-01，不对称路径导致报文丢失。

---

## 六、与 ICMP 快回问题的区别

本网络中存在**两个不同的 `ping -a` 失败问题**，根因不同，需区分：

| 对比项 | ICMP 快回问题（姊妹篇） | ECMP 哈希问题（本文档） |
| --- | --- | --- |
| ping 目标 | 10.2.2.1（BL 本机 Vlanif30 IP） | 10.2.2.2（FW VRRP VIP） |
| 目标设备 | BL 交换机本机 IP | 防火墙 VRRP 虚拟 IP |
| 根因 | CE 默认使能 ICMP 快回，硬件转发回程报文到非直连目的时失败 | Spine ECMP 哈希将 ping -a 送到了另一台 BL，去程/回程路径不对称 |
| `ping`（无 -a） | ✅ 通（源直连，快回硬件能直接回复） | ✅ 通（哈希选中 BL-01，路径对称） |
| `ping -a` | ❌ 不通（源非直连，快回硬件转发失败） | ❌ 不通（哈希选中 BL-02，路径不对称） |
| `tracert -a` | ✅ 通（UDP 不触发快回，走软件路由表） | — |
| 解决方法 | BL 上 `icmp echo-reply fast disable` | 消除 ECMP 路径不对称（见第七节） |
| 文档 | [CE 交换机 ICMP 快回导致 ping -a 失败分析](CE%20交换机%20ICMP%20快回导致%20ping%20-a%20失败分析.md) | 本文 |

> **两个问题表现相同（ping -a 不通）但根因完全不同**，排查时需根据 ping 的目标地址判断属于哪种情况。

---

## 七、解决方案

### 方案 1：理解并接受（不影响业务流量）

ECMP 哈希不对称主要影响**带指定源 IP 的诊断性 ping**。实际业务流量的源/目的 IP 组合不同，哈希分布也会不同，**不一定都会命中问题路径**。如果业务流量正常，可以理解为这是诊断手段的局限，而非网络故障。

### 方案 2：诊断时使用不带 -a 的 ping

```text
<SP-01>ping 10.2.2.2    # ✅ 通
```

不带 `-a` 时源 IP 自动选为出接口直连地址，哈希路径对称，可以正常验证连通性。

### 方案 3：临时指定单条路由消除 ECMP

在 Spine 上临时加一条更具体的静态路由，强制走单台 BL：

```text
[~SP-01]ip route-static 10.2.2.2 255.255.255.255 10.2.1.9
[*SP-01]commit
```

然后重测 `ping -a 10.3.1.1 10.2.2.2`，预期通。验证后删除：

```text
[~SP-01]undo ip route-static 10.2.2.2 255.255.255.255 10.2.1.9
[*SP-01]commit
```

### 方案 4：调整 ECMP 哈希算法（需评估影响）

CE 交换机支持调整 ECMP 哈希字段，可以通过 `load-balance profile` 调整哈希算法。但修改全局哈希策略会影响所有 ECMP 流量分布，需谨慎评估。

### 方案 5：长期优化 —— 理解 M-LAG 双活网关的回程行为

在 M-LAG 双活网关场景下，FW 的回程报文发往 M-LAG 共享地址（10.2.2.1），M-LAG 会根据 MAC 表将报文送到某一台 BL。这导致：

- **去程**：由 Spine 的 ECMP 哈希决定走 BL-01 还是 BL-02；
- **回程**：由 FW 的 ARP/MAC 表决定回到 BL-01 还是 BL-02；
- **两者独立决策，不保证一致** → 路径不对称。

这是 M-LAG 双活 + ECMP 的固有特性。对于**有状态协议**（如 TCP），不对称路径通常不影响业务（TCP 报文双向独立路由，只要到达即可）；对于**诊断性 ping -a**，可能因为硬件转发的某些限制导致不通。

---

## 八、总结

| 要点 | 说明 |
| --- | --- |
| **根因** | Spine 默认路由 2 条 ECMP 下一跳（BL-01/BL-02），`ping -a` 改变源 IP → 哈希选中另一台 BL → 去程走 BL-02 但回程经 M-LAG 共享网关可能回到 BL-01 → 路径不对称 → 报文丢失 |
| **`ping`（无 -a）为何通** | 源 IP = 出接口直连地址，哈希选中 BL-01，去程回程都走 BL-01，路径对称 |
| **FW 反向 ping 为何通** | FW 主动发起，源 = 10.2.2.2（FW VIP），目的 = 10.3.1.1，FW 查路由→10.2.2.1（BL），BL 查路由→Spine，单路径无 ECMP 不对称问题 |
| **是否影响业务** | 不一定。业务流量的源/目的 IP 组合不同，哈希分布不同，且 TCP 对不对称路径容忍度高 |
| **与 ICMP 快回的区别** | ICMP 快回是 ping BL 本机 IP 时的硬件转发问题；ECMP 哈希是 ping FW VIP 时的路径不对称问题 —— 两个问题根因不同 |
| **排查要点** | 看到 `ping -a` 不通时，先确认 ping 的目标地址：是 BL 本机 IP（查快回）还是 FW VIP（查 ECMP 哈希），再针对性排查 |

---

> **相关文档**：[CE 交换机 ICMP 快回导致 ping -a 失败问题分析](CE%20交换机%20ICMP%20快回导致%20ping%20-a%20失败分析.md)
> **涉及设备**：FW-Primary/Secondary（FW HRP）、BL-01/02（BL M-LAG）、SP-01/02（Spine M-LAG）
