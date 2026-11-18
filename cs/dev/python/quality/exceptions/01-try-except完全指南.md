---
tags: [python, 异常处理]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# try-except 完全指南（含 raise 与堆栈记录）

Python 异常处理的核心是 `try...except`：捕获运行时错误，避免程序崩溃。配套的 `raise` 用于主动抛出异常，二者构成 Python 中"优雅的错误传播与控制流机制"。

## 一、try...except 七种基础形式

### 1. 最基本形式（裸 except 不推荐）

```python
try:
    result = 10 / 0
except:
    print("发生了错误！")
```

> ⚠️ 不推荐裸 `except:`：它会捕获所有异常（包括 `KeyboardInterrupt`、`SystemExit`），导致 Ctrl+C 无法中断程序。

### 2. 捕获特定异常

```python
try:
    x = int(input("请输入一个数字: "))
    result = 10 / x
except ValueError:
    print("输入的不是有效数字！")
except ZeroDivisionError:
    print("不能除以零！")
```

多个 `except` 块按顺序匹配，**只执行第一个命中的块**。

### 3. 元组捕获多个异常类型

```python
except (ValueError, ZeroDivisionError) as e:
    print(f"输入错误或除零错误: {e}")
```

### 4. as 获取异常对象

```python
try:
    with open("nonexistent.txt", "r") as f:
        content = f.read()
except FileNotFoundError as e:
    print(f"文件未找到: {e.filename}")
except PermissionError as e:
    print(f"权限不足: {e}")
```

异常实例的常用属性：`.args`（异常参数元组）、`.errno`（系统错误码）、`.filename`（文件相关异常）、`.strerror`（错误描述）。

### 5. else：无异常时执行

```python
try:
    x = int(input("请输入一个数字: "))
    result = 10 / x
except ValueError:
    print("输入无效")
except ZeroDivisionError:
    print("不能除以零")
else:
    print(f"计算成功: 10 / {x} = {result}")
```

`else` 块仅在 `try` 中**没有发生异常**时执行。用途：分离"正常逻辑"和"异常处理逻辑"。

> 最佳实践：只把**可能抛异常的代码**放进 `try`，其余正常逻辑放 `else`。

### 6. finally：无论如何都执行

`finally` 的核心用途是**资源清理**（关闭文件、数据库连接、释放锁、网络连接等）。

⚠️ 常见错误：`open()` 失败时 `f` 未定义，不能在 `finally` 中直接 `f.close()`。

```python
# ✅ 正确写法：先判空
f = None
try:
    f = open("data.txt", "r")
    content = f.read()
except FileNotFoundError:
    print("文件不存在")
finally:
    if f is not None:
        f.close()

# ✅ 更推荐：用 with 上下文管理器，自动关闭，无需 finally
try:
    with open("data.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("文件不存在")
```

### 7. 嵌套 try-except

```python
try:
    x = int(input("请输入数字: "))
    try:
        result = 10 / x
    except ZeroDivisionError:
        print("内部除零错误")
        raise  # 重新抛出异常
except ValueError:
    print("输入格式错误")
```

嵌套结构可用于**局部处理 + 重新抛出**。`raise` 不带参数：重新抛出**当前异常**（保留原始 traceback）。

## 二、raise：主动抛出异常

### 1. 抛出内置异常

```python
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("除数不能为零")
    return a / b

try:
    divide(10, 0)
except ZeroDivisionError as e:
    print(e)  # 输出: 除数不能为零
```

### 2. 抛出自定义异常

```python
class AgeError(Exception):
    """自定义异常：年龄不合理"""
    def __init__(self, age):
        self.age = age
        super().__init__(f"年龄 {age} 不合法（应在 0-150 之间）")

def set_age(age):
    if not isinstance(age, int) or age < 0 or age > 150:
        raise AgeError(age)
    print(f"年龄设置为: {age}")

try:
    set_age(200)
except AgeError as e:
    print(f"自定义异常: {e}")
    print(f"出错年龄: {e.age}")
```

自定义异常的好处：语义清晰、可携带额外上下文（如 `age`）、与业务逻辑绑定，便于调用方区分错误类型。

### 3. raise from：异常链（Exception Chaining）

```python
def read_config(filename):
    try:
        with open(filename) as f:
            return f.read()
    except FileNotFoundError as e:
        raise RuntimeError("配置文件缺失，请检查环境") from e

try:
    read_config("config.ini")
except RuntimeError as e:
    print(e)
    print(f"原始异常: {e.__cause__}")  # 显示原始异常
```

