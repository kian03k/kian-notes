---
tags: [network, ssh, 安全加固, 协议]
created: 2026-10-24
updated: 2026-10-24
status: ok
---

# SSH 弱协议加固与算法原理详解

> **适用平台**：华为网络设备（NetEngine 8000 M6/M8、CE 交换机、USG 防火墙等，VRP8/V8 平台）
> **文档说明**：本文档为两轮技术对话的总结留档，涵盖 SSH 弱协议删除建议与 SSH 四类算法原理详解
> **参考来源**：华为官方产品文档与安全加固指导材料

---

## 第一部分：SSH 弱协议删除建议

### 1.1 背景

用户配置了以下 4 类 SSH server 算法，客户要求 SSH 不能使用弱协议，需逐类分析并建议删除：

```
ssh server cipher aes256_ctr aes128_ctr aes256_cbc aes128_cbc 3des_cbc blowfish_cbc
ssh server hmac sha2_256_96 sha2_256 sha1 sha1_96
ssh server key-exchange dh_group_exchange_sha256 dh_group_exchange_sha1 ecdh_sha2_nistp256 ecdh_sha2_nistp384 ecdh_sha2_nistp521 sm2_kep curve25519_sha256
ssh server publickey ecc rsa x509v3-ssh-rsa rsa_sha2_256 rsa_sha2_512
```

### 1.2 加密算法（ssh server cipher）

**官方安全等级排序**（从高到低）：

> aes256_gcm > aes128_gcm > aes256_ctr > aes192_ctr > aes128_ctr > sm4_gcm > sm4_ctr > sm4_cbc > aes256_cbc > aes192_cbc > aes128_cbc > arcfour256 > arcfour128 > blowfish_cbc > 3des_cbc > des_cbc

| 算法 | 判定 | 原因 |
|------|------|------|
| aes256_ctr | ✅ 保留 | CTR 模式，安全 |
| aes128_ctr | ✅ 保留 | CTR 模式，安全 |
| aes256_cbc | ❌ 删除 | CBC 模式，华为官方弱算法列表明确列入 |
| aes128_cbc | ❌ 删除 | CBC 模式弱算法 |
| 3des_cbc | ❌ 删除 | 3DES 已被 NIST 废弃 + CBC 双重弱 |
| blowfish_cbc | ❌ 删除 | Blowfish + CBC 双重弱 |

> 官方原文："Parameters des_cbc, 3des_cbc, aes128_cbc, aes256_cbc, arcfour128, arcfour256, blowfish_cbc, aes192_cbc, and sm4_cbc in the command can be used only after the weak security algorithm function is enabled using the undo crypto weak-algorithm disable command."

**建议新增**：`aes256_gcm`、`aes128_gcm`（安全等级最高的 GCM 模式，当前配置缺失）。

### 1.3 完整性保护算法（ssh server hmac）

| 算法 | 判定 | 原因 |
|------|------|------|
| sha2_256 | ✅ 保留 | SHA-256 完整长度，安全加固推荐 |
| sha2_256_96 | ❌ 删除 | SHA-256 截断至 96 位，弱算法 |
| sha1 | ❌ 删除 | SHA-1，弱算法 |
| sha1_96 | ❌ 删除 | SHA-1 截断 96 位，弱算法 |

> 官方原文："For security purposes, you are advised to use the following HMAC algorithms: sha2_512_etm, sha2_256_etm, sha2_512, and sha2_256."

**建议新增**：`sha2_512`（当前配置缺失）。

### 1.4 密钥交换算法（ssh server key-exchange）

**官方安全等级排序**（从高到低）：

> curve25519_sha256 > ecdh_sha2_nistp521 > ecdh_sha2_nistp384 > ecdh_sha2_nistp256 > dh_group16_sha512 > dh_group_exchange_sha256 > sm2_sm3 > sm2_kep > dh_group14_sha1 > dh_group_exchange_sha1 > dh_group1_sha1

