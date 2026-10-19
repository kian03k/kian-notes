---
tags: [vue, vue3, 组件通信, 前端]
created: 2026-10-19
updated: 2026-10-19
status: ok
---

# Vue3 组件通信

> 四种方向、四种写法，附 Vue2 对照。选型看文末那张表。

## 一、一览

| 方向 | Vue2 | Vue3（`<script setup>`） |
| --- | --- | --- |
| 父 → 子 | `props: {}` | `defineProps()` |
| 子 → 父 | `this.$emit()` | `defineEmits()` |
| 父调子方法 | `this.$refs.school.loadData()` | `ref` + `defineExpose()` |
| 跨层级（祖 → 孙） | 事件总线 `$bus` / 逐层传 | `provide()` / `inject()` |

## 二、父传子：props

```vue
<!-- 子组件 School.vue -->
<script setup>
const props = defineProps({
  teacherName: String,
  salary: Number,
  age: { type: Number, required: true, default: 0 },
})
console.log(props.teacherName)
</script>

<template>
  <h3>{{ teacherName }} · {{ salary + 1000 }} · {{ age }}</h3>
</template>
```

```vue
<!-- 父组件 App.vue -->
<script setup>
import School from './components/School.vue'
const age = ref(20)
</script>

<template>
  <School teacher-name="王强" :salary="5000" :age="age" />
</template>
```

要点：

- `defineProps` / `defineEmits` 是**编译宏**：不用 `import`，且必须在 `<script setup>` **顶层**调用（放进函数或 `if` 里会报错）。
- `:salary="5000"` 带冒号 = 传**表达式**（数字）；不带冒号 = 传字符串 `"5000"`。
- props 是**单向只读**的：子组件直接改会告警，要改就 `emit` 出去让父改。
- 也支持类型声明式写法：`defineProps<{ age: number }>()`（需要 TS）。

## 三、子传父：emit

```vue
<!-- 子组件 -->
<script setup>
const emit = defineEmits(['funGetAddress'])

const sendAddress = () => {
  emit('funGetAddress', '浙江大学软件学院')   // 事件名 + 参数
}
</script>

<template>
  <button @click="sendAddress">发送学校地址</button>
</template>
```

```vue
<!-- 父组件 -->
<script setup>
const myAddress = ref('')
const getAddress = (address) => { myAddress.value = address }
</script>

<template>
  <h2>学校地址:{{ myAddress }}</h2>
  <School @funGetAddress="getAddress" />
</template>
```

要点：

- 没在 `defineEmits` 里声明的事件名，`emit` 出去不会生效（相当于没注册）。
- 事件名在**模板里推荐 kebab-case**（`@fun-get-address`）；DOM 内模板（直接写 HTML）不区分大小写，用 camelCase 会失效。
- `v-model` 本质就是 `props + emit`，组件上写 `v-model` 等于 `:modelValue` + `@update:modelValue`。

## 四、父调子方法：模板引用

```vue
<!-- 父组件 -->
<script setup>
import { ref, onMounted } from 'vue'
const school = ref(null)          // 名字要和模板里的 ref 属性一致

onMounted(() => {
  school.value.loadData({ id: 1, name: 'jack' })   // 父组件主动调子组件方法
})
</script>

<template>
  <School ref="school" />
</template>
```

```vue
<!-- 子组件 -->
<script setup>
const loadData = (data) => console.log(data)

defineExpose({ loadData })        // ⚠️ 必须暴露，否则父组件拿不到
</script>
```

要点：

- **`<script setup>` 组件默认是封闭的**，不写 `defineExpose` 父组件调用会拿到 `undefined`（或代理上空空如也）。
- `ref` 的值在 **`onMounted` 之后**才有，`setup` 同步阶段是 `null`。
- 只能调方法，**不能**靠它改子组件内部状态（改状态还是走 props）。

## 五、跨层级：provide / inject

```vue
<!-- 顶层组件 App.vue -->
<script setup>
import { provide, ref } from 'vue'
const studentName = ref('jack')
provide('studentName', studentName)         // key, value
</script>

<template><School /></template>
```

```vue
<!-- 任意深度的后代 Student.vue（中间层不用转发） -->
<script setup>
import { inject } from 'vue'
const studentName = inject('studentName', '默认值')   // 第二个参数是兜底
</script>

<template><h2>学生姓名：{{ studentName }}</h2></template>
```

要点：

- **provide 只能向下传**，拿不到上层；同级兄弟要绕到共同父级 provide。
- 想让下游能改，就 **provide 一个 `ref`**，下游 `inject` 后改 `.value`（响应式会跟着走）。
- 不想让下游改，就 provide `readonly(state)`。
- `inject` 也要在 `setup` 顶层同步调用。
- 语义上是"**依赖注入**"，不是全局变量 —— key 用 `Symbol` 更安全（避免重名）。

### 为什么不继续用事件总线

Vue2 里常用的 `Vue.prototype.$bus = this` + `$on/$emit`，在 Vue3 **实例上已经删掉了 `$on/$off/$once`**（`$emit` 保留），老代码会直接报错。要么装 `mitt`，要么改用 `provide/inject` 或状态库（Pinia）。事件总线的问题本来就是：**谁发的、谁收的，全局看不见**，调试困难。

## 六、怎么选

| 场景 | 用什么 |
| --- | --- |
| 父传数据给子 | `props` |
| 子通知父（点击、提交、改值） | `emit` |
| 父要主动触发子组件里的方法（如弹窗 `open()`） | 模板引用 + `defineExpose` |
| 祖孙跨多层、中间层只是"路过" | `provide` / `inject` |
| 兄弟组件通信 | 状态提升到共同父级，或 Pinia |
| 全局共享（登录用户、主题） | Pinia（`provide/inject` 也行，但状态库更好调试） |

## 七、坑清单

1. `defineExpose` 忘了写 —— 父组件 `ref` 拿到但调不动子方法。
2. 模板里事件名大小写写错（`@funGetAddress` 在 DOM 内模板里失效）。
3. `emit` 里的参数超过一个时，父组件收到的是多个位置参数，不是一个数组。
4. `inject` 拿到的 `ref` 忘了 `.value`。
5. `props` 里对象/数组是引用传递，子组件**改内部属性**不会告警，但**改了父组件的数据** —— 属于隐性副作用，尽量避免。
