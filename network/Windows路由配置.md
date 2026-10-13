---
tags: [network, windows, 路由]
created: 2026-10-13
updated: 2026-10-13
status: ok
---

# Windows 路由配置

Windows 下用 `route` 命令手工管理 IPv4 路由表（需管理员权限）。

## 删除路由

```bat
route delete 192.168.1.0
```

## 添加静态路由

```bat
route add 192.168.1.0 mask 255.255.255.0 10.1.1.1 metric 1 if 10
```

参数含义：

| 参数 | 含义 |
| ---- | ---- |
| `192.168.1.0` | 目标网段 |
| `mask 255.255.255.0` | 子网掩码 |
| `10.1.1.1` | 下一跳网关 |
| `metric 1` | 路由优先级，越小越优先 |
| `if 10` | 出接口编号（`route print` 接口列表可查） |

## 常用配合命令

```bat
route print          # 查看路由表与接口编号
route add -p ...     # -p 添加永久路由（重启后保留，否则重启丢失）
```