| 算法 | 判定 | 原因 |
|------|------|------|
| curve25519_sha256 | ✅ 保留 | 安全等级 #1，默认算法 |
| ecdh_sha2_nistp521 | ✅ 保留 | ECDH + SHA-2，官方推荐 |
| ecdh_sha2_nistp384 | ✅ 保留 | 同上，安全等级 #3 |
| ecdh_sha2_nistp256 | ✅ 保留 | 同上，官方推荐 |
| dh_group_exchange_sha256 | ✅ 保留 | DH 组交换 + SHA-256，安全加固推荐 |
| sm2_kep | ✅ 保留 | 国密 SM2 密钥交换 |
| dh_group_exchange_sha1 | ❌ 删除 | SHA-1 基础，官方明确认定为弱安全算法 |

> 官方原文："For security purposes, you are advised to use the curve25519_sha256, ecdh_sha2_nistp521, ecdh_sha2_nistp384, and ecdh_sha2_nistp256 key exchange algorithms. The algorithms specified by dh_group_exchange_sha1, dh_group1_sha1, and dh_group14_sha1 in this command are weak security algorithms and are not recommended."

### 1.5 主机密钥算法（ssh server publickey）

| 算法 | 判定 | 原因 |
|------|------|------|
| rsa_sha2_256 | ✅ 保留 | RSA + SHA-256 签名，安全加固推荐 |
| rsa_sha2_512 | ✅ 保留 | RSA + SHA-512 签名，安全加固推荐 |
| ecc | ⚠️ 建议删除 | ECDSA 本身安全，但部分安全加固指南建议仅保留 RSA-SHA2；如客户端需要 ECDSA 认证可保留 |
| rsa | ❌ 删除 | 原始 ssh-rsa 使用 SHA-1 签名，华为弱算法列表明确列入 |
| x509v3-ssh-rsa | ⚠️ 建议删除 | X.509 证书 + RSA，底层签名可能依赖 SHA-1；不在任何安全加固推荐列表中 |

> 官方原文："The algorithms specified by dsa, rsa, and x509v3-ssh-rsa in this command are weak security algorithms and are not recommended."

### 1.6 删除汇总

| 类别 | 删除 | 保留 | 新增 |
|------|------|------|------|
| cipher | aes256_cbc、aes128_cbc、3des_cbc、blowfish_cbc | aes256_ctr、aes128_ctr | aes256_gcm、aes128_gcm |
| hmac | sha2_256_96、sha1、sha1_96 | sha2_256 | sha2_512 |
| key-exchange | dh_group_exchange_sha1 | dh_group_exchange_sha256、ecdh_sha2_nistp256/384/521、sm2_kep、curve25519_sha256 | — |
| publickey | rsa（必删）、ecc、x509v3-ssh-rsa（建议删） | rsa_sha2_256、rsa_sha2_512 | — |

### 1.7 推荐配置

```
# 加密算法：仅保留 CTR + GCM 模式
ssh server cipher aes256_gcm aes128_gcm aes256_ctr aes128_ctr

# 完整性保护：仅保留 SHA-2 完整长度
ssh server hmac sha2_512 sha2_256

# 密钥交换：仅保留 SHA-2 / Curve25519 / 国密
ssh server key-exchange curve25519_sha256 ecdh_sha2_nistp521 ecdh_sha2_nistp384 ecdh_sha2_nistp256 dh_group_exchange_sha256 sm2_kep

# 主机密钥：仅保留 RSA-SHA2（如需 ECDSA 可加 ecc）
ssh server publickey rsa_sha2_512 rsa_sha2_256

# 建议同时配置 DH 交换最小位数
ssh server dh-exchange min-len 2048
```


### 1.8 验证命令

```
# 查看当前 SSH 算法配置
display ssh server cipher
display ssh server hmac
display ssh server key-exchange
display ssh server publickey

# 查看系统中仍存在的弱算法/弱协议（VRP8 平台）
display security risk

# 查看告警（弱算法告警）
display alarm active | include secure
```

