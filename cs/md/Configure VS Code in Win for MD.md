# VS Code Markdown 图片自动归类配置方案（Windows端）

## 文档说明
本文档记录了在 **Windows 11** 环境下，配置 VS Code 实现 Markdown 图片自动保存到“与文件同名文件夹”的成功方案。**经实际验证，方案一已完全实现预期效果**。

---

## 环境说明
- **操作系统**：Windows 11
- **VS Code版本**：最新版
- **已安装插件**：
  - Paste Image (by mushan)
  - Markdown All in One

---

## 方案一：使用 Paste Image 插件（推荐，已成功验证）

这是目前最成熟的方案，通过精细配置可以实现：**粘贴图片时自动创建与 Markdown 文件同名的文件夹，并按时间戳命名图片**。

### 第一步：安装插件
1. 打开 VS Code
2. 点击左侧活动栏的扩展图标（或按 `Ctrl+Shift+X`）
3. 搜索 **Paste Image**
4. 找到由 `mushan` 开发的版本并安装

### 第二步：配置插件
打开 VS Code 设置（`Ctrl + ,`），点击右上角的 **打开设置(JSON)** 图标，将以下配置写入全局 `settings.json`：

```json
{
    // 1. 核心配置：图片保存路径为Markdown文件同名的文件夹
    // ${currentFileDir}：当前文件所在目录
    // ${currentFileNameWithoutExt}：当前文件名（不含扩展名）
    "pasteImage.path": "${currentFileDir}/${currentFileNameWithoutExt}/",
    
    // 2. 文件名格式：使用时间戳，避免重名且便于整理
    // 格式：年-月-日-时分秒毫秒 → 例如：2026-03-15-143025123.png
    "pasteImage.defaultName": "YYYY-MM-DD-HHmmssSSS",
    
    // 3. 可选：添加固定前缀（如图片统一加 "img-" 前缀）
    // "pasteImage.namePrefix": "img-",
    
    // 4. 可选：保存前弹出确认框，方便手动修改文件名
    // "pasteImage.showFilePathConfirmInputBox": true,
    
    // 5. 插入到Markdown中的格式，保持默认即可
    // 如需自定义可使用： "![${imageFileNameWithoutExt}](${imageFilePath})"
}
```

**配置项详解：**
- **`pasteImage.path`**：`${currentFileDir}/${currentFileNameWithoutExt}/`
  - 效果：编辑 `/docs/我的笔记.md` 时，图片自动保存到 `/docs/我的笔记/` 文件夹
  - 末尾的 `/` 表示这是一个文件夹，插件会自动创建
  
- **`pasteImage.defaultName`**：`YYYY-MM-DD-HHmmssSSS`
  - 支持的变量：
    - `YYYY`：四位年份
    - `MM`：两位月份
    - `DD`：两位日期
    - `HH`：24小时制小时
    - `mm`：分钟
    - `ss`：秒
    - `SSS`：毫秒

### 第三步：使用
1. 在 Windows 中截图或复制任意图片到剪贴板
2. 在 VS Code 中打开你的 Markdown 文件
3. 按下快捷键 **`Ctrl+Alt+V`**
4. 插件会自动完成：
   - 检查并创建与 Markdown 文件同名的文件夹（如不存在）
   - 将图片以时间戳格式保存到该文件夹
   - 在光标位置自动插入 Markdown 图片语法：`![](文件夹名/时间戳.png)`

---

## 方案二：VS Code 内置功能（1.79+ 版本，未尝试）

如果你不想安装额外插件，且 VS Code 版本在 1.79 以上，可以尝试使用内置的“复制外部文件”功能。

### 配置步骤
1. 打开 VS Code 设置（`Ctrl + ,`）
2. 在搜索框输入 `markdown copy`
3. 找到 **`Markdown > Copy Files: Destination`** 配置项
4. 点击“添加项”，配置如下：
   - **项**：`**/*.*`（匹配所有被拖入或粘贴的文件）
   - **值**：`${documentDirName}/${documentBaseName}/`

