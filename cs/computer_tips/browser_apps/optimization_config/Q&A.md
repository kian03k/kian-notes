我帮你整理成**规范、清爽、适合知识库**的 Markdown 格式：
- 所有路径/命令统一放进代码块 `` ` `` 或 ``` ```
- 中文作为清晰副标题
- 层级统一、可读性强

直接复制下面这段即可使用：

---

## How to Extract Google Theme Wallpaper
如何提取 Google 主题壁纸

---

### Computer: Save Chrome Theme Wallpaper
电脑端：Chrome 浏览器主题壁纸保存（最常用）

#### Method 1: Direct Access to Original Wallpaper
方法 1：直接访问壁纸原图（最简单）

1. Open Chrome and go to theme settings
   打开 Chrome，进入已安装主题页面
   - Address:
     ```
     chrome://settings/appearance
     ```
   - Extensions page:
     ```
     chrome://extensions/
     ```

2. Open high-definition wallpaper directly in address bar
   在地址栏输入以下链接，直接打开高清壁纸：
   ```
   chrome://theme/IDR_THEME_NTP_BACKGROUND@2x
   ```
   - `@2x` means high-definition image
     `@2x` 代表高清 2 倍图（更清晰）

3. Right-click the image → Save image as…
   右键图片 → 图片另存为 → 保存到本地

---

#### Method 2: Extract from Installed Theme Folder
方法 2：从已安装主题提取（通用）

1. Open Chrome version info
   打开 Chrome，地址栏输入：
   ```
   chrome://version/
   ```

2. Find and copy your **Profile Path**
   找到个人资料路径并复制：
   - Windows default path:
     ```
     C:\Users\用户名\AppData\Local\Google\Chrome\User Data\Default
     ```
   - Mac default path:
     ```
     ~/Library/Application Support/Google/Chrome/Default
     ```

3. Open the folder and go to `Themes` or `Extensions`
   打开该文件夹 → 进入 `Themes` 或 `Extensions` 文件夹

4. Actual example path:
   实际地址示例：
	```
	C:\Users\用户名\AppData\Local\Google\Chrome\User Data\Default\Extensions\comagpdccoohcedfdcpgglndcjkhkpgo\3.0_0\images
	```

---
