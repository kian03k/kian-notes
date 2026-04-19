# WSL2 与 Git 项目规范化管理指南
（优化凝练版，可直接保存使用）

## 一、开源协议选择
- 个人学习/练手/展示类项目优先使用 **MIT License**
- 特点：宽松开源、版权明确、无法律风险、职场观感专业

### 添加方式
1. 进入 GitHub 仓库
2. 点击 `Add file → Create new file`
3. 文件名填写 `LICENSE`
4. 右侧选择 `Choose a license template`
5. 选用 `MIT License` 并提交

## 二、多模块项目管理
- 前后端分离项目：**前后端拆分为独立 Git 仓库**
- 多服务/微服务项目：**每个服务独立建仓**
- 优势：结构清晰、便于部署、符合工业界规范

### 仓库组织方式
- 使用 **GitHub Organization（组织）**
- 或使用 **Repository Collection（收藏集）**
- 按业务线分组，主页整洁、便于展示与检索

## 三、仓库命名规范
统一规则：**英文小写、短横线分隔、无中文、无特殊符号**

1. 项目名 + 技术栈
   - `music-server-flask`、`music-web-vue`、`todo-list-springboot`
2. 项目名 + 前后端标识
   - `shop-frontend`、`shop-backend`、`movie-api`
3. 简洁通用型
   - `music-platform`、`blog-system`、`ai-chatbot`

## 四、GitHub 仓库大小限制
- 单个文件硬限制：**100MB**，超出无法上传
- 推荐单仓库体积：**< 1GB**
- 软限制：**5GB**，超出会收到提醒
- 硬限制：**10GB**，常规项目几乎不会触及

## 五、WSL2 项目目录结构
### 推荐根路径
```
/home/你的用户名/workspace/
```

### 标准目录结构
```
workspace/
├── demos/            # 小练习、语法测试、课程作业
│   ├── cpp/
│   ├── java/
│   ├── python/
│   └── web/
│
├── projects/         # 完整可上传 GitHub 的项目
│   ├── music-platform/
│   │   ├── frontend/  # Vue 前端
│   │   └── backend/   # Flask 后端
│   ├── blog-system/
│   └── ai-demo/
│
└── private/           # 私密文件，不上传 Git
    ├── docs/
    ├── notes/
    └── assets/
```

## 六、WSL2 + Git 使用铁律
**核心原则：项目在哪，就用哪的 Git，不交叉、不混用**

1. 项目位于 WSL2 `/home/xxx`
   - 使用：**WSL2 终端（bash）** 操作 Git
   - 禁止：Git Bash / PowerShell 操作
   - 原因：避免权限错乱、符号链接破坏、Git 索引异常

2. 项目位于 Windows `C:/D:/`
   - 使用：Git Bash / PowerShell
   - 不建议：WSL2 通过 `/mnt/c` 操作 Git（性能极差）

## 七、资源与隐私数据管理
- 代码与工程文件：放入 WSL2 `/home/xxx/workspace`
- 密钥、配置、私人文档：放入 `workspace/private`
- PPT/Excel 等业务资料：存放于 Windows 目录
- 项目内可建立
  ```
  docs/resource-links.md
  ```
  用于记录资源路径、参考资料，避免敏感信息入 Git

## 八、为什么项目必须放在 WSL2 内部
- WSL2 为虚拟机架构，`/home` 为原生 ext4 文件系统，性能接近真机 Linux
- `/mnt/c` 基于 9P 协议转发，大量小文件场景性能下降 **10~50 倍**
- Git、npm、maven、编译、AI 工程等强 IO 操作必须放在 WSL2 内

---
