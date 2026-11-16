---
tags: [git]
created: 2026-11-16
updated: 2026-11-16
status: ok
---

# 06 · 大文件与 LFS

> 第 6 环。目标：让二进制大文件（模型权重、xlsx、视频、设计稿）不进主仓库的对象库，同时搞清楚 LFS 的传输链路和证书问题。

## 6.1 为什么需要 LFS

Git 对每个文件存全量快照（不是增量 diff）。一个 50MB 的 xlsx 改 20 次，仓库里就躺着 1GB。而且 clone 时**所有人都要把这些全量拉下来**。

LFS（Large File Storage）的做法：仓库里只存一个几百字节的**指针文件**，真实内容放在独立的 LFS 存储上，按需下载。

```text
仓库中的文件内容：
version https://git-lfs.github.com/spec/v1
oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
size 12345
```

## 6.2 从零接入

```bash
git lfs install                 # 每个用户执行一次，装 hook
cd /path/to/repo
git lfs track "*.xlsx"          # 声明要跟踪的类型
git lfs track "*.psd" "*.mp4"
git add .gitattributes          # 关键：跟踪规则本身必须提交
git add data.xlsx
git commit -m "chore: 启用 LFS 管理 xlsx"
git push
```

`.gitattributes` 会被写成：

```gitattributes
*.xlsx filter=lfs diff=lfs merge=lfs -text
```

`-text` 是必须的，它告诉 Git 不要对这些文件做换行符转换，否则二进制会被破坏。

## 6.3 最容易误解的一点：`.gitattributes` 不追溯

**给已有提交里的文件加上 LFS 规则，不会自动把它迁到 LFS。** 规则只作用于「之后发生的提交」，历史里的旧对象原样躺在仓库里。

想让历史中的文件也迁走，必须重写历史：

```bash
git lfs migrate import --include="*.xlsx" --everything
```

| 参数 | 含义 |
| --- | --- |
| `--include` | 要迁移的路径模式，可写多个 |
| `--everything` | 所有分支和标签都处理；不加则只处理当前分支 |
| `--exclude` | 排除项 |

这个命令**重写提交、变更所有相关 SHA**，因此：

1. 执行前必须 `git branch backup-$(date +%Y%m%d)` 或整仓再 clone 一份。
2. 推送到远端要 `git push --force-with-lease --all` 和 `--tags`。
3. 所有协作者必须重新 clone（或 `git fetch --all` 后 `git reset --hard origin/<branch>`），否则他们的本地历史和远端彻底分叉。

只想处理「刚提交还没推」的文件时不必 migrate，用 amend 即可：

```bash
git lfs track "*.xlsx"
git add .gitattributes data.xlsx
git commit --amend --no-edit
```

## 6.4 LFS 走 HTTPS，不走 SSH

这是排查 LFS 问题时最反直觉的一点：

| 组件 | 负责 | 可用协议 |
| --- | --- | --- |
| Git 本体 | 提交、分支、指针文件 | SSH / HTTPS / git |
| Git LFS | 大文件的实际内容 | **仅 HTTP(S) API** |

所以：**用 SSH 克隆成功，不等于大文件能下载下来。** `git clone` 只拿到指针，真正取内容时 LFS 会去访问：

```text
https://<git服务器域名>/<owner>/<repo>.git/info/lfs/objects/batch
```

这个地址由服务器决定，与你的 remote 是 `git@` 还是 `https://` 无关。确认实际地址：

```bash
git lfs env | grep -i url
```

推论：**LFS 的证书校验是独立的**，SSH 免密通过不代表 LFS 能下。企业自建 Git 服务常用内部 CA 签发的证书，客户端没装该根证书时，表现就是 `git clone` 正常、`git lfs fetch` 报 SSL 错误。

### 证书问题的通用处理顺序

1. **装企业根 CA（正解）**：向 IT 索取内部根证书（`.crt` / `.pem`），双击导入「受信任的根证书颁发机构」，重启终端。
2. **只让 Git 信任指定证书**（不动系统证书库）：

   ```bash
   git config --global http.sslCAInfo "C:/certs/internal-ca.crt"
   ```

3. **关校验（仅临时排障）**：`git config --global http.sslVerify false`。这会让所有 HTTPS 操作失去中间人防护，**排障完必须改回来**，不要当成长期方案。

验证是否走通：

```bash
GIT_TRACE=1 GIT_CURL_VERBOSE=1 git lfs fetch
# 期望看到 HTTP/1.1 200 OK 和 batch 请求返回
```

## 6.5 常用命令

| 目的 | 命令 |
| --- | --- |
| 看当前跟踪规则 | `git lfs track`（不带参数） |
| 看哪些文件已被 LFS 管理 | `git lfs ls-files` |
| 看 LFS 服务器地址 | `git lfs env` |
| 补拉全部大文件 | `git lfs fetch --all` / `git lfs pull` |
| 只下载指定文件 | `git lfs pull --include="models/*.bin"` |
| 清理本地 LFS 缓存 | `git lfs prune` |
| 停用某类跟踪 | `git lfs untrack "*.xlsx"` |

## 6.6 注意事项

- **LFS 空间通常单独计费/限容**。GitHub 免费额度有限，大模型权重建议放对象存储，仓库里只留下载脚本。
- **不要把已经是大文件的历史硬迁进 LFS 再指望仓库变小**：`migrate` 后还需要协作者重新 clone，旧对象才会真正从他们的本地消失。
- **`.gitignore` 与 `.gitattributes` 分工**：不该进仓库的（数据集、缓存）用 ignore 排除；该进但要省空间的用 LFS。
- 用 LFS 的仓库，README 里应写明「本项目使用 Git LFS，clone 前请确保 `git lfs install`」，否则新人 clone 下来只有一堆指针文件。

机制细节与更多排查见 [[git-lfs]]。

## 6.7 本章检查清单

- [ ] `git lfs install` 已执行
- [ ] 跟踪规则写进了 `.gitattributes` 并已提交
- [ ] 已提交的历史文件，要么接受现状，要么用 `migrate` 并通知协作者
- [ ] 知道 LFS 走 HTTPS、证书与 SSH 无关
- [ ] 没有长期开着 `http.sslVerify false`

上一章：[[05-合并发布与版本标记]]　下一章：[[07-故障恢复]]
