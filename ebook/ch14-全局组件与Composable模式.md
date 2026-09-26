# 第十四章：全局组件与 Composable 模式

Vue 3 的 composable + 全局组件，是实现 Toast 通知和确认对话框的轻量方案。本章讲四个组件：三个"全局挂载"的（AppToast、ConfirmDialog、BackToTop）和一个受控输入组件（TagInput）。

## Composable + Teleport 模式

```
composables/toast.js          ← 模块级响应式状态（轻量 Store）
       │
       ▼
components/AppToast.vue       ← Teleport 渲染到 body
       │
       ▼
在任何 .vue 文件中使用：
  import { showToast } from "../composables/toast";
  showToast.success("操作成功");
```

核心思路：**composable 管理状态，组件负责渲染，通过模块级 reactive 对象通信。** 状态放在模块顶层，就绕过了 Pinia——对一个只有几条 toast 的小系统来说，这就够了。

## Toast 通知系统

### 状态管理（composables/toast.js）

```javascript
import { reactive } from "vue";

const state = reactive({
  toasts: [],
  _id: 0,
});

export function showToast(message, type = "info", duration = 3000) {
  const id = ++state._id;                 // 自增后取，保证 id 从 1 开始且唯一
  state.toasts.push({ id, message, type });
  if (duration > 0) {                     // duration 为 0 表示"常驻不自动消失"
    setTimeout(() => {
      const idx = state.toasts.findIndex((t) => t.id === id);
      if (idx > -1) state.toasts.splice(idx, 1);
    }, duration);
  }
}

// 便捷方法
showToast.success = (msg, d) => showToast(msg, "success", d);
showToast.error = (msg, d) => showToast(msg, "error", d);
showToast.info = (msg, d) => showToast(msg, "info", d);

export function useToastState() {
  return state;
}
```

**关键设计：**

- `state` 定义在**模块顶层**，不是定义在函数里。整个应用共享同一个响应式对象——所有 `import` 拿到的是同一个实例
- `_id` 用 `++state._id` 自增，确保每个 toast 唯一
- `duration > 0` 才排定时器，把"常驻"留作一个可选项
- `showToast.success/error/info` 是挂在函数上的属性，调用简洁

### 渲染组件（AppToast.vue）

```html
<Teleport to="body">
  <div class="toast-container" v-if="toasts.length">
    <TransitionGroup name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast-item" :class="t.type" @click="remove(t.id)">
        <span class="toast-icon"><!-- success / error / info 三种 SVG --></span>
        <span class="toast-message">{{ t.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</Teleport>
```

```javascript
import { useToastState } from "../composables/toast";
const { toasts } = useToastState();
```

- `<Teleport to="body">` — 渲染到 body 下，避免被父组件的 `overflow: hidden` 裁切
- `<TransitionGroup>` — 列表动画，入场从右侧滑入、出场滑出
- 每种类型配一个图标（勾 / 叉 / 感叹号），点击 toast 可手动关闭

### 使用方式

```javascript
import { showToast } from "../composables/toast";

showToast.success("帖子发布成功");
showToast.error("加载失败");
showToast.info("已复制到剪贴板");
```

## 确认对话框系统

### 状态管理（composables/confirm.js）

```javascript
import { reactive } from "vue";

const state = reactive({
  visible: false,
  message: "",
  resolve: null,       // 保存 Promise 的 resolve 函数
});

export function showConfirm(message) {
  // 如果已有未完成的确认框，先拒绝它
  if (state.visible && state.resolve) {
    state.resolve(false);
  }
  return new Promise((resolve) => {
    state.message = message;
    state.visible = true;
    state.resolve = resolve;
  });
}

export function useConfirmState() {
  return state;
}
```

**Promise 模式：** `showConfirm` 返回一个 Promise，把 `resolve` 存进共享状态。用户点"确认"调 `resolve(true)`、点"取消"调 `resolve(false)`，调用方 `await` 即可拿到结果。

开头那段"先拒绝已有确认框"是个防御：如果上一个确认框还没关就又弹一个，旧的那个 Promise 会被 resolve 成 `false`（相当于自动取消），不会永久悬空。

### 渲染组件（ConfirmDialog.vue）

```javascript
import { useConfirmState } from "../composables/confirm";
const state = useConfirmState();

function handleConfirm() {
  state.resolve?.(true);
  state.visible = false;
}
function handleCancel() {
  state.resolve?.(false);
  state.visible = false;
}
```

