
# 虚拟机 Linux (Ubuntu/CentOS) Python 3.12 环境搭建完整指南 (基于 Anaconda)

本文档旨在提供一套在 Linux 虚拟机中，从零开始搭建基于 Anaconda 的 Python 3.12 开发环境的完整、可复现的流程。特别涵盖了使用 `wget` 下载时可能遇到的常见问题（如 403 错误）及其解决方案，并详细解释了关键命令的含义，适合初学者理解和操作。



## 第一部分：安装 Anaconda

Anaconda 是一个开源的 Python 发行版本，包含了 `conda`、Python 以及大量科学计算包，可以方便地管理多版本的 Python 环境。

### 步骤 1：下载 Anaconda 安装脚本

打开虚拟机终端，进入临时目录并下载安装包。

```bash
# 1. 进入系统临时目录，避免文件混乱
cd /tmp
```

#### 🔧 下载方法 A：使用清华大学镜像站（推荐，速度快）
由于 Anaconda 官方源在国外，下载速度可能很慢。国内用户强烈建议使用镜像站。
 **清华环境**
https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/

> **⚠️ 常见问题：`wget` 下载报错 `403 Forbidden`**
> *   **原因**：镜像站通常有防盗链机制，拒绝非浏览器的下载请求（即拒绝 `User-Agent` 为 `Wget` 的请求）。
> *   **解决方案**：使用 `--user-agent` 参数，让 `wget` 伪装成浏览器。

```bash
# 使用 --user-agent 参数伪装成 Chrome 浏览器进行下载
# 请确保文件名与镜像站上的最新版本一致（截至文档编写，最新版为 2025.12-2）
wget -c --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-2025.12-2-Linux-x86_64.sh
```

*   **`-c`**：`--continue` 的缩写，支持断点续传，防止因网络中断导致下载失败。

#### 🌐 下载方法 B：使用 Anaconda 官方源
如果镜像站链接失效或你希望直接从官网下载。

```bash
# 从官方仓库下载，通常不限制 User-Agent，但速度可能较慢
wget -c https://repo.anaconda.com/archive/Anaconda3-2025.12-2-Linux-x86_64.sh
```

### 步骤 2：运行安装脚本

下载完成后，运行脚本开始安装。

```bash
# 使用 bash 命令执行安装脚本（可以使用 Tab 键自动补全文件名）
bash Anaconda3-2025.12-2-Linux-x86_64.sh
```

#### 📜 跟随安装向导
1.  **阅读协议**：按下 **空格键** 逐页浏览许可协议，直到提示输入。
2.  **同意协议**：输入 `yes` 并按回车。
3.  **选择安装路径**：
    *   提示：`Do you wish the installer to install Anaconda3 at this location? [/home/你的用户名/anaconda3]`
    *   **直接按回车**，接受默认路径。这是最规范的安装方式。
4.  **初始化 Anaconda（关键步骤）**：
    *   提示：`Do you wish the installer to initialize Anaconda3 by running conda init? [yes|no]`
    *   **务必输入 `yes` 并回车**。此操作会自动将 `conda` 命令添加到你的 shell 配置文件（如 `~/.bashrc`）中。

### 步骤 3：验证安装

安装完成后，需要使配置生效并验证。

```bash
# 1. 重新加载 .bashrc 配置，使 conda 命令立即生效
source ~/.bashrc

# 2. 此时命令行前应出现 (base) 字样，表示已进入 Anaconda 的 base 环境

# 3. 验证 conda 版本
conda --version
```
如果成功显示 `conda` 的版本号，则安装成功。

---

## 第二部分：创建与管理 Python 3.12 环境

为了保持项目环境的独立和整洁，我们将创建一个专属的 Python 3.12 环境。

### 步骤 1：创建新环境

```bash
# 创建名为 py312 的环境，并指定 Python 版本为 3.12
conda create -n py312 python=3.12
```

*   **`-n py312`**：`-n` 是 `--name` 的缩写，用于指定新环境的名称（这里命名为 `py312`，可自定义）。
*   **`python=3.12`**：指定环境中的 Python 版本。

