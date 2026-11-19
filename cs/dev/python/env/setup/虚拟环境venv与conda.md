---
tags: [python, 环境, venv, conda]
created: 2026-11-19
updated: 2026-11-19
status: ok
---

# 虚拟环境：venv 与 conda 怎么选、怎么用

> **适用场景**：新项目装依赖怕污染全局；两个项目依赖版本打架；别人拿到代码跑不起来；一台机器要并存多个 Python 版本；装完库却报「找不到模块」。
> 结论先说：**写脚本、做 Web 用 `venv`；数据/AI/科学计算用 `conda`**。两者不要在同一项目里混着用。

## 1. 为什么必须有虚拟环境

虚拟环境 = 独立的 Python 环境，有自己的解释器入口、`site-packages` 和 `pip`，与系统全局 Python 完全隔离。

全局 Python 像公共厨房，谁用谁往里放东西；虚拟环境是你自己的小厨房，装什么、升级什么，都只影响这一间。

| 场景 | 问题 | 虚拟环境怎么解决 |
|---|---|---|
| 两个项目 | A 要 `Django 3.2`，B 要 `Django 4.2` | 各建一个环境，互不干扰 |
| 依赖冲突 | 新代码要 `numpy 2.0`，老脚本只认 `1.24` | 各装各的，互不影响 |
| 项目交接 | 对方「跑不起来」 | 导出 `requirements.txt` / `environment.yml`，一键复现 |
| 重装系统 | 全局库全丢 | 有依赖清单，重建几分钟 |

## 2. venv：标准库自带，零依赖

### 2.1 它到底创建了什么

```bash
python -m venv .venv
```

```text
.venv/
├── Scripts/                 ← Windows
│   ├── python.exe           ← 这个环境自己的解释器
│   ├── pip.exe
│   └── activate.bat
├── bin/                     ← macOS / Linux（python / pip / activate）
├── lib/python3.x/site-packages/   ← 库装在这里
└── pyvenv.cfg               ← 记录由哪个解释器创建
```

没有魔法：**激活 = 把 `.venv` 的 `Scripts`/`bin` 临时插到 `PATH` 最前面**。所以「激活」只对当前这个终端窗口有效，换个窗口就得重来。

### 2.2 五步标准流程

```bash
# 1. 创建（每个项目一次）
cd your_project
python -m venv .venv

# 2. 激活（每次开终端都要做）
.venv\Scripts\activate          # cmd
.\.venv\Scripts\Activate.ps1    # PowerShell
source .venv/Scripts/activate   # Git Bash（Windows）
source .venv/bin/activate       # macOS / Linux

# 3. 装依赖
pip install requests flask

# 4. 记录依赖
pip freeze > requirements.txt

# 5. 别人复现
python -m venv .venv
source .venv/bin/activate       # Windows 见第 2 步
pip install -r requirements.txt
python app.py
```

**四种 shell 的激活命令不一样**，这是 Windows 上最常见的一个卡点：

| Shell | 命令 | 备注 |
|---|---|---|
| cmd | `.venv\Scripts\activate` | 走 `.bat` |
| PowerShell | `.\.venv\Scripts\Activate.ps1` | 被策略拦时报 `无法加载文件`，执行一次 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Git Bash | `source .venv/Scripts/activate` | 路径用正斜杠，不能用 `.bat` |
| macOS / Linux | `source .venv/bin/activate` | — |

切换环境：先 `deactivate`，再激活目标环境。

```bash
(myenv) $ deactivate
$ source .venv/bin/activate
```

### 2.3 激活与不激活的差别

| 操作 | 不激活 | 激活后 |
|---|---|---|
| `where python`（Windows） | `C:\Python310\python.exe` | `...\project\.venv\Scripts\python.exe` |
| `pip install requests` | 装进全局 | 装进 `.venv\Lib\site-packages\` |
| `pip list` | 全机器的库 | 只有这个环境的库 |

**「明明装了库还是 ModuleNotFoundError」九成是这条**：包进了全局，程序跑在另一个解释器上。用 `python -c "import sys; print(sys.executable)"` 一看就知道跑的哪个。

## 3. conda：连解释器一起隔离

### 3.1 与 venv 的对比

| 项目 | `venv` | `conda env` |
|---|---|---|
| 本质 | 隔离包 + pip | 隔离解释器 + 包 + C 库 + 系统依赖 |
| 创建 | `python -m venv .venv` | `conda create -n myenv python=3.9` |
| 换 Python 版本 | 不能，只能用创建它的那个解释器 | 能，`python=3.8/3.10/3.12` 随意指定 |
| 科学计算库 | 能装，但常卡在编译（numpy/scipy 源码构建） | 预编译二进制，一条命令装完 |
| 包管理器 | `pip` | `conda` + `pip` |
| 依赖清单 | `requirements.txt` | `environment.yml` |
| 编译工具链 | 无 | 自带 `gcc` / `gfortran`（Windows 下 `Library/bin/`） |
| 典型场景 | Web、脚本、自动化 | 数据科学、AI、图像处理 |

### 3.2 多版本并存

conda 的价值就在这一条：同一台机器上按需造出任意多个解释器，各自带一套库。

```bash
conda create -n py38  python=3.8
conda create -n py310 python=3.10
conda create -n py312 python=3.12
```

「Python 3.8 + TensorFlow 1.x」和「Python 3.12 + PyTorch」两个项目可以同时存在，切环境即可。

### 3.3 常用命令

```bash
# —— 环境 ——
conda env list                  # 列出所有环境，当前环境带 *
conda create -n myenv python=3.10
conda activate myenv
conda deactivate
conda remove -n myenv --all     # 删环境（含其下所有包）
conda info                      # 当前环境信息