### 1.9 兼容性影响

删除弱算法后，**使用旧版 SSH 客户端可能无法连接设备**：

| 客户端类型 | 影响 | 应对 |
|-----------|------|------|
| 老版本 SecureCRT（< 8.0） | 可能不支持 rsa_sha2_256/512 | 升级到 SecureCRT 8.0+ |
| 老版本 PuTTY | 可能不支持 GCM 模式和 ECDH | 升级到最新版 PuTTY |
| 旧版 OpenSSH（< 7.0） | 默认使用 ssh-rsa，删除后协商失败 | 升级 OpenSSH 或客户端强制指定 rsa-sha2-256 |
| 第三方网管/控制器 | 可能依赖特定弱算法 | 提前测试，必要时临时保留兼容算法 |

> 官方提示："执行命令前请确保SSH客户端工具支持以上算法，否则会导致无法使用SSH协议连接设备。"
>
> "关闭不安全的算法，可能会导致兼容问题，需要充分测试后实施。"

**操作建议**：修改前务必先用新算法测试登录，确认管理跳板机/运维工具能正常连接后再正式部署。

---

## 第二部分：SSH 密钥与算法原理详解

### 2.1 四类算法总览

| 类别 | 命令 | 本质 | 作用 | 使用阶段 |
|------|------|------|------|---------|
| 密钥交换 (key-exchange) | `ssh server key-exchange` | 非对称加密协商 | 双方在不安全信道上安全协商出共享的**会话密钥** | 阶段 4：密钥交换 |
| 主机密钥/公钥 (publickey) | `ssh server publickey` | 非对称加密 | ① 服务端身份验证（防中间人）② 用户公钥认证 | 阶段 4 密钥交换 + 阶段 5 用户认证 |
| 加密 (cipher) | `ssh server cipher` | 对称加密 | 用会话密钥对传输数据进行**加解密**，保证机密性 | 阶段 6：交互会话 |
| 完整性校验 (hmac) | `ssh server hmac` | 消息认证码 | 对每个报文计算 MAC 值，保证数据**完整性**和**防篡改** | 阶段 6：交互会话 |

### 2.2 逐类详解

#### 2.2.1 密钥交换算法（key-exchange）—— "怎么安全地约定密码"

**作用**：双方在公开信道上协商出一个只有彼此知道的**会话密钥**（session key），后续对称加密和 HMAC 都用这个密钥。

**原理**：利用 Diffie-Hellman 或 ECDH 等非对称算法，双方各出一半材料，拼出同一个会话密钥，全程不传输密钥本身。

| 算法 | 安全性 | 说明 |
|------|--------|------|
| curve25519_sha256 | ★★★★★ | Curve25519 曲线 + SHA-256，最推荐 |
| ecdh_sha2_nistp521/384/256 | ★★★★☆ | 椭圆曲线 ECDH + SHA-2，官方推荐 |
| dh_group_exchange_sha256 | ★★★★☆ | 动态 DH 组 + SHA-256，安全加固推荐 |
| sm2_kep | ★★★★☆ | 国密 SM2 密钥交换 |
| dh_group_exchange_sha1 | ★★☆☆☆ | SHA-1，弱算法，建议删除 |

#### 2.2.2 主机密钥/公钥算法（publickey）—— "证明你是你"

**作用有两层**：

- **服务端身份验证**（阶段 4）：客户端首次连接时，服务端用主机私钥对密钥交换过程中的数据签名，客户端用主机公钥验签——确认"我连的确实是这台设备，不是中间人"。这就是第一次 SSH 登录时看到的 `Are you sure you want to continue connecting (yes/no)?` 的由来。
- **用户公钥认证**（阶段 5）：如果用户使用密钥登录（非密码），客户端用用户私钥签名，服务端用预先配置的用户公钥验签——确认"这个用户确实是合法的"。

