---
tags: [python, gui, pyqt]
created: 2026-11-19
updated: 2026-11-19
status: ok
---

# PyQt 入门：选型、事件循环与信号槽

> **适用场景**：要用 Python 做桌面程序（窗口、按钮、进度条、实时曲线），先要决定装 PySide6 还是 PyQt，然后把界面跑起来、控件摆对、耗时任务挪到子线程。
> 这一篇解决「能跑起来 + 知道每个机制为什么存在」；**长任务怎么把进度送到界面上**是独立的一篇，见 [[02-长任务进度反馈]]。

## 1. 选型：PySide6 还是 PyQt

两者都是 Qt 的 Python 绑定，**API 几乎完全一样**，区别只在维护方和许可证：

| | PySide6 | PyQt6 / PyQt5 |
|---|---|---|
| 维护方 | Qt 官方（The Qt Company） | Riverbank（第三方） |
| 许可证 | **LGPL**，闭源商用可免费 | GPL 或商业许可，闭源商用**要付费** |
| 导入 | `from PySide6.QtWidgets import ...` | `from PyQt6.QtWidgets import ...` |
| 信号类 | `Signal` | `pyqtSignal` |
| 启动事件循环 | `app.exec()` | `app.exec()`（PyQt5 是 `exec_()`） |
| 推荐度 | **默认选它** | 只在接手老代码时用 |

**结论**：新项目一律 PySide6。老代码是 PyQt5 的，改导入语句 + `pyqtSignal`→`Signal` + `exec_()`→`exec()` 就能迁，逻辑一行不用动（对照表见 [[02-长任务进度反馈]] 末尾）。

## 2. 装环境与验证

```bash
pip install pyside6
```

装完自带 Qt Designer（可视化拖界面），终端直接敲 `designer` 打开。macOS / Linux 走系统包：

```bash
brew install qt@6            # macOS
sudo apt-get install qt6-tools   # Ubuntu
```

验证（`test.py`，跑完能看到一个写着 Hello 的窗口就通了）：

```python
import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Hello PySide6")
label.show()
sys.exit(app.exec())
```

`sys.argv` + `sys.exit(app.exec())` 是正式写法，能把应用的退出码传回系统；`QApplication([])` + `app.exec()` 只是快速测试用的简写。

## 3. 三个必须理解的机制

### 3.1 事件循环

`app.exec()` 会**阻塞主线程**，在里面不停收事件（点击、键盘、重绘、定时器）并分发给对应控件。所以：

- `exec()` 之后的代码要等窗口关闭才执行；
- 任何放在主线程里的耗时循环都会让界面「未响应」——解决方式是子线程，见 [[02-长任务进度反馈]]。

### 3.2 信号槽

「A 发生时自动触发 B」。按钮点击是信号，你写的处理函数是槽：

```python
button.clicked.connect(show_message)   # 连接
```

自定义信号要带类型声明：

```python
from PySide6.QtCore import Signal, QObject

class Worker(QObject):
    progress = Signal(int)        # 带一个 int 参数

w = Worker()
w.progress.connect(lambda p: print(f"进度 {p}%"))
w.progress.emit(50)               # 触发 → 打印「进度 50%」
```

**信号的意义不只是解耦**：跨线程时，`emit()` 会把槽函数的执行排到**主线程**的事件队列里，这是子线程改 UI 的唯一安全通道。

### 3.3 布局管理

别用 `setGeometry` 手摆坐标——窗口一缩放就全乱。用布局管理器：

```python
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget

layout = QVBoxLayout()
layout.addWidget(QPushButton("Top"))
layout.addWidget(QPushButton("Middle"))
layout.addWidget(QPushButton("Bottom"))

window = QWidget()
window.setLayout(layout)
```

| 布局 | 适用场景 |
|---|---|
| `QVBoxLayout` | 纵向排列（表单、日志区） |
| `QHBoxLayout` | 横向排列（工具栏、按钮行） |
| `QGridLayout` | 表格式（计算器键盘、仪表盘） |
| `QFormLayout` | 标签 + 输入框成对（登录、参数配置） |

嵌套是常规操作：外层 `QVBoxLayout`，某一行塞一个 `QHBoxLayout` 放「路径输入框 + 浏览按钮」。

## 4. 方案：最小窗口骨架

`QMainWindow` + 中央容器 + 布局 + 按钮回调，这是所有桌面工具的起点：

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("最小骨架")
        self.resize(400, 200)

        self.label = QLabel("点击下面按钮")
        self.button = QPushButton("执行")
        self.button.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)     # QMainWindow 必须设 centralWidget

    def on_click(self):
        self.label.setText("已执行")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
