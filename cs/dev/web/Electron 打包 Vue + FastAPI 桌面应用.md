---
tags: [web, 踩坑]
created: 2026-11-15
updated: 2026-11-15
status: review
---

# Electron 打包 Vue + FastAPI 为 Windows 桌面应用

> 本篇为方案整理，代码结构依据 Electron 24+ / electron-builder 24+ 文档与本机踩坑记录，未做端到端实测。首次落地时请以下文"坑清单"逐条验证。

## 路线选择

后端是 Python 进程，无法编译进前端静态资源，必须由 Electron 在主进程里拉起。前端页面的加载方式有两种，必须先二选一，两套混用必有跨域或路径问题。

| | A：后端托管前端 | B：Electron 载入本地文件 |
|---|---|---|
| 页面来源 | `http://127.0.0.1:<port>/` | `file://.../dist/index.html` |
| 后端需挂载 | `StaticFiles(directory="dist", html=True)` | 不需要 |
| 跨域 | 同源，无需处理 | `file://` 的 Origin 为 `null`，需后端放行或关闭 `webSecurity` |
| 打包路径 | 简单 | `publicPath` 必须为 `./`，资源路径易错 |
| 推荐 | **是** | 仅在需要极简后端时考虑 |

下文按 A 展开。

## 项目结构

```
app/
├── frontend/              # Vue 项目
│   └── dist/              # npm run build 产物，由 FastAPI 托管
├── backend/
│   ├── main.py
│   └── requirements.txt
├── main.js                # Electron 主进程
├── preload.js
└── package.json
```

`vue.config.js` 只需一行 `publicPath: './'`，其余保持默认。

后端挂载静态目录时注意顺序——`StaticFiles` 挂在 `/` 会吞掉后续路由，必须先注册 API 路由，再挂载：

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api/data")
def get_data():
    return {"data": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/", StaticFiles(directory="dist", html=True), name="static")
```

## 主进程

原稿的两个版本各有一半问题：第一版等日志匹配才加载页面（字符串匹配不稳定），第二版先 `loadFile` 再 `spawn`（后端起不来就白屏）。正确做法是**动态端口 + HTTP 健康探测 + 探测通过再加载**。

```js
const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const net = require('net');
const http = require('http');
const fs = require('fs');
const { spawn } = require('child_process');

let win = null;
let api = null;
let apiPort = null;

function freePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on('error', reject);
    srv.listen(0, '127.0.0.1', () => {
      const port = srv.address().port;
      srv.close(() => resolve(port));
    });
  });
}

function waitFor(url, timeoutMs = 30000) {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve, reject) => {
    const probe = () => {
      const req = http.get(url, (res) => { res.resume(); resolve(); });
      req.on('error', () => {
        if (Date.now() > deadline) return reject(new Error(`后端在 ${timeoutMs} ms 内未就绪`));
        setTimeout(probe, 300);
      });
      req.setTimeout(1000, () => req.destroy());
    };
    probe();
  });
}

function killTree(pid) {
  if (!pid) return;
  if (process.platform === 'win32') {
    spawn('taskkill', ['/pid', String(pid), '/T', '/F'], { stdio: 'ignore' });
  } else {
    process.kill(-pid, 'SIGTERM');
  }
}