| 算法 | 安全性 | 说明 |
|------|--------|------|
| rsa_sha2_256 | ★★★★☆ | RSA + SHA-256 签名，推荐 |
| rsa_sha2_512 | ★★★★★ | RSA + SHA-512 签名，推荐 |
| ecc | ★★★★☆ | ECDSA 椭圆曲线，推荐（但部分加固指南建议仅保留 RSA-SHA2） |
| rsa | ★☆☆☆☆ | 原始 ssh-rsa，用 SHA-1 签名，弱算法，建议删除 |
| x509v3-ssh-rsa | ★★☆☆☆ | X.509 证书 + RSA，底层依赖 SHA-1，建议删除 |

#### 2.2.3 加密算法（cipher）—— "数据怎么加密"

**作用**：密钥交换阶段协商出会话密钥后，**所有后续传输的数据**（命令、配置、文件传输等）都用这个对称密钥加解密。

**为什么用对称加密**：对称加密（AES 等）处理速度远快于非对称加密（RSA 等），适合大数据量传输。非对称加密只在密钥交换阶段用一次。

| 算法 | 安全性 | 说明 |
|------|--------|------|
| aes256_ctr | ★★★★★ | AES-256 + CTR 模式，推荐 |
| aes128_ctr | ★★★★☆ | AES-128 + CTR 模式，推荐 |
| aes256_cbc | ★★☆☆☆ | CBC 模式，弱算法，建议删除 |
| aes128_cbc | ★★☆☆☆ | 同上 |
| 3des_cbc | ★☆☆☆☆ | 3DES 已被 NIST 废弃，弱算法，删除 |
| blowfish_cbc | ★☆☆☆☆ | Blowfish + CBC，弱算法，删除 |

#### 2.2.4 HMAC 完整性算法（hmac）—— "数据有没有被篡改"

**作用**：对每个传输的报文计算一个**消息认证码**（MAC），接收方用相同的密钥重新计算并比对。如果报文在传输中被篡改，MAC 值不匹配，接收方丢弃报文。

| 算法 | 安全性 | 说明 |
|------|--------|------|
| sha2_256 | ★★★★☆ | SHA-256 完整长度，推荐 |
| sha2_256_96 | ★★☆☆☆ | SHA-256 截断至 96 位，弱算法，建议删除 |
| sha1 | ★☆☆☆☆ | SHA-1，弱算法，建议删除 |
| sha1_96 | ★☆☆☆☆ | SHA-1 截断 96 位，弱算法，建议删除 |

### 2.3 SSH 登录全流程（6 个阶段）

根据华为 UNC 产品文档，SSH 连接经过 6 个阶段：

```
客户端                                      服务端
  |                                            |
  |========== 1. TCP 三次握手 =================>|
  |                                            |
  |<======== 2. 版本号协商 (SSH-2.0) =========>|
  |                                            |
  |========== 3. 算法协商 ====================>|
  |  客户端发送自己的算法列表：                  |
  |  - key-exchange 列表  ← 密钥交换算法        |
  |  - host key 列表      ← 主机密钥算法        |
  |  - cipher 列表        ← 加密算法            |
  |  - MAC 列表           ← HMAC 算法           |
  |                                            |
  |  服务端比对双方列表，每类选第一个匹配的：      |
  |  - 选定 key-exchange 算法                   |
  |  - 选定 host key 算法                       |
  |  - 选定 cipher 算法                         |
  |  - 选定 MAC 算法                            |
  |  任一类无匹配 → 断开连接                     |
  |                                            |
  |========== 4. 密钥交换 ====================>|
  |  用选定的 key-exchange 算法（如 ECDH）      |
  |  双方交换公钥材料，各自算出相同的             |
  |  会话密钥 (session key)                     |
  |                                            |
  |  同时：服务端用主机私钥对交换数据签名         |
  |  客户端用已知的服务端主机公钥验签             |
  |  → 确认服务端身份（防中间人）                 |
  |  ← 这里用到了 publickey 算法                 |
  |                                            |
  |========== 5. 用户认证 ====================>|
  |  方式 A：密码认证                            |
  |  - 客户端发送用户名+密码（已加密）            |
  |                                            |
  |  方式 B：公钥认证                            |
  |  - 客户端用用户私钥签名                      |
  |  - 服务端用预配的用户公钥验签                 |
  |  ← 这里也用到了 publickey 算法               |
  |                                            |
  |========== 6. 交互会话 ====================>|
  |  从此以后，所有数据传输：                     |
  |  - 用 session key + cipher 算法 对称加密     |
  |  - 用 session key + HMAC 算法 计算完整性标签  |
  |                                            |
  |  客户端：加密命令 → 发送                     |
  |  服务端：解密 → 执行 → 加密结果 → 返回        |
  |  客户端：解密 → 显示                         |
```


