---
tags: [android, 踩坑]
created: 2026-10-24
updated: 2026-10-24
status: ok
---

# Android 刷机与 Root（三星 A5000 实践记录）

> **这是一份历史记录，不是教程推荐。**
> 2023 年 4 月为了一台三星 Galaxy A5 走过一遍完整的「回官方固件 → Root → 装游戏辅助」流程，原始资料 4.7 GB 已于 2026-10-24 删除。本文保留**路怎么走**，方便以后遇到同类需求（尤其是老三星救砖）不用从零查。
> ⚠️ **2026 年现状**：CF-Auto-Root 已停止维护、游戏辅助全部失效、Android 6 无安全更新。**下面的流程对「老三星刷官方固件 / 救砖」仍然有效，对「root 后装辅助」已无意义。**

## 一、设备与工具组合

| 项 | 值 |
| --- | --- |
| 机型 | 三星 Galaxy A5（2015），型号 **SM-A5000**（国行） |
| 区域码 | CHC（中国大陆） |
| 固件版本 | `A5000ZCS1CRG1`（Android 6.0.1） |
| 刷机工具 | Odin3（用到过 v3.10.6 和 v3.14.4） |
| Root 方案 | CF-Auto-Root，包名 `a5ltechn-a5ltezc-sma5000` |
| Root 管理 | Magisk v23.0 |
| 辅助工具 | 小曦 COC 辅助（手机版 + 雷电模拟器专版）、Total Control 群控 |

> 型号与包名的对应关系是复现的关键：`a5ltechn` = A5 LTE 电信版，`a5ltezc` = A5 LTE 中国区，`sma500` = SM-A5000。**刷错包会卡开机。**

## 二、完整流程

### 1. 准备阶段

1. 电脑装**三星 USB 驱动**（没有的话 Odin 认不到设备）
2. 手机开**开发者选项**：设置 → 关于手机 → 连点「版本号」7 次
3. 打开 **USB 调试** 和 **OEM 解锁**（OEM 解锁不开，刷完会锁 BL）
4. **备份数据**——刷机必然清空，照片 / 通讯录 / 微信记录先导出

### 2. 回官方固件（救砖 / 从头开始）

1. 从 SamMobile / SamFrew / Frija 按 `SM-A5000` + `CHC` 下载固件
2. 老机型固件通常是**四件套**：`AP` / `BL` / `CP` / `CSC`
   - 单文件 `.tar.md5` 也常见，直接放 **AP** 槽
3. 手机关机，进 Download 模式：**音量下 + Home + 电源**，出现警告后按**音量上**确认
4. Odin **以管理员身份运行**，用原装或质量好些的数据线连接
5. 四件套分别放入对应槽位（CSC 用普通版，`HOME_CSC` 是保留数据版）
6. 勾选 `Auto Reboot` 和 `F.Reset Time`，其余默认 → **Start**
7. 显示 `PASS!` 后自动重启；首次开机很慢（5–10 分钟），别急着拔线

### 3. 获取 Root（当年的做法）

1. 把 `CF-Auto-Root-a5ltechn-a5ltezc-sma5000.tar.md5` 放进 Odin 的 **AP** 槽
2. 同样流程刷入，重启后设备已带 root
3. 装 **Magisk** 或 SuperSU 做权限管理

> CF-Auto-Root 的原理：把改过的 `boot.img` 和 `recovery` 打包成 Odin 能刷的 tar，一次性完成，不用先刷第三方 recovery。**它强绑定固件版本**，版本一变就可能卡开机。

### 4. 装辅助（已失效，仅记录）

当时的路子是：手机直接装辅助 APK；或者电脑跑**雷电模拟器小曦专版**，用 Total Control 群控多开挂机。

## 三、踩过的坑

| 坑 | 表现 | 处理 |
| --- | --- | --- |
| **Knox 熔断** | 刷非官方固件后 Knox 计数器变 `0x1`，Samsung Pay / 安全文件夹永久失效 | 不可逆，国行机刷机前要想清楚 |
| **固件版本不匹配** | 卡在开机 logo 循环 | 必须下**同型号同区域**的固件重刷 |
| **Odin 认不到设备** | ID:COM 不亮 | 换数据线 / 装驱动 / 换 USB 口（别用前置口和 hub） |
| **刷完卡开机** | 进 Recovery 双清（`wipe data` + `wipe cache`）再重启 | 通常是 CSC 不匹配或降级刷机导致 |
| **降级刷机** | 高版本固件刷低版本会失败 | 三星有防回滚（RP SWREV），只能刷同级或更高 |
| **root 后系统更新失败** | OTA 检测到系统被改 | 需先 unroot 或刷回官方固件 |

## 四、现在（2026）要 root 三星该怎么做

CF-Auto-Root 早就没更新了，**不要再找它的新版**。现行通用方案：

| 方案 | 适用 | 步骤概要 |
| --- | --- | --- |
| **Magisk patch boot** | 有官方固件包、能解出 `boot.img` 的机型 | 提取 `boot.img` → Magisk App 修补 → Odin 刷回 |
| **TWRP + Magisk** | 有可用 TWRP 的老机型 | Odin 刷 TWRP → 进 Recovery 刷 Magisk zip |
| **KernelSU** | 支持 GKI 内核的新机型 | 刷内核，不开机也能 root |

工具都在官方仓库，按需下载，不用囤：

- Magisk：`github.com/topjohnwu/Magisk`
- Odin：三星内部工具、无官方公开页，第三方站可下但**务必校验来源**
- 三星官方固件：`sammobile.com/firmwares`、SamFrew、Frija

## 五、原资料清单（已删除）

留个账，方便日后判断"是不是有一套完整的"：

| 内容 | 大小 | 说明 |
| --- | --- | --- |
| 官方固件 `CHC-A5000ZCS1CRG1.rar` | 1.26 GB | 四件套，救砖核心 |
| CF-Auto-Root 包（tar.md5 + Odin3） | 39 MB | 一键 root |
| Magisk v23.0 | 6.8 MB | root 管理 |
| Odin3 v3.14.4 | — | 刷机 |
| Total Control | — | 手机群控（商业软件） |
| 小曦 COC 辅助全家桶 | 343 MB | 辅助 APK + 雷电模拟器专版 + 说明文档 |
| 部落冲突本体 / 辅助 / Clash | 408 MB | 2023 年版本，全部过期 |
| COC 辅助源码（Android Studio 项目） | 8.7 MB | `COC_helper_xtyzhen` |

**共约 4.7 GB，2026-10-24 删除**——所有内容要么已失效，要么可从官方重新获取。
