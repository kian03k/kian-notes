---
tags: [git, 速查]
created: 2026-11-16
updated: 2026-11-16
status: ok
---

# git-lfs

Git LFS（Large File Storage）把大文件的实际内容从 Git 对象库搬到独立存储，仓库里只留指针。要理解它，关键是分清**两个独立系统**：Git 本体和 LFS 传输层用的是不同协议、不同地址、不同证书校验。

## 一、机制

```text
仓库中的文件只是一段指针：
version https://git-lfs.github.com/spec/v1
oid sha256:4d7a2146...
size 12345
```

克隆时默认只取指针，`checkout` 或 `lfs pull` 时才按 oid 去 LFS 服务器下载真实内容。

存量的代价：Git 对每个文件保存全量快照，一个 50MB 的二进制改 20 次就是 1GB，且所有 clone 的人都要拉全量。这是 LFS 存在的唯一理由。

## 二、LFS 走 HTTPS，与 SSH 无关（核心知识点）

| 组件 | 负责 | 协议 |
| --- | --- | --- |
| Git 本体 | 提交、分支、指针文件 | SSH / HTTPS / git |
| Git LFS | 大文件内容传输 | **仅 HTTP(S) API** |

所以会出现「SSH 克隆成功，但大文件下不下来」的现象：

```text
git clone git@<host>:<owner>/<repo>.git     ← 只拿到指针
git lfs fetch                                ← 实际访问下面这个地址
https://<host>/<owner>/<repo>.git/info/lfs/objects/batch
```

这个 HTTPS 地址由服务器端决定，**跟你 remote 用的是 `git@` 还是 `https://` 没有关系**。确认实际地址：

```bash
git lfs env | grep -i url
```

推论：SSH 免密通过 ≠ LFS 能下载。LFS 的 TLS 校验是独立的一套。

## 三、从零接入

```bash
git lfs install                # 每用户一次，安装 hook
git lfs track "*.xlsx"         # 声明跟踪模式，写入 .gitattributes
git add .gitattributes         # 规则本身必须提交，否则别人 clone 后不生效
git add big.xlsx
git commit -m "chore: LFS 管理 xlsx"
git push
```

`.gitattributes` 生成内容：

```gitattributes
*.xlsx filter=lfs diff=lfs merge=lfs -text
```

`-text` 不可省——它禁用换行符转换，否则二进制文件会被 CRLF 转换破坏。

## 四、`.gitattributes` 不追溯已提交文件

最容易出错的一点：**给已提交的文件加上 LFS 规则，不会把历史里的内容迁走**。规则只对「之后的提交」生效，旧对象仍完整躺在 Git 对象库里，仓库体积一点没减。

### 不追溯的原因

LFS 的设计是追加式的：改写历史需要重写所有相关提交的 SHA，属于高风险操作，因此不做自动处理。

### 迁移历史：`git lfs migrate`

```bash
git lfs migrate import --include="*.xlsx" --include="*.psd" --everything
```

| 参数 | 含义 |
| --- | --- |
| `--include` | 路径模式，可重复 |
| `--everything` | 处理所有分支和标签；不加则只处理当前分支 |
| `--exclude` | 排除项 |

`migrate` 会重写提交、变更 SHA，所以完整流程是：

```bash
git branch backup-$(date +%Y%m%d)        # 1. 留后路
git lfs migrate import --include="*.xlsx" --everything
git lfs ls-files                          # 2. 验证已进 LFS
git push --force-with-lease --all         # 3. 推所有分支
git push --force-with-lease --tags        # 4. 推所有标签
```

协作者必须重新 clone（或 `git fetch --all` 后 `git reset --hard origin/<branch>`），否则他们的本地历史与远端彻底分叉。

### 只处理尚未推送的提交

```bash
git lfs track "*.xlsx"
git add .gitattributes big.xlsx
git commit --amend --no-edit
git push
```

不必动 `migrate`。

## 五、企业自签证书导致的 LFS 失败

典型症状：`git clone` 正常（走 SSH），`git lfs fetch` 报 SSL 证书错误；同一份仓库在别人机器上没问题。

原因是 LFS 的 HTTPS 端点用了内部 CA 签发的证书，客户端系统证书库不认。**这不是 LFS 的 bug，是 PKI 配置问题。**

处理顺序：

1. **装根 CA（正解）**：从 IT 获取内部根证书（`.crt` / `.pem`），导入「受信任的根证书颁发机构」（Windows：双击证书 → 安装到本地计算机 → 受信任的根证书颁发机构），重启终端。
2. **只让 Git 信任指定证书**（不动系统证书库）：

   ```bash
   git config --global http.sslCAInfo "C:/certs/internal-ca.crt"
   ```

   证书可从浏览器导出：访问该域名 → 地址栏锁图标 → 证书 → 详细信息 → 复制到文件 → 选 **Base64 编码**（DER 格式 Git 用不了）。

3. **临时关闭校验**（仅排障）：

   ```bash
   git config --global http.sslVerify false
   ```

   关闭后所有 HTTPS 操作失去中间人防护，**排障完必须改回 `true`**，不要留在配置里。

验证：

```bash
GIT_TRACE=1 GIT_CURL_VERBOSE=1 git lfs fetch
# 能看到 batch 请求返回 200 即通
```

团队层面避免复发：README 写明「本项目使用 LFS，请先安装内部根证书」，或把根证书放进仓库并提供安装脚本。

## 六、常用命令

| 目的 | 命令 |
| --- | --- |
| 看跟踪规则 | `git lfs track`（不带参数） |
| 看已被 LFS 管理的文件 | `git lfs ls-files` |
| 看 LFS 端点地址 | `git lfs env` |
| 拉全部大文件 | `git lfs fetch --all` / `git lfs pull` |
| 只拉指定文件 | `git lfs pull --include="models/*.bin"` |
| 清理本地缓存 | `git lfs prune` |
| 取消跟踪 | `git lfs untrack "*.xlsx"` |

## 七、与 `.gitignore` 的分工

| 需求 | 手段 |
| --- | --- |
| 不该进仓库（缓存、数据集、`.env`） | `.gitignore` |
| 要进仓库但太大 | LFS |
| 曾经进过仓库，现在要排除 | `git rm --cached` + `.gitignore`，见 [[gitignore常见问题]] |

## 八、关联

- 完整接入流程：[[06-大文件与LFS]]
- SSH 多账号与密钥：[[01-环境与身份配置]]
- 误提交大文件后的清理：[[07-故障恢复]]
