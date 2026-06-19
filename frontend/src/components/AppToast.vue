<script setup>
import { useToastState } from "../composables/toast";

const { toasts } = useToastState();

function remove(id) {
  const idx = toasts.findIndex((t) => t.id === id);
  if (idx > -1) toasts.splice(idx, 1);
}

function iconFor(type) {
  if (type === "success") {
    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
  }
  if (type === "error") {
    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
  }
  return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
}
</script>

<template>
  <Teleport to="body">
    <div class="toast-container" v-if="toasts.length">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast-item"
          :class="t.type"
          @click="remove(t.id)"
        >
          <span class="toast-icon" v-html="iconFor(t.type)"></span>
          <span class="toast-message">{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style>
.toast-container {
  position: fixed;
  top: 88px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}
.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1.1rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  max-width: 360px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.toast-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.toast-message {
  flex: 1;
}
.toast-item.success {
  background: var(--color-success);
  color: #fff;
}
.toast-item.error {
  background: var(--color-danger);
  color: #fff;
}
.toast-item.info {
  background: var(--color-text);
  color: var(--color-bg);
}

.toast-enter-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  transform: translateX(120%);
  opacity: 0;
}
.toast-leave-to {
  transform: translateX(120%);
  opacity: 0;
}
</style>
