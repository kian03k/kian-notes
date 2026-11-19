---
tags: [python, 爬虫, selenium, 反检测]
created: 2026-11-19
updated: 2026-11-19
status: ok
---

# Selenium 反检测：让自动化脚本不被识别为机器人

> **适用场景**：用 Selenium 驱动浏览器时，目标站点把默认实例识别成自动化工具——弹验证码、直接拦页面、或要求人机校验。需要在**已获授权、可人工兜底**的前提下，让浏览器表现为正常用户。
> **留档说明**：本篇记录的是这个问题**为什么会发生、当时怎么解**的思路与方案，用于理解问题缘由。当前已有更成熟的落地实现，尚未并入本库，待补充后与之合并。
> **红线先说**：这套配置只适用于自己可控或已获授权的站点。绕过检测本身不等于获得操作授权，涉及他人账号、考试、抢购、风控场景一律不适用。

## 1. 为什么 Selenium 会被检测为机器人

| 检测方式 | 说明 | 能否绕过 |
|---|---|---|
| `navigator.webdriver` 属性 | JS 检查 `window.navigator.webdriver === true` | 能 |
| `chrome.runtime` 对象 | Selenium 会暴露 `chrome.runtime` 等 API | 能隐藏 |
| 鼠标轨迹异常 | 自动点击是直线 + 瞬间完成，真人带加速度与抖动 | 能模拟 |
| 请求头特征 | 默认 UA、语言、屏幕分辨率不真实 | 能伪造 |
| WebGL / Canvas 指纹 | 浏览器渲染指纹与真实用户不同 | 能伪造 |
| DevTools 端口 / 进程特征 | Chrome 启动参数暴露自动化痕迹 | 能隐藏 |

判定逻辑基本都是「多个弱信号加权」：单看某一项未必拦你，**JS 指纹干净但点击全是瞬移**照样会被行为模型拦下，所以下面四层配置要一起上。

## 2. 完整防检测驱动（复制即用）

