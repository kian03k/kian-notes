# 如何搭建一个简单的 MCP Server

> 本文从本项目 `MCP-SSE/main.py` 提炼而来，剥离全部业务逻辑，只保留"用 Python 搭一个能跑的 MCP Server"所需的最小骨架，供快速上手。

---

## 一、MCP 是什么（一句话）

**MCP（Model Context Protocol）** 是 Anthropic 提出的"大模型 ↔ 外部工具/数据"的开放协议。你可以把它理解成"AI 应用的 USB-C"：Server 端用统一格式暴露若干 **工具（Tool）**，任意支持 MCP 的客户端（Claude Desktop、Cursor、Cline 等）都能即插即用地调用它们，不用为每个模型单独对接。

我们要做的，就是写一个 **MCP Server**，对外暴露几个工具函数。

---

## 二、环境准备

| 项 | 要求 |
|---|---|
| Python | ≥ 3.10 |
| 依赖包 | `mcp`（官方 Python SDK，内含 FastMCP） |

```bash
# 建议固定版本，避免后续 breaking change
pip install "mcp>=1.0"
```

> 本项目 `requirements.txt` 里还混装了 `fastapi`、`loguru`、`dataclasses_json`，那些都是**业务代码**用到的，最小模板**不需要**。

---

## 三、最小可运行模板（完整代码）

下面是一个不到 30 行、复制即跑的 MCP Server。它暴露两个与业务无关的工具：查当前时间、简单计算器。

```python
# mcp_minimal_template.py
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# 1. 创建 Server 实例
mcp = FastMCP(
    "demo-server",       # 服务名称（会展示给客户端）
    host="0.0.0.0",      # 监听地址
    port=8000,           # 监听端口
    sse_path="/sse",     # 客户端用 EventSource 订阅的路径
    message_path="/messages/",  # 客户端 POST 消息的路径
)

# 2. 用装饰器注册工具 —— 一个工具 = 一个普通函数
@mcp.tool()
def get_current_time() -> str:
    """返回当前的日期和时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def calculate(a: float, b: float, operator: str) -> str:
    """简单计算器：支持 add / sub / mul / div"""
    ops = {"add": a + b, "sub": a - b, "mul": a * b}
    if operator == "div":
        return "错误：除数不能为零" if b == 0 else str(a / b)
    if operator in ops:
        return str(ops[operator])
    return f"错误：不支持的操作符 {operator}"

# 3. 启动服务
if __name__ == "__main__":
    mcp.run(transport="sse")
```

运行它：

```bash
python mcp_minimal_template.py
```

终端会打印类似 `Uvicorn running on http://0.0.0.0:8000`，Server 就起来了。

---

## 四、逐段讲解

### 1. `FastMCP(...)` —— 创建服务实例

`FastMCP` 是官方 SDK 提供的高层封装，把协议细节（JSON-RPC、能力协商、消息路由）全部藏掉，你只需关心"暴露哪些工具"。构造参数里：

- **`host` / `port`**：和写普通 Web 服务一样。
- **`sse_path` / `message_path`**：SSE 传输模式下两条通道的 URL。客户端通过 `sse_path` 建立长连接接收事件，通过 `message_path` 回传请求。一般保持默认即可，**不必改**。

### 2. `@mcp.tool()` —— 注册工具（核心）

这是整个模板最关键的一行。**一个 MCP 工具，就是一个带类型标注和 docstring 的普通 Python 函数**：

| 你写的 | MCP 自动做的 |
|---|---|
| 函数名 → 工具名 | 自动注册，客户端按名调用 |
| 参数类型标注 (`a: float`) | 自动转成 JSON Schema，告诉模型该传什么 |
| docstring (`"""..."""`) | 自动作为工具描述，模型靠它判断"何时该调这个工具" |
| `return` 值 | 自动序列化后回传给模型 |

> **写好 docstring 是 MCP 的精髓**：模型完全靠它来决定"该不该调这个工具、传什么参数"。描述越清晰，调用越准。本项目每个工具都写了中文 docstring，这一点值得借鉴。

### 3. `mcp.run(transport="sse")` —— 启动

`transport` 决定通信方式：

- **`sse`**：HTTP + Server-Sent Events，远程服务常驻，适合多人/多客户端共享。本项目用的就是这种。
- **`stdio`**：标准输入输出，客户端把 Server 当子进程拉起，适合本地单机（Claude Desktop 默认走 stdio）。
- **`streamable-http`**：2025-03 规范的新推荐，替代 sse（见下文"演进提示"）。

---

## 五、如何验证它能用

### 方式 A：MCP Inspector（官方 GUI 调试器，最直观）

```bash
npx @modelcontextprotocol/inspector
```

浏览器打开后，选择 Transport Type = **SSE**，填入 `http://localhost:8000/sse`，点 Connect。左侧会列出 `get_current_time` / `calculate` 两个工具，点进去填参数 → Run，右侧立刻看到返回。**这是排错最快的办法。**

### 方式 B：写几行客户端代码自测

```python
from mcp.client.sse import sse_client
from mcp import ClientSession

async def main():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("工具列表：", [t.name for t in tools.tools])
            res = await session.call_tool("calculate", {"a": 6, "b": 2, "operator": "mul"})
            print("计算结果：", res.content[0].text)

import asyncio
asyncio.run(main())
```

---

## 六、演进提示（避免踩坑）

本项目用的是 `transport="sse"`，这是 **2024 版规范**的写法。**2025-03-26 的新规范已把 SSE 标记为 deprecated**，推荐改用 `streamable-http`：

```python
# 新写法（需 mcp 较新版本）
mcp.run(transport="streamable-http")
```

- 旧客户端仍兼容 `sse`，**短期不影响使用**。
- 新项目建议直接上 `streamable-http`，一条通道更简单、更易穿透代理。

另外，本项目还用了 `from fastmcp.server.dependencies import get_http_headers` 读取自定义 HTTP 头——这属于**进阶用法**（从请求里拿用户身份等上下文），最小模板不需要。等你会跑基础工具后，再按需引入。

---

## 七、小结

搭一个能跑的 MCP Server，只需要三步：

1. `pip install "mcp>=1.0"`
2. `FastMCP(...)` 建实例
3. `@mcp.tool()` 给函数加装饰器 + 写好 docstring → `mcp.run()`

**记住一句话：在 MCP 里，一个工具就是一个带类型标注和 docstring 的函数，别的都是脚手架。**

会跑这个最小模板后，想系统学完整能力面（Resources / Prompts / Context / 结构化错误 / 流式输出），建议看官方仓库：
- `modelcontextprotocol/python-sdk` —— 官方 SDK 与示例
- `modelcontextprotocol/servers` —— Anthropic 维护的参考 Server 集
