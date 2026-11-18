---
tags: [python, 装饰器]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# 装饰器基础与 functools.wraps

## 1. 装饰器是什么

装饰器本质是一个**函数**：它接受一个函数作为参数，返回一个新函数，作用是**增强或修改原函数的行为**，而无需修改原函数的代码。

## 2. 基础装饰器

### 2.1 不带参数的装饰器

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("装饰器开始执行")
        result = func(*args, **kwargs)  # 调用原函数
        print("装饰器结束执行")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("Alice")
```

输出：

```text
装饰器开始执行
Hello, Alice!
装饰器结束执行
```

关键点：

- `@my_decorator` 等价于 `say_hello = my_decorator(say_hello)`。
- `wrapper` 包裹了原函数，调用时先执行装饰器的逻辑。

### 2.2 执行流程

1. **定义阶段**：定义装饰器函数 `my_decorator`。
2. **应用阶段**：函数定义时用 `@my_decorator` 标记目标函数，此时装饰器立即执行并替换原函数。
3. **运行阶段**：调用目标函数时，实际调用的是装饰器返回的 `wrapper`。

## 3. 带参数的装饰器（三层嵌套）

```python
def repeat(num_times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(num_times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Bob")
```

输出：

```text
Hello, Bob!
Hello, Bob!
Hello, Bob!
```

三层结构分工：

| 层 | 函数 | 职责 |
|---|---|---|
| 外层 | `repeat` | 接收装饰器参数 `num_times` |
| 中层 | `decorator` | 接收被装饰函数 `func` |
| 内层 | `wrapper` | 实现具体增强逻辑 |

## 4. functools.wraps 保留元数据

### 4.1 问题：装饰器会丢失原函数的元数据

元数据（Metadata）是描述函数自身的信息，包括：

- `__name__`：函数名称
- `__doc__`：文档字符串（docstring）
- `__module__`：所在模块
- `__qualname__`：限定名称（类中的情况）
- `__annotations__`：参数与返回值的类型注解

装饰后，原函数被**替换为 wrapper**，于是：

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def add(a, b):
    """加法函数"""
    return a + b

print(add.__name__)  # 输出: wrapper（错误！）
print(add.__doc__)   # 输出: None（wrapper 没有文档字符串）
```

### 4.2 解决方案：@wraps(func)

`functools.wraps` 本身也是一个装饰器，内部调用 `functools.update_wrapper(wrapper, func)`，把原函数的元数据**复制到包装函数**上：

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # 保留原函数的元数据
    def wrapper(*args, **kwargs):
        print("装饰器开始执行")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def add(a, b):
    """这是一个加法函数"""
    return a + b

print(add.__name__)  # 输出: add（正确）
print(add.__doc__)   # 输出: 这是一个加法函数（正确）
```

### 4.3 为什么必须保留元数据

- **调试**：函数名被覆盖后，调试器、堆栈信息里看到的都是 `wrapper` 而非真实函数名。
- **文档生成**：Sphinx 等工具读取 `__doc__` 生成文档，丢失后文档不完整。
- **反射**：其他代码可能依赖函数名或文档字符串（如 `help(add)`）。

**最佳实践：编写装饰器时始终加 `@wraps(func)`。**

## 5. 典型应用场景

### 5.1 日志记录

```python
from functools import wraps

def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result
    return wrapper

@log_decorator
def multiply(a, b):
    return a * b

multiply(3, 4)
```

输出：

```text
Calling multiply with args: (3, 4), kwargs: {}
Result: 12
```

### 5.2 权限验证（带参数的装饰器）

```python
from functools import wraps

def require_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if check_user_permission(permission):
                return func(*args, **kwargs)
            else:
                raise PermissionError("无权限访问！")
        return wrapper
    return decorator

@require_permission("admin")
def delete_data():
    print("数据删除成功！")
```

### 5.3 统一异常处理

装饰器 `log_exception` 的作用是统一捕获异常并记录警告：

```python
from functools import wraps

def log_exception(func):
    """异常处理装饰器：记录异常并返回 False/None"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"在 {func.__name__} 中发生异常: {str(e)}")
            # 根据函数类型返回 None 或 False，保持接口一致性
            return None if func.__name__ == 'read_data' else False
    return wrapper
```

关键点：

1. **异常捕获**：在 `try-except` 中调用原函数。
2. **日志记录**：捕获异常后记录 WARNING 级别日志。
3. **返回值处理**：根据函数类型返回 `None` 或 `False`，不改变调用方的使用方式。

## 6. 自定义装饰器三步法

以"记录函数执行时间"为例：

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

@timer
def compute_sum(n):
    return sum(range(n))

compute_sum(1000000)
```

输出：

```text
函数 compute_sum 执行时间: 0.0005 秒
```

## 7. 练习：执行时间 + 超时告警

任务：编写装饰器，记录函数执行时间；超过 1 秒时记录一条 WARNING 日志。

```python
import logging
import time
from functools import wraps

logging.basicConfig(level=logging.INFO)

def time_and_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logging.info(f"函数 {func.__name__} 执行时间: {elapsed:.4f} 秒")
        if elapsed > 1:
            logging.warning(f"警告：函数 {func.__name__} 执行时间过长！")
        return result
    return wrapper

@time_and_log
def slow_function():
    time.sleep(1.5)

slow_function()
```

输出：

```text
INFO:root:函数 slow_function 执行时间: 1.5005 秒
WARNING:root:警告：函数 slow_function 执行时间过长！
```

## 8. 总结

| 要点 | 说明 |
|---|---|
| 装饰器本质 | 函数的"包装器"，接收函数、返回新函数 |
| 语法糖 | `@deco` 等价于 `f = deco(f)`，在定义时立即生效 |
| 带参数的装饰器 | 三层嵌套：参数层 → 函数层 → 包装层 |
| 元数据 | 装饰会覆盖 `__name__`/`__doc__` 等，用 `functools.wraps` 修复 |
| 典型用途 | 日志、权限、异常处理、性能计时、重试 |

> 相关：`*args`/`**kwargs` 的细节与全局装饰器组织见 [[02-参数传递与全局装饰器]]；装饰器叠加的执行顺序（从下往上包裹）见 [[02-参数传递与全局装饰器|参数传递篇的注意事项]]。

---

回到：[[cs/dev/python/index|Python 导航]]　下一篇：[[02-参数传递与全局装饰器]]
