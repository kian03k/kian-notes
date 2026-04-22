# python联调
这是一个非常经典的开发场景！你的架构现在是这样的：

*   **数据库层**：MySQL 运行在 WSL2 (Docker) 中。
*   **应用层**：Python 代码也运行在 WSL2 中（比如你通过 VS Code Remote-WSL 或者直接在终端运行脚本）。
*   **客户端层**：Windows 宿主机（你想用 Windows 上的软件来管理数据）。

好消息是，得益于 WSL2 的自动端口转发机制，这三者之间的连接非常顺畅，几乎不需要复杂的网络配置。

以下是具体的实现方案：

### 1. Python 代码如何连接 MySQL（应用层连接）

**场景**：你的 Python 脚本运行在 WSL2 的终端里。
**原理**：因为 Python 和 MySQL 都在同一个 WSL2 系统内部，它们就像在同一台电脑上。

#### 第一步：安装驱动
在 WSL2 的终端中，进入你的 Python 环境，安装 `pymysql`（目前 Python 生态中最流行的纯 Python 驱动，安装简单，兼容性好）：

```bash
pip install pymysql
```

#### 第二步：编写连接代码
在你的 Python 代码中，`host` 直接填 `localhost` 或 `127.0.0.1` 即可。

```python
import pymysql

# 建立连接
# 因为 Python 和 Docker 都在 WSL2 内部，所以直接用 localhost
connection = pymysql.connect(
    host='localhost',       # 或者 '127.0.0.1'
    user='root',            # 你的数据库用户名
    password='MyStrongPassword123!', # 你的数据库密码
    database='app_db',      # 你的数据库名
    charset='utf8mb4',      # 推荐使用 utf8mb4 支持中文和表情符号
    cursorclass=pymysql.cursors.DictCursor # 让查询结果以字典形式返回，方便处理
)

try:
    with connection.cursor() as cursor:
        # 执行 SQL
        sql = "SELECT VERSION()"
        cursor.execute(sql)
        result = cursor.fetchone()
        print(f"数据库版本: {result}")
        
        # 插入数据示例
        # insert_sql = "INSERT INTO users (name, age) VALUES (%s, %s)"
        # cursor.execute(insert_sql, ('Alice', 25))
        
    # 提交事务（如果是增删改操作）
    connection.commit()
    
finally:
    # 关闭连接
    connection.close()
```

**关键点**：
*   **Host**：填 `localhost`。因为 WSL2 的端口转发机制，你在 WSL2 里访问 `localhost:3306`，实际上会被转发到 Docker 容器的 3306 端口。
*   **端口**：保持默认的 `3306`。

---

# Windows 本地推荐什么软件连接（客户端层连接）

既然你的数据库在 WSL2 里，但你想用 Windows 的图形界面工具来管理，推荐以下几款软件。它们都能通过 `localhost` 直接连上 WSL2 里的 MySQL。

#### 推荐一：DataGrip (JetBrains 出品) —— **专业首选**
如果你是 PyCharm 或 IntelliJ IDEA 的用户，DataGrip 是最强的选择（也可以单独下载，或者用 PyCharm 自带的数据库插件）。
*   **优点**：智能提示极强，支持多种数据库，界面统一。
*   **连接配置**：
    *   **Host**: `localhost`
    *   **Port**: `3306`
    *   **User**: `root`
    *   **Password**: `MyStrongPassword123!`
*   **原理**：DataGrip 运行在 Windows 上，当你填 `localhost` 时，WSL2 会自动把 Windows 的流量转发进去。

#### 推荐二：HeidiSQL —— **轻量免费**
这是 Windows 上非常老牌且轻量的 MySQL 客户端，免费且速度快。
*   **优点**：启动秒开，功能实用，完全免费。
*   **连接配置**：
    *   **网络类型**: MySQL (TCP/IP)
    *   **主机名**: `localhost`
    *   **端口**: `3306`

#### 推荐三：DBeaver —— **开源全能**
如果你除了 MySQL 还会用到 PostgreSQL、SQLite 等其他数据库，DBeaver 是最佳免费替代品。
*   **优点**：社区版免费，支持几乎所有数据库，跨平台。

---

### 3. 架构全景图解

为了让你彻底放心，这是数据流向图：

