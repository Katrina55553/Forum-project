# 第十四章：全局组件与 Composable 模式

Vue 3 的全局组件 + composable 是实现 Toast 通知和确认对话框的轻量方案。

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

核心思路：**composable 管理状态，组件负责渲染，通过模块级 reactive 对象通信。**

## Toast 通知系统

### 状态管理（composables/toast.js）

```javascript
import { reactive } from "vue";

const state = reactive({
  toasts: [],
  _id: 0,
});

function showToast(message, type = "info", duration = 3000) {
  const id = state._id++;
  state.toasts.push({ id, message, type });
  setTimeout(() => {
    const idx = state.toasts.findIndex((t) => t.id === id);
    if (idx !== -1) state.toasts.splice(idx, 1);
  }, duration);
}

// 便捷方法
showToast.success = (msg) => showToast(msg, "success");
showToast.error = (msg) => showToast(msg, "error");
showToast.info = (msg) => showToast(msg, "info");

export function useToastState() {
  return state;
}

export { showToast };
```

**关键设计：**
- `state` 定义在模块顶层，不是定义在函数里。这意味着整个应用共享同一个响应式状态
- 3 秒后自动消失，`_id` 自增确保每个 toast 的唯一性
- `showToast.success/error/info` 是挂载到函数上的属性，调用简洁

### 渲染组件（AppToast.vue）

```html
<Teleport to="body">
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div v-for="t in state.toasts" :key="t.id" :class="['toast', t.type]">
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</Teleport>
```

```javascript
import { useToastState } from "../composables/toast";
const state = useToastState();
```

- `<Teleport to="body">` — 把 toast 渲染到 body 下，避免被父组件的 overflow hidden 裁切
- `<TransitionGroup>` — 列表动画，入场滑入、出场滑出

### 使用方式

任何 .vue 文件中都可以直接使用：

```javascript
import { showToast } from "../composables/toast";

// 成功提示
showToast.success("帖子发布成功");
// 错误提示
showToast.error("加载失败");
// 普通提示
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

function showConfirm(message) {
  state.message = message;
  state.visible = true;
  return new Promise((resolve) => {
    state.resolve = resolve;   // 把 resolve 存起来
  });
}

export function useConfirmState() {
  return state;
}

export { showConfirm };
```

**Promise 模式：** 点击"确认"或"取消"时调用 `state.resolve(true)` 或 `state.resolve(false)`，调用方通过 `await showConfirm(...)` 获取结果。

### 渲染组件（ConfirmDialog.vue）

```html
<Teleport to="body">
  <div v-if="state.visible" class="overlay" @click.self="cancel">
    <div class="dialog">
      <p>{{ state.message }}</p>
      <div class="actions">
        <button @click="confirm">确认</button>
        <button @click="cancel">取消</button>
      </div>
    </div>
  </div>
</Teleport>
```

```javascript
function confirm() {
  state.resolve(true);
  state.visible = false;
}
function cancel() {
  state.resolve(false);
  state.visible = false;
}

// ESC 键关闭
function onKeydown(e) {
  if (e.key === "Escape") cancel();
}
onMounted(() => document.addEventListener("keydown", onKeydown));
```

### 使用方式

```javascript
import { showConfirm } from "../composables/confirm";

async function deleteTopic(id) {
  const ok = await showConfirm("确定要删除这篇帖子吗？");
  if (ok) {
    await deleteTopic(id);
    showToast.success("已删除");
  }
}
```

## 回到顶部（BackToTop.vue）

```html
<Transition name="fade">
  <button v-if="visible" @click="scrollToTop" class="back-to-top">
    ↑
  </button>
</Transition>
```

```javascript
const visible = ref(false);

onMounted(() => {
  window.addEventListener("scroll", () => {
    visible.value = window.scrollY > 400;
  });
});

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}
```

## 设计模式总结

| 模式 | 说明 | 优势 |
|------|------|------|
| **模块级 reactive 状态** | 状态定义在 composable 模块顶层 | 全局共享，不需要 Pinia，足够轻量 |
| **Teleport to="body"** | 渲染到 body 下 | 避免 CSS 层叠问题 |
| **TransitionGroup** | 列表动画 | Toast 进出有平滑动画 |
| **Promise 桥接** | `showConfirm` 返回 Promise | 调用方用 await 等待结果，代码线性 |
| **函数挂载方法** | `showToast.success = fn` | 调用简洁，语义清晰 |
