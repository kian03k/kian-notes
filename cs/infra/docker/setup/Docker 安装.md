在 Linux 系统上，通过官方提供的软件源手动安装 Docker 。

### 🛠️ 第一步：准备工作

在安装新版本之前，清理系统中可能存在的旧版本 Docker 是一个好习惯，可以避免潜在的冲突。

1.  **更新软件包索引**
    ```bash
    sudo apt-get update
    ```
    **作用**：同步你系统本地的软件包列表与软件源服务器上的最新列表，确保后续安装的软件包是最新版本。

2.  **卸载旧版本（如果存在）**
    ```bash
    sudo apt-get remove -y docker docker-engine docker.io containerd runc
    ```
    **作用**：移除 Ubuntu 官方仓库中自带的旧版 Docker 相关软件包。这些旧版本通常更新滞后，功能不完整。

3.  **安装必要的依赖包**
    ```bash
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    ```
    **作用**：
    *   `ca-certificates`: 提供 SSL 证书，用于安全地通过 HTTPS 访问软件源。确保能安全访问 `https://download.docker.com`。
    *   `curl`: 用于从网络下载文件（如 GPG 密钥）。
    *   `gnupg`: 用于验证下载软件包的数字签名，确保软件来源可信，防止恶意篡改。
    *   `lsb-release`: 用于获取当前 Ubuntu 系统的版本代号（如 `noble`），以便添加正确的软件源。

### 📦 第二步：配置 Docker 官方软件源

这一步是规范安装的核心，它告诉你的系统从哪里下载 Docker。

1.  **创建密钥存储目录**
    ```bash
    sudo install -m 0755 -d /etc/apt/keyrings
    ```
    **作用**：创建一个专门用于存放 GPG 密钥的目录。这是新版 Ubuntu 推荐的做法，用于更好地管理软件源的密钥。
    该命令等于
    ```bash
    sudo mkdir -p /etc/apt/keyrings 
    sudo chmod 0755 /etc/apt/keyrings
    ```

2.  **添加 Docker 的官方 GPG 密钥**
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    ```
    **作用**：从 Docker 官方服务器下载 GPG 公钥并导入到你的系统中。`apt` 在安装软件时会使用这个密钥来验证软件包的完整性和真实性，这是保障系统安全的关键步骤。
    - -f：出错时不输出 HTML 错误页
    - -s：静默模式（不显示进度条）
    - -S：出错时显示错误
    - -L：如果 URL 重定向，自动跟随
    - -|：管道，把 `curl` 的输出传给 `gpg`
    - `--dearmor`：将 ASCII 格式的 GPG 密钥（文本）转换为**二进制格式**（.gpg 文件）
    - `-o ...`：输出到指定文件
    - a+r：给所有用户（`a` = all）添加**读权限**（`+r`）




3.  **添加 Docker 稳定版软件源**
    ```bash
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```
    **作用**：将 Docker 的官方软件源地址添加到你的系统配置中。
    *   `$(dpkg --print-architecture)`: 自动识别你的系统架构（如 `amd64`）。
    *   `$(lsb_release -cs)`: 自动获取你的 Ubuntu 版本代号。
    *   `stable`: 指定使用稳定版仓库，这是生产环境的首选。
或者使用
```shell

echo \

  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \

  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \

  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
- `. /etc/os-release`：加载系统信息文件（包含 `VERSION_CODENAME=jammy` 等
- echo "$VERSION_CODENAME"：输出 Ubuntu 代号，如：
- 20.04 → `focal`
- 22.04 → `jammy`
- 24.04 → `noble`
- **为什么不用 `lsb_release -cs`？**
  因为某些最小化安装的系统可能没装 `lsb-release` 包，而 `/etc/os-release` 是标准文件。
##### 🧩 `sudo tee ... > /dev/null`
- `tee`：从标准输入读取，并写入文件（同时可输出到屏幕）
- `sudo tee`：以 root 权限写入受保护目录 `/etc/apt/sources.list.d/`
- `> /dev/null`：丢弃 `tee` 的屏幕输出（保持安静）
> 📁 最终效果：创建文件 `/etc/apt/sources.list.d/docker.list`，APT 会自动读取它。
### 🚀 第三步：安装 Docker Engine

软件源配置好后，就可以像安装普通软件一样安装 Docker 了。

1.  **再次更新软件包索引**
    ```bash
    sudo apt-get update
    ```
    **作用**：让系统识别刚刚添加的 Docker 软件源，并获取其中的软件包列表。

2.  **安装 Docker 核心组件**
    ```bash
    sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin
    ```
    **作用**：
    *   `docker-ce`: Docker 社区版的核心引擎（守护进程）。
    *   `docker-ce-cli`: Docker 的命令行工具，你通过它来与 Docker 交互。
    *   `containerd.io`: 一个工业级的容器运行时，负责容器的启动、停止等生命周期管理。
    *   `docker-buildx-plugin`: 用于构建镜像的强大插件。
    *   `docker-compose-plugin`: 用于定义和运行多容器应用的插件（使用 `docker compose` 命令）。

### ⚙️ 第四步：安装后配置

安装完成后，进行一些必要的配置，让 Docker 更好用、更快。

1.  **启动并设置开机自启**
    ```bash
    sudo systemctl start docker
    sudo systemctl enable docker
    ```
    **作用**：立即启动 Docker 服务，并设置为随系统启动而自动启动。

2.  **配置非 root 用户权限（推荐）**
    默认情况下，执行 `docker` 命令需要 `sudo` 权限。为了方便，可以将你的用户添加到 `docker` 用户组。
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker
    ```
    **作用**：将当前用户（`$USER`）添加到 `docker` 组。`newgrp docker` 命令可以让组变更立即生效，无需重新登录。之后你就可以不加 `sudo` 直接运行 `docker` 命令了。
  - `newgrp` 会启动一个新的 shell 会话，并加载 `docker` 组,立即激活新组权限，无需重新登录。

3.  **配置国内镜像加速（国内用户必做）**
    由于网络原因，直接从 Docker Hub 拉取镜像会非常慢。配置国内镜像源可以极大提升速度。
    ```bash
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json << 'EOF'
    {
      "registry-mirrors": [
        "https://docker.m.daocloud.io",
        "https://docker.1panel.live", 
        "https://mirror.baidubce.com"
      ]
    }
    EOF
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    ```
    **作用**：创建或修改 Docker 的守护进程配置文件 `daemon.json`，添加国内的镜像加速器地址。配置后，Docker 会优先从这些更快的镜像源拉取镜像。

### ✅ 第五步：验证安装

最后，运行一个测试容器来确认 Docker 是否安装成功。

```bash
docker run hello-world
```
**作用**：这条命令会尝试从（已配置好的）镜像源拉取 `hello-world` 镜像，并创建一个容器运行它。如果看到 "Hello from Docker!" 的欢迎信息，就说明你的 Docker 已经成功安装并可以正常使用了。