```html
<Teleport to="body">
  <Transition name="confirm">
    <div v-if="state.visible" class="confirm-overlay" @click.self="handleCancel">
      <div class="confirm-box">
        <div class="confirm-icon"><!-- 警示三角 SVG --></div>
        <p class="confirm-msg">{{ state.message }}</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="handleCancel">取消</button>
          <button class="btn-confirm" @click="handleConfirm">确认</button>
        </div>
      </div>
    </div>
  </Transition>
</Teleport>
```

- 用 `@click.self` 实现"点遮罩层关闭"
- `state.resolve?.()` 用可选调用兜底，防止 resolve 还没挂上就点了按钮

### 使用方式

```javascript
import { showConfirm } from "../composables/confirm";

async function remove(id) {
  const ok = await showConfirm("确定删除这条评论吗？");
  if (!ok) return;
  await deleteComment(id);
  showToast.success("评论已删除");
}
```

## 回到顶部（BackToTop.vue）

```html
<Transition name="fade">
  <button v-if="visible" class="back-to-top" @click="scrollToTop" aria-label="回到顶部">
    <svg ...><!-- 向上箭头 --></svg>
  </button>
</Transition>
```

```javascript
const visible = ref(false);

function onScroll() {
  visible.value = window.scrollY > 400;   // 滚动超过 400px 才出现
}
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => window.addEventListener("scroll", onScroll));
onBeforeUnmount(() => window.removeEventListener("scroll", onScroll));
```

注意监听函数 `onScroll` 被**具名声明**了，而不是写成匿名箭头函数——因为 `removeEventListener` 必须传入同一个函数引用才能移除。这是"注册与注销必须配对"的又一例。

## 受控输入组件 — TagInput.vue

`TagInput.vue` 是一个标准的 `v-model` 组件，用于发帖时编辑标签。它不属于全局挂载组件，而是被 `TopicEditView` 局部引入。

```javascript
const props = defineProps({
  modelValue: { type: Array, default: () => [] },   // v-model 值（标签名数组）
  suggestions: { type: Array, default: () => [] },  // 热门标签建议
});
const emit = defineEmits(["update:modelValue"]);

const input = ref("");
const tags = ref([...props.modelValue]);

// 外部值变化时同步到内部（比如编辑帖子时异步加载出标签）
watch(() => props.modelValue, (val) => {
  tags.value = [...val];
});
```

**交互规则：**

- 回车或逗号 `,` 添加当前输入（`onKeydown` 里 `preventDefault` 后 `addTag`）
- 输入框为空时按 Backspace 删除最后一个标签
- 点击"热门标签"建议直接加入，已加入的会高亮
- 已存在的标签不重复添加

```javascript
function onKeydown(e) {
  if (e.key === "Enter" || e.key === ",") {
    e.preventDefault();
    addTag(input.value);
  }
  if (e.key === "Backspace" && !input.value && tags.value.length) {
    tags.value.pop();
    emit("update:modelValue", tags.value);
  }
}
```

**为什么内部要维护一份 `tags` 副本？** `v-model` 是单向数据流——子组件不能直接改 `props.modelValue`。所以内部用 `tags` 做副本，改完通过 `emit("update:modelValue", ...)` 把新数组交回父组件。同时用 `watch` 监听 `props.modelValue`，当父组件传入的数组整体变化（例如异步拉到了帖子的原有标签）时再同步回内部。这套"props 进、emit 出、watch 兜底同步"就是 Vue 3 里写受控组件的标准姿势。

## 设计模式总结

| 模式 | 说明 | 优势 |
|------|------|------|
| **模块级 reactive 状态** | 状态定义在 composable 模块顶层 | 全局共享，不必上 Pinia，足够轻量 |
| **Teleport to="body"** | 渲染到 body 下 | 避开父组件 `overflow` 裁切与层叠问题 |
| **TransitionGroup** | 列表进出动画 | Toast 有平滑的滑动效果 |
| **Promise 桥接** | `showConfirm` 返回 Promise | 调用方用 `await` 线性书写，逻辑清晰 |
| **函数挂载方法** | `showToast.success = fn` | 调用简洁、语义清晰 |
| **v-model 受控组件** | props 进 / emit 出 / watch 同步 | 单向数据流，父组件始终是数据源 |

## 本章要点

- composable 管状态、组件管渲染，靠模块级 reactive 对象通信，无需 Pinia
- Toast 的 `_id` 用 `++state._id`，`duration > 0` 才自动消失
- ConfirmDialog 用 Promise 桥接结果；新弹框会先把旧 Promise resolve 成 `false`
- 事件监听函数要具名声明，才能被 `removeEventListener` 正确移除
- `TagInput` 是 `v-model` 组件：`modelValue` 进、`update:modelValue` 出，`watch` 兜底同步
