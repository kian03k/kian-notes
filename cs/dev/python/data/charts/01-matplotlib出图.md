---
tags: [python, 可视化]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# matplotlib 出图（中文与常用图）

> **适用场景**：把统计结果快速出成折线图、柱状图、保存成 PNG 交付。
> **一句话**：中文显示和负号这两行设置是必需品，不设就是满屏方块。

## 1. 必备设置（中文 + 负号）

```python
import matplotlib.pyplot as plt

# 中文显示（必须设置，否则方块）
plt.rcParams["font.family"] = ["SimHei"]          # 或 font.sans-serif
plt.rcParams["axes.unicode_minus"] = False        # 负号正常显示
```

> Linux 服务器上通常没有 `SimHei`，需要装 `wqy-zenhei` / `Noto Sans CJK`，然后改成对应字体名。
> 找不到字体时用 `matplotlib.font_manager` 打印可用字体列表确认。

## 2. 方案：折线图

```python
import numpy as np

x = np.linspace(-10, 10, 50)
plt.plot(x, x ** 2, "ro-")     # r=红, o=点, -=线
plt.title("抛物线"); plt.xlabel("x"); plt.ylabel("y")
plt.show()
```

## 3. 方案：柱状图 + 数据标签

```python
names, vals = ["A", "B", "C"], [30, 45, 20]
plt.bar(names, vals, width=0.6, align="center")
for x, y in zip(names, vals):
    plt.text(x, y + 0.5, str(y), ha="center")     # 在柱顶标数值
plt.ylim([0, 50]); plt.title("商品信息"); plt.show()
```

## 4. 无界面环境（服务器 / 定时任务）

服务端没有显示器时 `plt.show()` 什么也不会发生，要用 `savefig`：

```python
import matplotlib
matplotlib.use("Agg")          # 必须在 import pyplot 之前设
import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [2, 4, 1])
plt.savefig("out.png", dpi=150, bbox_inches="tight")
plt.close()                    # 批量出图不 close 会累积泄漏内存
```

## 5. 陷阱清单

| 坑 | 现象 | 对策 |
|---|---|---|
| 没设中文字体 | 标题/轴标签全是方块 | `rcParams["font.family"] = ["SimHei"]` |
| 负号显示成方块 | `-1` 变方框 | `axes.unicode_minus = False` |
| 服务器上 `show()` | 无任何输出，也没报错 | 用 `Agg` 后端 + `savefig()` |
| 批量出图不 `close()` | 内存持续上涨 | 每张图后 `plt.close()` |
| 图被裁掉一部分 | 标签/图例被切边 | `bbox_inches="tight"` |

> 要交互式图表（网页里可缩放/悬浮）就别用 matplotlib，走 ECharts / Plotly，见 [[cs/dev/python/web/01-Flask全链路|web/01]] 的前端联调一节。

---

回到：[[cs/dev/python/index|Python 导航]]