```mermaid
graph TD
    subgraph Windows宿主机
        A[Python代码 (运行在WSL2终端)]
        B[DataGrip/HeidiSQL (Windows软件)]
    end

    subgraph WSL2系统
        C[WSL2 虚拟网卡]
        D[Docker 引擎]
        E[MySQL 容器 (端口 3306)]
    end

    A -- "连接 localhost:3306" --> C
    B -- "连接 localhost:3306" --> C
    C -- "自动端口转发" --> D
    D -- "映射端口" --> E
```

### 4. 常见问题排查

如果你发现 Windows 上的软件连不上（报错 `Can't connect to MySQL server`）：

1.  **检查 Docker 是否运行**：
    在 WSL2 里输入 `docker ps`，确保 MySQL 容器是 `Up` 状态。
2.  **检查端口映射**：
    确保你的 `docker-compose.yml` 里写了 `ports: - "3306:3306"`。
3.  **防火墙（极少见）**：
    通常 WSL2 内部没有防火墙阻拦，但如果连不上，可以尝试在 Windows 上重启 WSL：
    ```powershell
    # 在 Windows PowerShell 中执行
    wsl --shutdown
    # 然后重新打开 WSL 终端，再次启动 docker compose up -d
    ```

**总结**：
*   **代码里**：用 `pymysql`，Host 写 `localhost`。
*   **软件里**：推荐 **DataGrip** 或 **HeidiSQL**，Host 写 `localhost`。
*   **核心**：WSL2 会自动帮你搞定网络转发，你只需要把它当成一台普通的 Linux 服务器即可。


# jetbrains连接 WSL2 + Docker MySQL 教程

下面给你一套**最简单、一次成功**的 PyCharm 连接 WSL2 + Docker MySQL 教程，全程不用碰复杂 IP，不用猜地址。

## 前提（你已经满足）
- Docker 容器正常运行：`mysql-prod`
- 端口映射：`3306:3306`
- 密码你已经设置好

---

## 一、先确认两件事（非常重要）
1. 你的 MySQL 端口是 **3306**（你配置里写的就是）
2. 容器已经正常运行
```bash
docker ps
```
看到 `mysql-prod` 并且端口 `0.0.0.0:3306->3306/tcp` 就 OK。

---

## 二、PyCharm 连接步骤（Database 工具）

### 1. 打开 Database 面板
右侧边栏 → **Database**
没有的话：
`View → Tool Windows → Database`

### 2. 添加数据源
`+ → Data Source → MySQL`

### 3. 填写连接信息（**直接照抄**）
- **Host**: `localhost`
- **Port**: `3306`
- **User**: `root`
- **Password**: 你设置的密码（如 `MyStrongPassword123!`）
- **Database**: `app_db`（你配置里自动建的库，不填也能连）

### 4. 重点：驱动下载
第一次会提示 **Download missing driver files**
点一下自动下载，等待完成。

### 5. 测试连接
点 **Test Connection**
出现 **Succeeded** 就成功了！

### 6. 应用 → OK
完事。

---

## 三、为什么连 localhost 就行？
因为你在 `docker-compose.yml` 里写了：
```yaml
ports:
  - "3306:3306"
```
这表示：
**把容器 3306 映射到 Windows 本机 3306**

所以：
- Windows/PyCharm → `localhost:3306`
- 自动转发 → WSL2 → Docker MySQL

**不用填 WSL IP，不用填容器 IP，永远 localhost 就行。**

---

## 四、如果连不上，99% 是这 3 个原因
### 1. 密码不对
解决：重新进容器改密码，或删掉 ./data 重新初始化。

### 2. MySQL 不让 root 远程登录（新版 MySQL8 常见）
进容器执行：
```bash
docker exec -it mysql-prod mysql -uroot -p
```
然后执行：
```sql
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '你的密码';
FLUSH PRIVILEGES;
```

### 3. 端口被占用
改成：
```yaml
ports:
  - "3307:3306"
```
然后 PyCharm 端口填 3307。

---

## 五、一句话总结
**PyCharm 连 WSL2 里的 Docker MySQL，直接填 localhost:3306 + root + 密码即可。**

需要我帮你排查连接报错吗？把报错截图/文字发我，我直接告诉你怎么修。
