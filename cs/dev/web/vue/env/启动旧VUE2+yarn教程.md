# 已装 Node + pnpm，旧 Vue2 + Yarn 项目启动完整教程
我给你一套**零坑、直接照做**的步骤，完全适配你现在的环境（有 node、pnpm，项目是 yarn + vue2）。

## 第一步：先进入项目根目录
打开终端，**cd 到你的项目文件夹**（必须是有 `package.json` 的那一层）
```bash
cd 你的项目路径
```

---

## 第二步：清理旧依赖（必做，防止报错）
旧项目的 `node_modules` 和锁文件会导致启动失败，先删掉：
```bash
# 删除依赖包文件夹
rm -rf node_modules

# 删除 yarn 锁文件
rm -f yarn.lock

# 删除可能存在的 npm 锁文件（有的话）
rm -f package-lock.json
```

---

## 第三步：用 pnpm 重新安装依赖
你现在有 pnpm，**直接用 pnpm 装**，比 yarn 更快更稳定，兼容 Vue2：
```bash
pnpm install
```
等待安装完成（出现 `Done` 就 OK）。

---

## 第四步：启动项目（Vue2 最常用命令）
直接运行：
```bash
pnpm run dev
```
✅ 如果不行，就试下面这两个（Vue2 最常见启动命令）：
```bash
pnpm run serve
# 或
pnpm run start
```

---

## 最稳方案：看 package.json 确认启动命令
打开项目里的 `package.json`，找到 **scripts** 部分：
```json
"scripts": {
  "dev": "webpack-dev-server --inline --progress --config build/webpack.dev.conf.js",
  "serve": "vue-cli-service serve",
  "build": "node build/build.js"
}
```
- 有 `dev` → 运行 `pnpm run dev`
- 有 `serve` → 运行 `pnpm run serve`

---

## 常见报错 1 分钟解决
### 1. 报错：node 版本太高
Vue2 不支持 Node 18+ / 20+ 新版，解决方法：
```bash
# 临时降低兼容性（不用改 node 版本）
pnpm config set ignore-scripts false
pnpm install --legacy-peer-deps
```
然后再启动：`pnpm run dev`

### 2. 报错：Missing modules
重新装一遍就行：
```bash
rm -rf node_modules
pnpm install
```

### 3. 端口被占用
```bash
pnpm run dev --port 8081
```

---

## 最终最简总结（你可以只记这个）
1. `cd 项目目录`
2. `rm -rf node_modules yarn.lock`
3. `pnpm install`
4. `pnpm run dev` 或 `pnpm run serve`

---

### 总结
- 你有 Node + pnpm 完全能跑旧 Vue2 + Yarn 项目
- 不用装 Yarn，**pnpm 直接替代**
- 核心四步：进目录 → 清旧依赖 → 重装 → 启动
- 启动命令看 `package.json` 的 `scripts`

如果你愿意，我可以帮你**直接看你的项目结构**，告诉你该敲哪一条命令就能跑起来～