思路分三层：**启动参数隐藏自动化开关 → 注入 JS 伪装浏览器指纹 → 运行时模拟真人行为**（第三层见第 4 节）。

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def create_stealth_driver(headless: bool = False):
    """创建防检测版 Chrome 驱动"""
    options = Options()

    # 1. 隐藏自动化标志（最关键）
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    # 2. 模拟真实浏览器环境
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    options.add_argument("--lang=zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    # 3. 隐身模式（不保存历史、不加载插件）
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 4. 无头模式（生产环境按需开启）
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # ---- 注入 JS：伪装浏览器指纹 ----
    # webdriver 标志置为 undefined（绕过检测的关键一步，必须加）
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # 伪造 plugins / languages / maxTouchPoints
    driver.execute_script(
        "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script(
        "Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']})")
    driver.execute_script(
        "Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1})")
    # permissions.query 正常化
    driver.execute_script("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters)
        );
    """)
    # WebGL 指纹伪造（可选，增强隐蔽性）
    driver.execute_script("""
        const getParameter = WebGLRenderingContext.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Open Source Technology Center';
            if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 630 (Kaby Lake GT2)';
            return getParameter(parameter);
        };
    """)
    # 屏幕分辨率与平台
    driver.execute_script("""
        Object.defineProperty(screen, 'width', {value: 1920});
        Object.defineProperty(screen, 'height', {value: 1080});
        Object.defineProperty(screen, 'availWidth', {value: 1920});
        Object.defineProperty(screen, 'availHeight', {value: 1080});
        Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
    """)

    driver.implicitly_wait(10)
    driver.set_page_load_timeout(20)
    return driver
```

### 2.1 几处容易踩的坑（已在上面代码里规避）

- **别重写 `window.Intl` 和 `window.Date`**：会破坏页面正常的日期 / 国际化功能，得不偿失。
- **同一页面重复声明 `const originalQuery`** 会抛 `SyntaxError`（全局 `const` 不可重复声明），一段 permissions 注入只写一次。
- **启动参数已设 `--user-agent` 就别再 JS 重定义 `navigator.userAgent`**，两者会打架，且后者容易被检测出 `getter` 被改。
- **`service=` 必须传 `Service` 对象**，不能直接传 `ChromeDriverManager().install()` 返回的字符串路径。

## 3. 验证是否隐身成功

打开检测站逐项核对：

| 网站 | 功能 |
|---|---|
| `https://bot.sannysoft.com` | 最权威的 Selenium 检测页，逐项显示被检测特征 |
| `https://arh.antoinevastel.com/bots/areyouheadless` | 检测是否为 headless |
| `https://whoisxmlapi.com/browser-fingerprint-demo` | 检测指纹是否自洽 |

目标是 sannysoft 页面全部转绿。各项期望值：

| 检测项 | 期望值 |
|---|---|
| `navigator.webdriver` | `undefined`（不是 `true`） |
| `chrome.runtime` | 不存在或无异常 |
| `permissions.query` | 正常返回 |
| `languages` | `['zh-CN', 'zh', 'en']` |
| `screen.width` | `1920` |
| `userAgent` | 匹配所设的 Chrome 120 |
| `plugins` | 非空 |
| `maxTouchPoints` | `1` |
| headless 判定 | `false`（即使开了 headless） |

## 4. 模拟真人鼠标操作（防行为检测）

JS 指纹干净之后，「点击太快、直线移动」仍会被行为分析识别。用 `ActionChains` 加随机偏移与停顿：

```python
from selenium.webdriver.common.action_chains import ActionChains
import random
import time


def human_click(driver, element, delay_range=(0.3, 0.8)):
    """模拟真人点击：移动鼠标 + 停留 + 点击"""
    actions = ActionChains(driver)

    # 1. 移动到元素附近（随机偏移，避免每次都点正中心）
    x_offset = random.randint(-5, 5)
    y_offset = random.randint(-5, 5)
    actions.move_to_element_with_offset(element, x_offset, y_offset)

    # 2. 停留 0.3~0.8 秒，模拟"思考"
    time.sleep(random.uniform(*delay_range))

    # 3. 点击
    actions.click().perform()

    # 4. 等待响应
    time.sleep(random.uniform(0.5, 1.2))
```

使用：

```python
option_label = driver.find_element(By.CSS_SELECTOR, ".option-list-item label")
human_click(driver, option_label)
```

效果：鼠标不是「瞬间命中」，而是「移动、停顿、轻点」，行为模型更可能判定为真人。

## 5. 主程序模板：先自检，敏感步骤交人工

```python
import time
from selenium.webdriver.common.by import By

driver = create_stealth_driver(headless=False)   # 调试阶段一律 headless=False

driver.get("https://bot.sannysoft.com")           # 先验证是否隐身
time.sleep(5)

driver.get("https://target.example.com")          # 进入目标系统

input("登录步骤请手动完成，就绪后按回车继续...")    # 登录、验证码交人工

# 之后的自动化操作全部走「真人点击」
option = driver.find_element(By.CSS_SELECTOR, ".option-list-item label")
human_click(driver, option)
```

把登录、验证码、二次确认这类高风险动作留给人工，脚本只承担重复劳动——既是合规上的稳妥做法，也能大幅降低风控触发率。

## 6. 一键检测脚本

存为 `check_stealth.py`，快速验证配置是否生效：

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://bot.sannysoft.com")
print("打开检测页面，人工查看各项是否全部通过")
input("按回车关闭浏览器...")
driver.quit()
```

## 7. 使用策略

| 场景 | 推荐做法 |
|---|---|
| 受控 / 已授权环境 | `headless=False`，人工登录 + 人工确认，脚本只做辅助 |
| 需长期运行 | 定期更换 User-Agent 与窗口尺寸，避免固定指纹 |
| 降低风控 | 操作之间随机等待 3~10 秒，避免高频连续动作 |
| 出问题排查 | 保存截图与操作日志，便于回看被拦在哪一步 |
| 有 API 可用 | 优先调接口，根本不需要浏览器——反检测配置是最后手段 |

## 8. 陷阱清单

| 陷阱 | 后果 | 正解 |
|---|---|---|
| 只改 JS 不改启动参数 | `navigator.webdriver` 干净了，但 `--enable-automation` 仍在，仍被识别 | 两层一起上 |
| UA 设成 Chrome 120 但 `navigator.userAgentData` 是旧版本 | 指纹自相矛盾，反而更容易被标记 | UA 与版本号保持同一主版本 |
| `--incognito` 与已有的用户数据目录同用 | Chrome 直接启动失败 | 二者选一 |
| headless 下伪造 `screen` 尺寸 | 真实 headless 屏幕就是 800x600，改成 1920x1080 与视口矛盾 | headless 时同步设 `--window-size` |
| `time.sleep` 写成固定值 | 行为节奏过于规律，仍是机器特征 | 用 `random.uniform` 区间 |
| 检测站全绿就以为万事大吉 | 商业风控用的是另一套模型（IP、账号历史、行为序列） | 把反检测当辅助，不当护身符 |
| 用这套配置打他人系统 / 高频抓取 | 封号、封 IP，甚至触及法律与平台条款 | 只在自己可控或已授权范围内用 |

## 9. 速查

> 四层配合：`--disable-blink-features=AutomationControlled`（启动参数）+ `navigator.webdriver → undefined`（JS 注入）+ 随机化点击（`ActionChains` + 随机 sleep）+ 真实 UA / 语言 / 分辨率（环境伪装）。验证去 `bot.sannysoft.com`，全绿只说明「基础检测过关」，商业风控另算。登录等敏感步骤永远留人工。

---

回到：[[cs/dev/python/index|Python 导航]]

> 相关：抓静态页更省事，`requests` + `BeautifulSoup` 就够，桌面浏览器只在必须执行 JS 时才用——见 [[02-网页抓取]]；打包成 exe 分发时 chromedriver 的路径问题见 [[pyinstaller|PyInstaller 打包 Flask 桌面工具]]。
