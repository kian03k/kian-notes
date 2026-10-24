---
tags: [android, fragment, activity, 界面开发]
created: 2026-10-24
updated: 2026-10-24
status: ok
---

# Fragment 与 Activity：什么时候用哪个

> 整理自 2018 年的一篇博客（作者 _VITA），内容属**传统 View 体系**。概念仍然成立，但代码是当年的写法；Compose 时代的替代方案见文末。
> 结论先给：**不存在"该不该用 Fragment"，只有"这个界面需不需要模块化复用"**。

## 一、Activity 与 Fragment 的职责

| | Activity | Fragment |
| --- | --- | --- |
| 定位 | 一个独立屏幕，生命周期由系统管理 | 可复用的界面片段，依附于宿主 Activity |
| 复用性 | 差，跨页面复用要重复代码 | 好，可嵌进任意 Activity |
| 生命周期 | 完整一整套 | 依附宿主，多几个回调（`onAttach` / `onCreateView` / `onDestroyView` / `onDetach`） |
| 通信 | 通过 Intent / 接口 | 通过宿主 Activity 中转 |

一句话：**Activity 是"页面"，Fragment 是"页面里的模块"。**

## 二、该用 Fragment 的场景

1. **一个 Activity 需要模块化**
   把界面拆成独立 Fragment，可以嵌进任何界面，不用复制代码。

2. **主页多 Tab 切换**
   每个 tab 一个 Fragment，这是最常见的用法。同一页面内多种布局切换也适用。

3. **手机 / 平板适配**
   同一套 Fragment，在手机上分屏显示，在平板上左右并排。

4. **多步骤流程**
   注册流程（用户名 → 密码 → 手机号）每一步做成一个 Fragment，配合回退栈天然支持"上一步"，比开多个 Activity 干净得多。

## 三、Fragment 切换的标准套路

```java
FragmentManager fm = getSupportFragmentManager();
FragmentTransaction ft = fm.beginTransaction();

ft.hide(firstStepFragment);

if (secondStepFragment == null) {
    ft.add(R.id.fl_content, secondStepFragment);
} else {
    ft.show(secondStepFragment);
}

ft.addToBackStack(null);
ft.commit();
```

**`hide()` 与 `replace()` 的区别**（原文强调的点）：

- `hide()`：隐藏旧 Fragment 但不销毁视图，用户返回时**之前填的内容还在**
- `replace()`：移除旧 Fragment，视图销毁，返回时要重建，状态容易丢

多步骤表单这类场景应该用 `hide()` + `show()`。

## 四、Activity 管理 Fragment 的架构思路

原文给出的做法（个人经验，非官方推荐）：

1. 用 `FragmentManager` 管理当前显示的 Fragment 列表，`detach` 后与视图树断开联系的放入 backstack
2. 建一个 `HashMap` 缓存已实例化的 Fragment，复用时直接取，顺带解决 Fragment 重叠问题
3. 写 `BaseFragment`，子 Fragment 继承它并定义对外接口，Activity 实现接口方法——本质上就是**观察者模式**

```java
public class BaseFragment extends Fragment implements View.OnClickListener {

    public interface IOneFragmentClickListener {
        void onOneFragmentClick();
    }

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View contentView = inflater.inflate(R.layout.fragment_one, null);
        contentView.findViewById(R.id.edt_one).setOnClickListener(this);
        return contentView;
    }

    @Override
    public void onClick(View v) {
        if (getActivity() instanceof IOneFragmentClickListener) {
            ((IOneFragmentClickListener) getActivity()).onOneFragmentClick();
        }
    }
}
```

宿主 Activity 实现 `IOneFragmentClickListener`，Fragment 就能回调它——这是 Fragment 调 Activity 最经典的方式。

## 五、生命周期对照

Fragment 比 Activity 多出来的回调，按执行顺序：

```text
onAttach → onCreate → onCreateView → onViewCreated → onActivityCreated
       → onStart → onResume
       → onPause → onStop → onDestroyView → onDestroy → onDetach
```

几个容易踩的点：

| 回调 | 说明 |
| --- | --- |
| `onCreateView` | 返回 Fragment 的视图，只在这里 inflate |
| `onViewCreated` | 视图已创建，初始化控件、绑定数据放这里 |
| `onDestroyView` | **视图销毁但 Fragment 还活着**，要在这里清理视图引用，否则泄漏 |
| `onDetach` | 与 Activity 解除关联，之后 `getActivity()` 返回 null |
| `setHasOptionsMenu(true)` | 不调用就不会走 `onCreateOptionsMenu` |

Activity 侧的顺序则是：`onCreate → onStart → onResume → onPause → onStop → onDestroy`。

> 网上流传的那张"Fragment 与 Activity 生命周期对照图"值得存一张在手边，两者是交错的：Activity 的 `onCreate` 里挂 Fragment，Fragment 的 `onCreateView` 通常在 Activity 的 `onCreate` 之后、`onResume` 之前。

## 六、三者之间的通信规则

| 方向 | 方式 |
| --- | --- |
| Activity → Fragment | `findFragmentById()` / `findFragmentByTag()` 拿到实例直接调方法 |
| Fragment → Activity | `getActivity()` 强转成宿主类型，或走接口回调 |
| Fragment ↔ Fragment | **不要直接通信**，全部交给宿主 Activity 中转 |

原文的总结是"高内聚、低耦合"：Fragment 只管好自己的事，所有跨 Fragment 的显示控制都交给 Activity 统一调度。

## 七、时代说明：现在还这么写吗

这篇内容写于 2018 年，代码是 `support-v4` 那一代。现在的实际情况：

- **维护老项目**：上面这套仍然必须懂，尤其 `hide/show`、backstack、生命周期顺序，面试也常问
- **新项目（View 体系）**：优先用 **Navigation Component** 管理 Fragment 切换，手写 `FragmentTransaction` 已经很少了
- **新项目（Compose）**：单 Activity + Composable，**Fragment 基本不用了**，生命周期也换成 `remember` / `LaunchedEffect` 那套

所以：**概念值得记，代码别照抄。**

## 八、常见 tab 结构（原文手绘）

```text
Activity（主页面）
├── toolbar
├── 内容区（Fragment 容器）
└── 底部 tab
     ├── 首页    → Fragment
     ├── 分类    → Fragment
     ├── 购物车  → Fragment
     └── 个人中心 → Fragment
```

每个 tab 是一个 Fragment，Activity 只负责容器和切换——这就是标准的多 tab 骨架。
