### 关于 `.gitignore` 的常见误区

**`.gitignore` 只对未跟踪的文件生效**。如果文件已经推送到云端（即已经被 Git 跟踪），仅仅添加到 `.gitignore` 是**无效**的，它不会被忽略，也不会自动删除云端文件。

#### 正确做法（如果想把已跟踪文件加入 `.gitignore`）：

1. **先删除云端文件（但保留本地文件）**：
   ```bash
   git rm --cached file.txt   # 从 Git 中移除，但保留本地文件
   ```

2. **然后添加到 `.gitignore`**：
   ```bash
   echo "file.txt" >> .gitignore
   ```

3. **提交并推送**：
   ```bash
   git add .gitignore
   git commit -m "停止跟踪 file.txt 并加入 .gitignore"
   git push
   ```

### 总结

| 操作                                      | 本地文件 | 云端文件 |
| --------------------------------------- | ---- | ---- |
| 本地直接删除                                  | ❌ 删除 | ✅ 还在 |
| 本地删除 + `git add -u` + commit + push     | ❌ 删除 | ❌ 删除 |
| 只加 `.gitignore`（已跟踪文件）                  | ✅ 还在 | ✅ 还在 |
| `git rm --cached` + `.gitignore` + push | ✅ 还在 | ❌ 删除 |

**一句话**：要删除云端文件必须执行 `git rm` 并 push；`.gitignore` 只防新文件，不删旧文件。