```

## 5. 方案：进度条 + 后台线程（最小版）

耗时活必须开线程，**线程里只算，界面只在主线程改**：

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar
)
from PySide6.QtCore import QThread, Signal

class Downloader(QThread):
    progress = Signal(int)

    def run(self):                       # run() 在子线程执行
        for i in range(101):
            self.progress.emit(i)        # 发信号，槽在主线程跑
            self.msleep(50)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.progress = QProgressBar()
        self.button = QPushButton("开始")
        self.worker = None

        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.button.clicked.connect(self.start_task)

    def start_task(self):
        if self.worker and self.worker.isRunning():   # 防连点重入
            return
        self.worker = Downloader()
        self.worker.progress.connect(self.progress.setValue)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
```

两个要点：

- **worker 只建一次并保存引用**。写成 `Downloader().start()` 会连实例一起丢掉，信号还没连上线程就已经开跑，进度条不动；
- **`isRunning()` 判重**。不加这句，连点三次就有三条线程同时往同一个进度条写值。

真实项目里这套骨架会长成「生成器 + 线程消费」的结构，业务代码完全不认识 Qt，见 [[02-长任务进度反馈]]。

## 6. 方案：QChart 实时曲线

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QTimer
import random

class ChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        self.chart_view = QChartView(self.chart)
        self.setCentralWidget(self.chart_view)

        # 只在首次加 series 时建坐标轴，之后不再调用
        self.chart.createDefaultAxes()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)

    def update_data(self):
        self.series.append(self.series.count(), random.randint(0, 100))
```

**`createDefaultAxes()` 只能调一次**。放进 `update_data()` 里每 100ms 调一次，会不断往 chart 上叠加新坐标轴，几十秒后画面糊成一片。要动态改范围就取已有轴再 `setRange`：

```python
axis_x = self.chart.axes()[0]
axis_x.setRange(0, self.series.count())
```

数据量大时（上万点）别用 `QLineSeries` 逐点 append，改 `QScatterSeries` 或用 numpy 批量喂数据；纯静态出图仍推荐 matplotlib，见 [[01-matplotlib出图]]。

## 7. Qt Designer 与 QSS

**Designer**：拖控件 → 存 `.ui` → 代码里加载。

```python
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

f = QFile("main.ui")
f.open(QFile.ReadOnly)
window = QUiLoader().load(f)
window.show()
```

**QSS**：语法接近 CSS，能统一改外观，不碰布局逻辑。

```python
button.setStyleSheet("""
    QPushButton { background: #4CAF50; color: white;
                  border-radius: 5px; padding: 10px; }
    QPushButton:hover { background: #45a049; }
""")
```

小工具用 QSS 就够；界面复杂到要换主题时，再考虑 `QApplication.setStyleSheet` 统一管理样式表文件。

## 8. 陷阱清单

| 坑 | 后果 | 正解 |
|---|---|---|
| 子线程直接改控件（`log_text.append()`） | 随机崩溃，且不一定当次复现 | 一律通过 `Signal` 发回主线程改 |
| `Downloader().start()` 写成临时实例 | 信号连不上，进度条不动 | 先赋值给变量保存引用，再连接再 start |
| 连点按钮反复 `start()` | 多线程并发写同一控件 | `if worker and worker.isRunning(): return` |
| `createDefaultAxes()` 放进刷新回调 | 坐标轴层层叠加，画面糊掉 | 首次加 series 时调一次 |
| 主线程里 `time.sleep()` / 同步 request | 窗口「未响应」 | 挪进 `QThread`，见 [[02-长任务进度反馈]] |
| 用 `setGeometry` 摆位置 | 缩放窗口后控件错位重叠 | 全部用布局管理器 |
| `QMainWindow` 直接 `setLayout()` | 不报错但界面空白 | 先建 `QWidget` 容器 setLayout，再 `setCentralWidget` |
| PyQt 用在闭源商用产品 | 违反 GPL，需购买商业许可 | 直接用 LGPL 的 PySide6 |

## 9. 速查

```text
装：pip install pyside6          验证：QApplication + QLabel + app.exec()
四件套：QApplication / QMainWindow / QWidget 容器 / 布局 addWidget
信号：Signal(类型) → .connect(槽) → .emit(值)
线程：QThread 子类重写 run()，信号回主线程，isRunning() 防重入
图表：addSeries → createDefaultAxes() 仅一次 → QTimer 追加数据
```

---

相关：长任务进度反馈的完整架构见 [[02-长任务进度反馈]]；生成器的语言机制见 [[03-迭代器协议与抽象基类]]；打包成 exe 见 [[pyinstaller]]。

回到：[[cs/dev/python/index|Python 导航]]