- `raise ... from e`：将原始异常 `e` 作为**原因（cause）**附加到新异常上；
- `e.__cause__` 指向原始异常；
- `raise ... from None`：屏蔽原始异常链，仅显示新异常。

```python
raise RuntimeError("配置错误") from None  # 只显示 RuntimeError，不显示 FileNotFoundError
```

异常链在调试大型系统时非常有用，能清晰追踪错误源头。

## 三、except 中记录完整堆栈

在 `except` 块中记录日志时，用 `logger.exception()`（推荐）或 `logger.error(..., exc_info=True)`，都能把当前异常的**完整 traceback** 写进日志：

```python
import logging
import os
import shutil
import zipfile

logger = logging.getLogger(__name__)

try:
    with zipfile.ZipFile(zipFilePath) as azip:
        if os.path.exists(unpackFolderPath):
            shutil.rmtree(unpackFolderPath)
        azip.extractall(path=unpackFolderPath)
        rename_filename_in_dir(unpackFolderPath)
except Exception as e:
    # 写法一（推荐）：logger.exception() —— 只能在 except 块内调用，
    # 自动以 ERROR 级别附带当前异常的完整堆栈
    logger.exception("解压并处理目录时发生异常，zipFilePath=%s, unpackFolderPath=%s",
                     zipFilePath, unpackFolderPath)

    # 写法二：logger.error(..., exc_info=True) —— 效果相同，适合统一用 error() 的场景
    # logger.error("解压并处理目录时发生异常: %s", e, exc_info=True)

    # 如果需要继续抛给上层处理，可以再 raise
    # raise
```

要点：

- `logger.exception(...)` **必须在 `except` 语句块里调用**，自动记录完整 traceback；
- `logger.error(..., exc_info=True)` 与之等价；
- 两种写法都不会中断程序；要让异常继续向上传播，在记录日志后再 `raise`。

> 日志侧的对应场景与配置见 [[cs/dev/python/quality/logging/04-特殊场景手册|logging 04-特殊场景手册]] 场景 1。

## 四、Python 的哲学：EAFP vs LBYL

Python 奉行 **EAFP**（Easier to Ask for Forgiveness than Permission）："与其先检查，不如直接尝试，出错了再处理。"

```python
# EAFP（推荐）
try:
    value = my_dict[key]
except KeyError:
    value = default_value

# LBYL（Look Before You Leap，不推荐）
if key in my_dict:
    value = my_dict[key]
else:
    value = default_value
```

EAFP 更好的原因：

1. **避免竞态条件**：`if os.path.exists(filename): f = open(filename)` 中，文件可能在 `if` 和 `open` 之间被删除；
2. **更高效**：正常路径无检查开销，只在异常发生时才做额外处理；
3. **更简洁**：代码更少，逻辑更集中；
4. **更符合 Python 风格**：`getattr`、`dict.get` 等内置能力都体现 EAFP。

> 建议：预期异常很少发生时优先 `try...except`；高频循环内的检查可用 `len()`、`dict.get()` 等避免依赖异常做常规分支。

## 五、与"条件判断防错"方式的对比

条件判断方式：先检查再操作，出错返回 `None`/`False` 等哨兵值。

| 特性 | try...except 方式 | 条件判断方式 |
|---|---|---|
| 性能 | ✅ 异常少时更快（正常路径无判断开销） | ❌ 每次都要判断 |
| 可读性 | ✅ 正常流程在 try，异常在 except | ❌ 业务逻辑与错误检查混杂 |
| 可扩展性 | ✅ 易于新增异常类型 | ❌ 每种错误都要加新判断 |
| 错误传播 | ✅ 异常可向上抛，适合模块化设计 | ❌ 返回值需逐层判断，易遗漏 |
| 调试友好性 | ✅ 完整 traceback，易于定位 | ❌ 返回 None 时不知道哪里出错 |
| 语义 | ✅ 符合 EAFP 哲学 | ❌ LBYL 易有竞态条件 |

## 六、最佳实践与生产级模板