### 2.4 SSH 登录涉及的三类密钥

| 密钥类型 | 产生方式 | 用途 | 使用算法 |
|---------|---------|------|---------|
| **会话密钥** (session key) | 密钥交换阶段双方协商生成 | 对称加密 + HMAC 完整性校验 | key-exchange 算法协商产生，cipher + hmac 算法使用 |
| **主机密钥对** (host key pair) | 设备本地预先生成（`rsa local-key-pair create`） | 服务端身份验证（防中间人） | publickey 算法 |
| **用户密钥对** (user key pair) | 用户客户端生成，公钥预配到服务端 | 用户公钥认证（免密登录） | publickey 算法 |

> 华为官方原文："SSH通过以下措施实现在不安全网络上提供安全的远程访问：数据加密——通过Client/Server协商交换生成的Encryption Key，实现对数据报文的对称加密，确保数据在传输过程中的机密性。数据完整性——通过Client/Server协商交换生成的Integrity Key唯一标识一条会话链路，所有会话交互报文被Integrity Key标识。一旦数据被第三方修改，接收方就能够检查出来，并丢弃报文。"

### 2.5 一句话总结

| 问题 | 答案 |
|------|------|
| key-exchange 干什么？ | 安全协商会话密钥（非对称） |
| publickey 干什么？ | 服务端身份验证 + 用户公钥认证（非对称） |
| cipher 干什么？ | 加密传输数据（对称，用会话密钥） |
| hmac 干什么？ | 校验数据完整性防篡改（用会话密钥） |
| SSH 登录涉及哪些密钥？ | 会话密钥（临时）、主机密钥对（设备固定）、用户密钥对（用户固定） |
| 四类算法什么时候用？ | key-exchange 和 publickey 在连接建立时用一次，cipher 和 hmac 在整个会话期间持续使用 |

---

## 依据说明

本文结论整理自华为官方产品文档与安全加固指导材料。核心支撑要点：

- **弱算法判定**：官方命令参考对四类 `ssh server` 算法均有明确的安全等级排序与弱算法列表。`aes128_cbc`、`aes256_cbc`、`3des_cbc`、`blowfish_cbc`、`sha1`、`sha1_96`、`sha2_256_96`、`dh_group_exchange_sha1`、`rsa`（原始 ssh-rsa）等被明确列为弱安全算法，配置时需先使能弱算法功能。
- **推荐算法**：加密推荐 GCM / CTR 模式（`aes256_gcm`、`aes128_gcm`、`aes256_ctr`、`aes128_ctr`）；HMAC 推荐完整长度的 `sha2_512`、`sha2_256`；密钥交换推荐 `curve25519_sha256` 与 `ecdh_sha2_nistp521/384/256`；主机密钥推荐 `rsa_sha2_512`、`rsa_sha2_256`。
- **兼容性**：官方明确提示删除弱算法前必须确认 SSH 客户端支持新算法，否则会导致无法连接；需充分测试后再实施。
- **协议流程**：SSH 建链依次为 TCP 握手 → 版本号协商 → 算法协商 → 密钥交换 → 用户认证 → 交互会话；四类算法分别作用于「算法协商」与「交互会话」两个阶段。
