---
tags: [python, 语法]
created: 2026-11-18
updated: 2026-11-18
status: ok
---

# for 循环中的三种"跳出"方式

在 `for` 循环的 `if` 分支里，常见的三类需求对应不同写法：**跳过分支剩余代码**、**跳过本次迭代**、**退出整个循环**。

## 一、跳过当前 if 分支的剩余代码

"跳出当前分支"指跳过该 `if` 块内剩余语句，但**继续循环**——不需要 `break`。

**写法 1：`continue`**（在循环内最直接）

```python
for i in range(5):
    if i % 2 == 0:
        print(f"进入偶数分支: {i}")
        if i == 2:
            print("i 是 2，跳过后续操作")
            continue  # 跳过本次循环剩余代码，进入下一次迭代
        print("这行不会在 i==2 时执行")
    print("循环体其他代码")
```

**写法 2：`else` 分支**（逻辑更清晰，避免嵌套）

```python
for i in range(5):
    if i % 2 == 0:
        print(f"进入偶数分支: {i}")
        if i == 2:
            print("i 是 2，跳过后续操作")
        else:
            print("这行只在 i!=2 时执行")
    print("循环体其他代码")
```

> 注意：`continue` 跳过的是**当前循环迭代**，不是 `if` 分支本身。若只想跳过 `if` 块内剩余语句而不影响循环节奏，用 `else` 结构更合适。

## 二、结束本次迭代：continue

`continue` 跳过本次循环体中**剩余的所有代码**，直接进入下一次迭代。

```python
for i in range(5):
    if i % 2 == 0:
        if i == 2:
            print("遇到 2，跳过本次循环")
            continue
        print(f"偶数但不是2: {i}")
    print(f"循环第 {i} 次完成")
```

输出：

```text
偶数但不是2: 0
循环第 0 次完成
遇到 2，跳过本次循环
循环第 2 次完成
偶数但不是2: 4
循环第 4 次完成
```

## 三、结束整个循环：break

`break` 立即终止整个 `for` 循环，不再执行后续任何迭代。

```python
for i in range(5):
    if i % 2 == 0:
        if i == 2:
            print("遇到 2，立即退出整个循环")
            break
        print(f"偶数但不是2: {i}")
    print(f"循环第 {i} 次完成")

print("循环结束后执行")
```

输出：

```text
偶数但不是2: 0
循环第 0 次完成
遇到 2，立即退出整个循环
循环结束后执行
```

## 对比总结

| 目标 | 关键词 | 作用 |
|---|---|---|
| 跳过当前 `if` 分支的剩余代码 | `else` / 逻辑控制 | 不执行 `if` 内后续语句，但继续循环 |
| 结束当前循环迭代（继续下一次） | `continue` | 跳过本次循环剩余代码，进入下一次迭代 |
| 结束整个 `for` 循环 | `break` | 立即退出整个循环，不再执行任何后续迭代 |

## Python 没有 goto：多层跳出用函数 + return

Python 没有 C 的 `goto`，无法直接"跳出多层 if"，只能通过：

- `else` 结构；
- `continue` / `break` 控制循环；
- **函数 + `return`**（在函数内时，一步退出所有层）。

```python
def process():
    for i in range(5):
        if i % 2 == 0:
            if i == 2:
                print("遇到2，退出函数")
                return  # 直接退出整个函数，包括所有循环层
            print(f"偶数: {i}")
        print("循环中")

process()
print("函数执行完毕")
```

适用于需要**直接退出整个逻辑流程**的情况。

## 推荐写法

```python
for i in range(10):
    if condition1:
        if condition2:
            print("满足条件2，跳过本次循环")
            continue
        print("只在 condition1 为真且 condition2 为假时执行")
    else:
        print("condition1 不成立")

    # 循环体的其他代码
```

清晰、易读、无嵌套混乱。更复杂的场景（如多层嵌套循环）可结合 `for-else` 或标志变量控制，但一般不建议过度嵌套。

---

上一篇：[[03-面向对象]]　回到：[[cs/dev/python/index|Python 场景索引]]
