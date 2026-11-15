---
tags: [java]
created: 2026-11-15
updated: 2026-11-15
status: ok
---

# Java 泛型擦除与反射建数组

## 为什么不能 new T[]

```java
public static <T> T[] merge(T[] a, T[] b) {
    T[] result = new T[a.length + b.length]; // 编译错误：Cannot create a generic array of T
}
```

Java 泛型在编译期完成类型检查，编译后类型参数被擦除，字节码中只剩原始类型（`Object`）。运行时 JVM 不知道 `T` 是什么，而数组是协变且带运行时类型检查的结构——`String[]` 与 `Object[]` 在运行时是不同的类型，无法在不知道元素类型的前提下分配。

`List<String>` 和 `List<Integer>` 运行时都是 `ArrayList`，同理。

## 解法：Array.newInstance

```java
public static <T> T[] concatenate(T[] a, T[] b, Class<T> clazz) {
    @SuppressWarnings("unchecked")
    T[] result = (T[]) Array.newInstance(clazz, a.length + b.length);
    System.arraycopy(a, 0, result, 0, a.length);
    System.arraycopy(b, 0, result, a.length, b.length);
    return result;
}
```

`Array.newInstance(Class<?> componentType, int length)` 在运行时按指定元素类型分配数组，返回 `Object`，因此需要强转。该强转必然产生 unchecked 警告——正确性依赖调用方传入的 `clazz` 与实际类型一致，编译器无法校验。

调用方据此免去显式类型推断：

```java
String[] merged = concatenate(new String[]{"a", "b"}, new String[]{"c", "d"}, String.class);
```

## 完整工具类

原稿此处的 `if (b == null) b = (T, 0);` 是语法错误，无法编译。修正版：

```java
import java.lang.reflect.Array;
import java.util.Objects;

public class ArrayUtils {

    public static <T> T[] concatenate(T[] a, T[] b, Class<T> clazz) {
        Objects.requireNonNull(clazz, "clazz");
        if (a == null) a = newArray(clazz, 0);
        if (b == null) b = newArray(clazz, 0);

        T[] result = newArray(clazz, a.length + b.length);
        System.arraycopy(a, 0, result, 0, a.length);
        System.arraycopy(b, 0, result, a.length, b.length);
        return result;
    }

    /** 从首个参数推断元素类型，调用处无需再传 Class。 */
    @SuppressWarnings("unchecked")
    public static <T> T[] concatenate(T[] a, T[] b) {
        Objects.requireNonNull(a, "a");
        Objects.requireNonNull(b, "b");
        Class<T> clazz = (Class<T>) a.getClass().getComponentType();
        return concatenate(a, b, clazz);
    }

    @SuppressWarnings("unchecked")
    private static <T> T[] newArray(Class<T> clazz, int length) {
        return (T[]) Array.newInstance(clazz, length);
    }
}
```

`a.getClass().getComponentType()` 返回数组的元素类型，可省去显式传 `Class`；代价是又一次 unchecked 强转，原理相同。

## 边界：基本类型数组

原稿称"基本类型没有对应的 Class 对象，不能用于此方法"，**结论与原因都不成立**。实测（OpenJDK 17）：

```
int.class                -> int
int.class == Integer.class -> false
Array.newInstance(int.class, 3) 返回类型 -> [I   // 即 int[]
```

`int.class` 是合法对象，`Array.newInstance(int.class, n)` 也能正常创建基本类型数组。

真正的限制在**方法签名**上：泛型类型参数 `T` 只能绑定引用类型，所以 `T[]` 永远不可能是 `int[]`，也没法把 `int[]` 传给 `T[]` 形参。要处理基本类型数组，只能另写重载：

```java
public static int[] concatenate(int[] a, int[] b) {
    int[] result = new int[a.length + b.length];
    System.arraycopy(a, 0, result, 0, a.length);
    System.arraycopy(b, 0, result, a.length, b.length);
    return result;
}
```

八种基本类型各需一份，或改用 `IntStream` 等流式 API 规避。

## 运行时类型检查的代价

```java
String[] bad = (String[]) new Object[2];  // 编译通过，运行期 ClassCastException
```

数组协变的方向是单向的：`String[]` 可以赋给 `Object[]`，反向强转会在运行期失败。这也是为什么"先 `new Object[n]` 再强转 `T[]`"行不通——数组的真实类型在分配时就已确定，无法事后改变。

## 跨语言对比

| 语言 | 泛型实现 | 能否直接 `new T[]` | 运行时保留泛型信息 |
|---|---|---|---|
| Java（含最新版本） | 类型擦除 | 否 | 否 |
| C# / .NET | 具象化（Reified） | 可以 | 是 |
| C++ 模板 | 编译期单态化 | 可以 | 编译后消失 |
| Rust | 默认单态化 | 可以 | 否 |
| Go 1.18+ | 形状化（shape-based） | 可以 | 否 |
| Kotlin（JVM） | 擦除 + `reified` 语法糖 | `arrayOfNulls<T>(n)` 可用，取 `T::class` 需 `reified` | 原生擦除 |
| TypeScript | 完全擦除 | 可写 `new Array<T>()`，运行时无类型 | 否 |

差异根源在引入泛型时的约束条件：Java 5 需要兼容海量存量字节码，只能选擦除，保证新旧代码二进制互通；C# 2.0 时 .NET 生态尚新，选择改造 CLR 以换取值类型的真实特化；C++、Rust、Go 都在编译期生成具体代码，不存在运行期类型参数的概念。

## Valhalla 现状

截至 2026 年 11 月：

- JEP 401（Value Objects，Preview）已集成到 OpenJDK 主线，目标版本 JDK 28（计划 2027 年 3 月发布），默认关闭。
- **泛型特化（specialized generics）仍未交付**，尚处于研究阶段，不在 JDK 28 范围内。
- `ArrayList` 依旧基于引用数组，装箱开销不变。

因此"Java 泛型靠擦除实现、不能 `new T[]`"在可预见的版本内仍然成立。

> 修正：原稿称"Java 从 1.5 到最新 Java 24 泛型底层依然是类型擦除，Valhalla 迟迟没有正式发布"。结论方向正确，但版本信息已过期——值类特性已进入 JDK 28 预览，需要区分"值类"与"泛型特化"两件事，后者才是解决 `List<int>` 与泛型数组的关键。

## 面试回答

> 为什么 Java 不能 `new T[]`？
>
> 泛型在编译期被擦除，运行时 JVM 拿不到 `T` 的实际类型；而数组在分配时必须确定元素类型并参与运行时类型检查，两者冲突，所以编译器禁止创建泛型数组。解决方案是用 `Array.newInstance(clazz, length)` 在运行时按 `Class` 对象分配，再强转为 `T[]`，代价是需要调用方提供正确的 `Class<T>` 并承担一次 unchecked 强转。

## 相关

- [[创建maven项目]]