async function startBackend() {
  apiPort = await freePort();

  const isPackaged = app.isPackaged;
  const backendDir = isPackaged
    ? path.join(process.resourcesPath, 'backend')
    : path.join(__dirname, 'backend');

  // 生产环境启动 PyInstaller 产物，开发环境用系统解释器
  const cmd = isPackaged ? path.join(backendDir, 'server.exe') : 'python';
  const args = isPackaged ? [] : ['-m', 'uvicorn', 'main:app',
    '--host', '127.0.0.1', '--port', String(apiPort)];

  const logDir = path.join(app.getPath('userData'), 'logs');
  fs.mkdirSync(logDir, { recursive: true });
  const logStream = fs.createWriteStream(path.join(logDir, 'backend.log'), { flags: 'a' });

  api = spawn(cmd, args, {
    cwd: backendDir,
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  api.stdout.pipe(logStream);
  api.stderr.pipe(logStream);

  api.on('error', (err) => {
    dialog.showErrorBox('后端启动失败', err.message);
    app.quit();
  });

  await waitFor(`http://127.0.0.1:${apiPort}/health`);
}

async function createWindow() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  try {
    await startBackend();
    win.loadURL(`http://127.0.0.1:${apiPort}/`);
  } catch (err) {
    dialog.showErrorBox('启动失败', `本地服务未能就绪：${err.message}`);
    app.quit();
  }

  win.on('closed', () => { win = null; });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => killTree(api && api.pid));
```

三个关键点：

1. **端口不能写死。** `listen(0)` 由内核分配空闲端口，规避 8000 被占用导致整个应用报废。
2. **健康探测优于日志匹配。** 后端就绪的可靠信号是 `/health` 可访问，而不是 stdout 里出现某句日志——日志格式会随 uvicorn 版本变化。
3. **Windows 必须杀进程树。** `api.kill()` 只能杀掉直接子进程；uvicorn 在 `--reload` 或 PyInstaller 单文件模式下还有孙进程，残留会一直占着端口。

## 打包配置

```json
{
  "appId": "com.example.app",
  "productName": "MyApp",
  "directories": { "output": "build" },
  "files": ["main.js", "preload.js", "dist/**/*"],
  "extraResources": [{ "from": "backend/dist", "to": "backend" }],
  "win": { "target": ["nsis"], "icon": "build/icon.ico" },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true
  }
}
```

**后端产物必须走 `extraResources`，不能放进 `files`。** `files` 的内容最终打进 `app.asar`，而 asar 里的可执行文件无法被 `spawn` 直接运行。`extraResources` 会原样复制到 `resources/`，配合主进程里的 `process.resourcesPath` 才能取到。

同理，`files` 与 `extraResources` 不要同时包含 `backend/`，原稿的配置两份都写了，属于冗余且会放大安装包体积。

## 后端打包

```bash
pip install pyinstaller
cd backend
pyinstaller --onedir --name server \
  --collect-submodules uvicorn \
  --collect-submodules pydantic \
  main.py
```

要点：

- **用 `--onedir` 而不是 `--onefile`。** 单文件模式每次启动要把自身解压到临时目录，启动慢且极易被杀毒软件误报；`--onedir` 目录形式更稳，配合 `extraResources` 也更好管理。
- **不要加 `--windowed`（`--noconsole`）。** 后端进程一旦崩溃，没有任何日志可查。需要隐藏控制台时，把 stdout/stderr 重定向到日志文件（上文主进程已实现），而不是把控制台关掉。
- **显式声明隐式依赖。** uvicorn、pydantic 大量使用动态导入，PyInstaller 的静态分析抓不全，必须用 `--collect-submodules` 补齐，否则打包后启动即 `ModuleNotFoundError`。
- **资源路径会变。** 代码里凡是 `open(...)`、`Path(__file__).parent` 的路径，在冻结后指向 `sys._MEIPASS`，需要按 `getattr(sys, 'frozen', False)` 分支处理。

## 坑清单

| 现象 | 原因 | 处理 |
|---|---|---|
| 打开即白屏，接口全 404 | 页面加载早于后端就绪 | 健康探测通过后再 `loadURL` |
| 第二次启动报端口占用 | 上次退出残留后端进程 | `taskkill /T /F` 杀进程树 |
| `file://` 页面请求接口被拦 | Origin 为 `null` 触发 CORS | 改用路线 A；或后端放行 `null` |
| 打包后 `spawn ENOENT` | 后端 exe 被打进 asar | 改用 `extraResources` |
| 打包后 `ModuleNotFoundError` | PyInstaller 漏抓动态导入 | `--collect-submodules` |
| 杀毒软件报毒 | `--onefile` 自解压 | 改 `--onedir`，或做代码签名 |
| 用户机器没装 Python | 直接 `spawn('python')` | 生产环境只发布 PyInstaller 产物 |

## 相关

- [[Vue3基础与组合式API]]
- [[pyinstaller]]