# —— 包 ——
conda list                      # 本环境已装包
conda install numpy pandas
conda install -c conda-forge 包名
conda remove 包名

# —— 迁移 ——
conda env export > environment.yml
conda env create -f environment.yml       # 在另一台机器重建
conda env update -f environment.yml --prune   # 按文件同步，删掉多余包
```

**激活只能用 `conda activate`**，不要混用 `source activate`（老版本残留）或 `venv\Scripts\activate`。

## 4. pip 与 conda 混用：顺序不能乱

| 工具 | 优点 | 缺点 | 用在哪 |
|---|---|---|---|
| conda | 预编译、自动解依赖、能装非 Python 依赖 | 包数量少于 PyPI、更新偏慢 | numpy、pandas、scipy、tensorflow、pytorch、opencv |
| pip | PyPI 全量、版本最新 | 装二进制包容易编译失败 | requests、flask、fastapi、pyyaml、streamlit |

**先 conda，后 pip**：

```bash
conda install numpy pandas matplotlib scikit-learn
pip install streamlit plotly          # conda 没有的（或版本太旧的）再交给 pip
```

反过来（先用 pip 装 numpy、再用 conda 装别的）容易让同一个包出现两份、版本对不上，报错信息还很难读。

### environment.yml

```yaml
name: myproject
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy
  - pandas
  - scikit-learn
  - matplotlib
  - pip
  - pip:
      - streamlit
      - fastapi
```

`dependencies` 下的走 conda，`pip:` 子节点下的走 pip——**这份文件本身就是混用顺序的声明**。

## 5. 判断当前在哪个环境

```bash
# 1. 提示符前缀（最快）
(myenv) $ ...

# 2. 解释器路径（最准）
python -c "import sys; print(sys.prefix)"    # 指向 .venv 或 envs/myenv → 在环境里
python -c "import sys; print(sys.executable)"
where python        # Windows
which python        # macOS / Linux

# 3. conda 专用
conda info --envs
echo $CONDA_DEFAULT_ENV      # macOS / Linux
echo %CONDA_DEFAULT_ENV%     # Windows cmd；PowerShell 用 $env:CONDA_DEFAULT_ENV
```

## 6. 陷阱清单

| 坑 | 现象 | 正解 |
|---|---|---|
| 没激活就 `pip install` | 包进了全局，程序却跑在 `.venv` 里 → ModuleNotFoundError | 先看提示符前缀，或 `sys.executable` |
| 换终端窗口忘了重新激活 | 同上，时好时坏 | 每次开窗口都激活；IDE 里显式指定解释器 |
| PowerShell 激活被拦 | `无法加载文件 Activate.ps1，未对文件进行数字签名` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Git Bash 里敲 `.venv\Scripts\activate` | 提示找不到命令 | 用 `source .venv/Scripts/activate` |
| 把 `venv/`、`.venv/` 提交进 Git | 仓库暴涨、别人机器上路径全错 | 写进 `.gitignore` |
| `pip freeze` 全量导出 | 把无关的间接依赖也写进去，别人装一堆没用的 | 可接受（保证可复现）；要精简就维护手写清单 |
| conda 环境里混用 pip 装 numpy | 版本冲突、`ImportError: DLL load failed` | 科学库一律先 conda |
| 在 `base` 里直接开发 | 库越堆越乱，某天整个 base 崩掉 | `auto_activate_base: false`，每个项目单独建环境 |
| 项目目录里建 venv 但用绝对路径调用别的 python | 装的和跑的不是同一个 | IDE 解释器设为 `.venv` 里的那个 |

## 7. 速查

```text
venv：python -m venv .venv → 激活 → pip install → pip freeze > requirements.txt
激活：cmd .venv\Scripts\activate ｜ PS .\.venv\Scripts\Activate.ps1
      ｜ GitBash source .venv/Scripts/activate ｜ *nix source .venv/bin/activate
conda：create -n X python=3.10 → activate X → install → env export > environment.yml
混用：先 conda 后 pip；科学库 conda，通用库 pip
诊断：sys.prefix / sys.executable / conda info --envs
```

---

相关：各平台的安装与 IDE 配置见 [[Python Env Setup for wsl2]]、[[Python Env Setup]]、[[python 编辑环境创建]]；Windows 下彻底重装见 [[windows版卸载anaconda]]；`venv/` 已列入 `.gitignore` 的写法见 [[gitignore常见问题]]。

回到：[[cs/dev/python/index|Python 导航]]