系统会解析依赖并显示即将安装的包列表，提示 `Proceed ([y]/n)?`。输入 `y` 并回车，等待环境创建完成。

### 步骤 2：激活并使用新环境

```bash
# 激活 py312 环境
conda activate py312
```
此时，命令行前的提示符应从 `(base)` 变为 `(py312)`，表示当前终端会话已切换至此环境。

### 步骤 3：验证环境

```bash
# 检查 Python 版本
python --version
# 输出应为 Python 3.12.x

# 查看当前所在环境
conda info --envs
# 或
which python
# 路径应指向 /home/你的用户名/anaconda3/envs/py312/bin/python
```

### 📝 常用 Conda 命令速查表

| 目的 | 命令 |
| :--- | :--- |
| **查看所有环境** | `conda env list` |
| **激活指定环境** | `conda activate <环境名>` |
| **退出当前环境** | `conda deactivate` |
| **安装包（优先）** | `conda install <包名>` |
| **安装包（备选）** | `pip install <包名>` |
| **删除环境** | `conda remove -n <环境名> --all` |
| **更新 Conda 自身** | `conda update -n base -c defaults conda` |

> **💡 包管理建议**：优先使用 `conda install`，因为它能更好地处理依赖关系且提供预编译的二进制文件，在 Linux 上安装更稳定快速。当 `conda` 源中没有所需包时，再使用 `pip`。

---

## 第三部分：在 PyCharm 中配置远程解释器

如果你使用 PyCharm 进行远程开发（宿主机是 Windows/macOS，解释器在 Linux 虚拟机中），需要完成以下配置。

### 步骤 1：获取环境解释器路径

在 Linux 虚拟机终端中，确保已激活目标环境 `py312`，然后执行：

```bash
which python
```
复制输出的完整路径，例如：`/home/你的用户名/anaconda3/envs/py312/bin/python`。

### 步骤 2：在 PyCharm 中配置

1.  在宿主机上打开 PyCharm，并确保已配置好与虚拟机的 SSH 连接（参照 PyCharm 官方文档或相关教程）。
2.  打开你的项目，进入设置：`File` -> `Settings` (Windows/Linux) 或 `PyCharm` -> `Settings` (macOS)。
3.  导航到：`Project: <你的项目名>` -> `Python Interpreter`。
4.  点击右上角的齿轮图标 ⚙️，选择 `Add`。
5.  在弹出的对话框中，选择 **`SSH Interpreter`**。
6.  选择已配置好的 SSH 连接，或新建一个连接。
7.  在 **Interpreter** 配置页面，选择 **Existing environment**，然后在路径栏中**粘贴**你在步骤 1 中复制的路径（如 `/home/用户名/anaconda3/envs/py312/bin/python`）。
8.  点击 `Finish` 或 `OK`。PyCharm 将连接到远程环境并进行索引，完成后即可正常使用。

---

## 附录：常见问题与优化建议

### Q1: 为什么有时候打开新终端 `conda` 命令找不到？
**A**: 如果新终端没有自动进入 `(base)` 环境或找不到 `conda` 命令，可能是 shell 配置文件未正确加载。手动运行以下命令即可：
```bash
source ~/.bashrc
```

### Q2: 如何永久配置 Conda 使用国内镜像源加速？
**A**: 运行以下命令配置清华大学开源软件镜像站，可显著提升 `conda install` 的下载速度。
```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --set show_channel_urls yes
```

### Q3: 如何彻底删除 Anaconda？
**A**: 如需卸载，直接删除 Anaconda 安装目录并清理配置文件即可。
```bash
# 1. 删除 Anaconda 安装目录
rm -rf ~/anaconda3

# 2. 清理 .bashrc 文件中由 conda init 添加的配置段（可选，推荐手动编辑 ~/.bashrc 删除相关行）

# 3. 删除 Conda 的配置文件目录
rm -rf ~/.conda
```

### Q4: SSH 环境配置
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openssh-server -y
# 设置开机自启
sudo systemctl start ssh
sudo systemctl enable ssh
```