**参数说明：**
- `${documentDirName}`：当前文件所在目录名
- `${documentBaseName}`：当前文件名（不含扩展名）

### 使用方式
此功能更适合拖拽操作：
- 将图片文件从资源管理器拖入 Markdown 文档
- 或从网页直接拖拽图片到文档
- VS Code 会自动将图片复制到配置的路径并插入引用

---

## 方案对比与选择建议

| 特性 | 方案一：Paste Image 插件 | 方案二：VS Code 内置功能 |
|------|--------------------------|-------------------------|
| **自动创建同名文件夹** | ✅ 完全支持 | ✅ 支持 |
| **时间戳命名** | ✅ 支持，格式丰富可自定义 | ❌ 较弱，依赖系统命名 |
| **操作便捷性** | ✅ 快捷键 `Ctrl+Alt+V` 粘贴 | ⚡ 更适合拖拽操作 |
| **稳定性** | ✅ 成熟稳定，社区广泛使用 | 🆕 新功能，仍在完善 |
| **自定义程度** | ✅ 高，多种变量组合 | ⚡ 一般，选项有限 |
| **配置复杂度** | ⚡ 一次配置，永久使用 | ✅ 简单直观 |

---

## 最终推荐配置（可直接复制使用）

如果你想要一个开箱即用的配置，将以下内容完整复制到你的 `settings.json` 即可：

```json
{
    // Paste Image 完整推荐配置
    "pasteImage.path": "${currentFileDir}/${currentFileNameWithoutExt}/",
    "pasteImage.defaultName": "YYYY-MM-DD-HHmmssSSS",
    "pasteImage.forceUnixStyleSeparator": true,
    
    // Markdown 编辑体验优化（可选）
    "[markdown]": {
        "editor.quickSuggestions": true,     // 启用快速建议
        "editor.wordWrap": "on",              // 自动换行
        "editor.fontSize": 14                  // 字体大小
    }
}
```

---

## 使用效果演示

假设你有一个文件：`D:\notes\项目文档.md`

**操作前：**
```
D:\notes\
  └─ 项目文档.md
```

**操作：**
1. 在 `项目文档.md` 中按 `Ctrl+Alt+V`
2. 粘贴一张截图

**操作后：**
```
D:\notes\
  ├─ 项目文档.md
  └─ 项目文档\          # 自动创建的文件夹
      └─ 2026-03-15-143025123.png  # 自动命名的图片
```

**文档中自动插入：**
```markdown
![](项目文档/2026-03-15-143025123.png)
```

---

## 常见问题

### Q1：快捷键无效怎么办？
检查是否与其他软件冲突，可在 VS Code 中自定义快捷键：
1. 按 `Ctrl+K` `Ctrl+S` 打开快捷键设置
2. 搜索 `paste image`
3. 右键重新设置快捷键
> 已发现QQ音乐与ctrl+alt+v冲突

### Q2：想修改图片保存路径格式？
`pasteImage.path` 支持多种变量组合：
- `${currentFileDir}` - 当前文件目录
- `${currentFileNameWithoutExt}` - 当前文件名（无后缀）
- `${projectRoot}` - 项目根目录
- `${workspaceFolder}` - 工作区文件夹

例如：`${workspaceFolder}/assets/${currentFileNameWithoutExt}`

### Q3：图片命名想要更简洁？
修改 `defaultName` 格式：
- `YYYYMMDD-HHmmss` → `20260315-143025`
- `YYYY-MM-DD` → `2026-03-15`（同一天图片会覆盖，不推荐）

---

## 总结

**方案一使用 Paste Image 插件**完全实现了需求：
- ✅ 自动创建与 Markdown 文件同名的文件夹
- ✅ 按时间戳自动命名图片，避免重名
- ✅ 一键粘贴，无需手动整理
- ✅ 配置灵活，可满足个性化需求

一次配置，永久生效，强烈推荐使用。