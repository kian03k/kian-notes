---
tags: [git, 速查]
created: 2026-11-16
updated: 2026-11-16
status: ok
---

# rebase 与 merge

`rebase` 和 `merge` 都能把两条分支的改动合到一起，区别只在于**历史被写成什么形状**。选错的代价不对称：merge 选错只是历史难看，rebase 选错会让协作者的本地历史和远端彻底分叉。

## 一、两者在做什么

```text
起点：main 走到 C，你在 B 上拉出 feature 并提交了 D、E

  A — B — C            ← main
        ╲
         D — E          ← feature

merge（在 feature 上 merge main）：
  A — B — C —— M        ← M 是合并提交，有两个父节点（C 和 E）
        ╲    ╱
         D — E

rebase（在 feature 上 rebase main）：
  A — B — C — D' — E'   ← D、E 的内容不变，但被重放，SHA 全变了
```

一句话：**merge 保留分叉并记录「何时合的」；rebase 抹掉分叉假装「一直基于最新代码写的」。**

## 二、历史形态对比

| | merge | rebase |
| --- | --- | --- |
| 历史形状 | 有分叉、有合并提交 | 一条直线 |
| 提交 SHA | 全部保持不变 | 被重放的提交全部变新 SHA |
| 是否为「真实历史」 | 是 | 否，是整理后的叙述 |
| 冲突解决次数 | 一次（在合并提交时集中解决） | 可能每个被重放的提交都要解决一次 |
| 对协作者的影响 | 无 | 已推送的分支 rebase 后必须强推，他人本地会分叉 |
| 适用分支 | 共享分支 | 私有分支 |

## 三、决策规则：只看分支是否共享

```
这条分支上还有别人在提交或拉取吗？
├─ 没有 → rebase
└─ 有   → merge，且禁止 force push
```

判定「共享」的实操标准：**这条分支被推送到远端、并且除你之外有人 checkout 过或从它拉过代码**。只要满足，就当共享处理。

典型归属：

| 分支 | 性质 | 同步方式 |
| --- | --- | --- |
| `main` / `master` | 共享 | merge（通常只经 PR） |
| 团队 `wip` / `dev` / `staging` | 共享 | merge |
| 自己独用的 `wip` | 私有 | rebase 可以 |
| `feature/*` `fix/*` | 私有 | rebase |

### 为什么共享分支绝对不能 rebase

Git 用 SHA 识别「同一个提交」。rebase 产出的是内容相同、SHA 全新的提交，在 Git 看来完全是另一批东西：

```text
远端（你强推后）：A' — B' — C'
同事本地：        A  — B  — C    ← 他基于这个继续工作
```

同事下次 `pull` 时，Git 会试图把两套互不相关的历史拼起来，结果是大量重复提交、成片冲突，严重时报 `fatal: refusing to merge unrelated histories`。他手里的工作没丢，但需要手工收拾——这就是「rebase 共享分支」的真实成本。

同一个分支上只有你一个人时（哪怕它叫 `wip`、哪怕它在远端），rebase + `--force-with-lease` 完全安全。

### 一条容易搞错的边界：`git pull --rebase`

`git pull --rebase` 只重写**你自己尚未推送的提交**，别人手上没有这些旧 SHA，所以本身不破坏协作。它变危险只有一种情况：**被重写的提交已经推送过**，那么 pull 之后你只能强推，强推就会影响别人。

所以准确表述是：共享分支可以 `pull --rebase`（前提是本地没有已推送的提交），但**不要 rebase 已推送的提交、不要 force push**。

## 四、两条实操路径

### 私有分支同步主干

```bash
git switch feature/x
git fetch origin
git rebase origin/main        # 比 git pull --rebase origin main 更清晰：明确「基于谁重放」

# 有冲突时
git add <file> && git rebase --continue
git rebase --abort            # 放弃，回到 rebase 之前

# 已推送过则需强推
git push --force-with-lease
```

### 共享分支同步主干

```bash
git switch wip
git pull --no-rebase origin wip   # 先和同分支的人对齐
git fetch origin
git merge origin/main
git push
```

### 合并进主干之后

分支进主干后，开发线要跟上，否则会基于旧基线继续写、越拖冲突越大：

```bash
git switch main && git pull --ff-only
git switch wip
git rebase main       # wip 私有
# git merge main      # wip 共享
```

这一步的时机是「每次主干有新提交」，但它**不是必须 rebase 的仪式**，而是「让分支基线不过时」的手段——共享分支用 merge 达成同样目的。

## 五、强推：只认 `--force-with-lease`

```bash
git push --force-with-lease              # 远端没有你未见过的新提交时才覆盖
git push --force                         # 无条件覆盖，禁用
```

`--force-with-lease` 的语义是「如果远端当前指向的提交和我记录的一致，才允许覆盖」。它能挡住「我刚 rebase 完，同事正好推了一个提交，我一强推把它抹了」这种事故。`--force` 挡不住。

## 六、常见误解

| 说法 | 实际情况 |
| --- | --- |
| 「rebase 更高级，应该都用 rebase」 | rebase 只适合私有分支；共享分支用 rebase 等于给全队制造事故 |
| 「merge 会污染历史，所以要避免」 | 合并提交是真实发生过的事件。共享分支的合并提交不是噪音，是审计线索 |
| 「每次合并到主干后都要 rebase 一次」 | 前提是分支私有。共享分支应 merge |
| 「rebase 会丢代码」 | 不会丢内容，reflog 也能回退；危险的是它改了 SHA，影响别人 |
| 「强推才能 rebase」 | 只有提交已推送过才需要强推；本地未推的 rebase 直接 push 即可 |

## 七、关联

- 决策树在真实流程中的位置：[[04-同步主干与冲突解决]]
- 分支错乱后的重置：[[分支错乱恢复]]
- 冲突标记怎么读、怎么解：见 04 章 4.5

> 修正：原稿中存在两处互相冲突的表述——一处称「`wip` 是团队共享分支，绝不可 rebase」，另一处称「每次合并后都要 `rebase wip` 并强推」。两者各自成立，但适用前提不同：前者对应共享分支，后者对应单人私有分支。本笔记以「分支是否共享」作为唯一判据统一，不再按分支名（`wip`）判断。