| 原则 | 说明 |
|---|---|
| 不要用裸 except | 指定具体异常类型，或至少 `except Exception:` |
| 用 `as e` 捕获异常对象 | 便于调试、记录日志 |
| 用 `else` 分离正常逻辑 | 避免把正常代码误包进 try |
| 用 `finally` 清理资源 | 文件、锁、连接等必须释放（或直接用 with） |
| 自定义异常继承 `Exception` | 不要继承 `BaseException`（那是系统异常） |
| 异常链 `raise ... from` | 保留原始错误上下文 |
| 不要吞掉异常 | 避免空 `except: pass`，除非明确知道后果 |
| 记录日志 | 用 `logging.exception()` 自动记录 traceback |

生产级异常处理模板：

```python
import logging

def process_user_input(user_id):
    try:
        user = fetch_user_from_db(user_id)  # 可能抛出 DBError
        if not user.is_active:
            raise UserInactiveError(f"用户 {user_id} 已停用")

        result = calculate_score(user.data)  # 可能抛出 ValueError
        return result

    except UserInactiveError as e:
        logging.warning(f"用户状态异常: {e}")
        return None
    except (ValueError, TypeError) as e:
        logging.error(f"数据格式错误: {e}", exc_info=True)  # 记录完整 traceback
        raise  # 重新抛出，让上层处理（如 API 返回 500）
    except Exception as e:
        logging.critical(f"未预期错误: {e}", exc_info=True)
        raise RuntimeError("系统内部错误") from e
    else:
        logging.info(f"成功处理用户 {user_id}")
    finally:
        close_db_connection()  # 清理资源
```

## 七、常见陷阱

| 陷阱 | 正确做法 |
|---|---|
| `except:` 捕获所有异常（包括 Ctrl+C） | 改为 `except Exception:` |
| `finally` 中 return 会覆盖 try/except 的 return | 避免在 finally 中 return |
| 用异常做流程控制（如循环） | 用 `for/while` + 条件判断 |
| 忘记关闭文件/连接 | 用 `with` 上下文管理器 |
| 捕获异常后什么都不做 | 至少记录日志或打印 |
| 自定义异常未继承 `Exception` | `class MyError(Exception):` |

## 八、raise 与 return 的区别

```python
# ❌ 不推荐：捕获后转成返回值，掩盖了原始错误
def func():
    try:
        if error_condition:
            raise ValueError("出错了")
        return "成功"
    except ValueError:
        return "处理失败"   # 丢失原始异常信息，不利于调试
```

```python
# ✅ 正确做法：记录日志后重新抛出
def func():
    try:
        if error_condition:
            raise ValueError("出错了")
        return "成功"
    except ValueError as e:
        logging.error(f"业务逻辑错误: {e}")
        raise  # 重新抛出，保留 traceback
```

`raise` 不带参数 = **重新抛出当前异常**，保留原始调用栈。

## 九、总结与口诀

| 维度 | try...except + raise 的优势 |
|---|---|
| 健壮性 | 不因未预料错误崩溃，程序可恢复 |
| 可维护性 | 异常类型明确，便于模块化和单元测试 |
| 调试友好 | 完整 traceback + 异常链，快速定位 |
| 性能 | 正常路径无检查开销（EAFP） |
| 扩展性 | 可自定义异常，构建领域错误模型 |
| 资源安全 | `finally` 保证资源释放，避免泄漏 |

> `try...except` 和 `raise` 不是"兜底机制"，而是 Python 中优雅的错误传播与控制流机制——让程序面对不确定性时，依然安全、清晰、可追踪地运行。

记忆口诀：

> 先试后查，异常为王；捕获要准，资源要清；自定义异常，语义分明；raise 保留链，日志别忘记。

---

## 附：数据库事务模板（失败回滚 + 释放资源）

数据库操作的失败处理是 `try/except/finally` 最典型的用法：异常**必须回滚**，连接**必须释放**。

```python
try:
    conn, cursor = get_conn()
    cursor.execute("delete from student where id=%s", (i,))
    conn.commit()
except Exception as e:
    print("操作失败:", e)
    conn.rollback()          # ← 数据库操作失败务必回滚
finally:
    close(conn, cursor)      # ← 无论成败都释放资源
```

三步曲：`try` 执行 → 失败 `rollback()` → `finally` 关连接。

> ⚠️ 只 `commit` 不 `rollback` 的后果：连接池里的连接带着未完成事务被复用，后续操作会看到"不该存在"的中间状态，甚至长时间持锁。

---

回到：[[cs/dev/python/index|Python 导航]]
