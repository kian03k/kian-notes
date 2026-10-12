---
tags: [docker, linux, centos]
created: 2026-10-12
updated: 2026-10-12
status: ok
---



docker学习

参考文档

[‌‍‬⁠‌‍⁠﻿‬‌﻿﻿‍‍﻿⁠﻿‬﻿⁠‬‬﻿‬⁠‌‍‍‬安装Docker - 飞书云文档](https://b11et3un53m.feishu.cn/wiki/Rfocw7ctXij2RBkShcucLZbrn2d)

更换 CentOS 7 的 YUM 源为国内源是一个常见的操作，尤其是为了加速软件包的下载。

步骤 1：备份原有的 YUM 源文件
在更换 YUM 源之前，建议先备份系统自带的 YUM 源配置文件，以防需要恢复原配置。

sudo cp /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak

步骤 2：下载国内源的 YUM 配置文件
以下是一些常用的国内镜像源，你可以选择其中一个替换。

1. 阿里云源
sudo wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
2. 清华大学源
sudo wget -O /etc/yum.repos.d/CentOS-Base.repo https://mirrors.tuna.tsinghua.edu.cn/repo/Centos-7.repo
3. 网易源
sudo wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.163.com/.help/CentOS7-Base-163.repo
4. 中科大源
sudo wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.ustc.edu.cn/centos/7/os/x86_64/
步骤 3：清理 YUM 缓存
更换源之后需要清理原有的缓存，以便使用新的源进行软件包更新。

sudo yum clean all
sudo yum makecache
步骤 4：验证新源是否可用
更新完缓存后，可以检查 YUM 是否能正常工作，并确认使用的是新源。

sudo yum repolist
如果显示的源信息和你选择的国内源匹配，说明更换成功。

步骤 5：测试安装软件包
最后，可以尝试安装一个软件包来确认新的源是否工作正常。

sudo yum install vim -y
如果软件包安装顺利，则说明你的 YUM 源已经成功更换为国内源。

旧源恢复： 如果更换新源后遇到问题，可以使用备份的 .repo.bak 文件来恢复旧的 YUM 配置。
原文链接：https://blog.csdn.net/yxyc666/article/details/141705431



首先如果系统中已经存在旧的Docker，则先卸载：

```Shell
yum remove docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-engine \
    docker-selinux 
```



1. 安装依赖工具
   #使用 yum 安装必需的工具，yum-utils 提供了 yum 配置工具，device-mapper-persistent-data 和 lvm2 是 Docker 所需的依赖
   sudo yum install -y yum-utils device-mapper-persistent-data lvm2

2. 配置 Docker 的阿里云源
   使用 yum-config-manager 工具将阿里云的 Docker 镜像源添加到系统中
   sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

3. 替换默认源为阿里云源
   #使用 sed 命令替换 /etc/yum.repos.d/docker-ce.repo 文件中的默认 Docker 官方源地址为阿里云的镜像源
   sudo sed -i 's+download.docker.com+mirrors.aliyun.com/docker-ce+' /etc/yum.repos.d/docker-ce.repo

4. 更新并生成 yum 缓存
   #更新 yum 缓存，这样在安装 Docker 时能加速并避免从原始源下载
   sudo yum makecache fast

安装Docker

```Bash
yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```Bash
# 启动Docker
systemctl start docker

# 停止Docker
systemctl stop docker

# 重启
systemctl restart docker

# 设置开机自启
systemctl enable docker

# 执行docker ps命令，如果不报错，说明安装启动成功
docker ps
```

阿里云镜像加速

产品-容器-容器镜像服务ACR-管理控制台-镜像工具-镜像加速器-每个人都不同

https://0o9i9hxn.mirror.aliyuncs.com

```
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://0o9i9hxn.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

```



mysql安装

```PowerShell
docker run -d \
  --name mysql \
  -p 3306:3306 \
  -e TZ=Asia/Shanghai \
  -e MYSQL_ROOT_PASSWORD=123 \
  mysql
```

-d进程后台运行

-e环境变量

-p:端口映射，前面为宿主机端口，即虚拟机端口，外界访问的端口。后面为容器运行的端口。

mysql完整应该跟版本号mysql:5.1。
