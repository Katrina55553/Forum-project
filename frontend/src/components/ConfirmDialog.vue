<script setup>
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

function onKeydown(e) {
  if (e.key === "Escape") handleCancel();
}
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div v-if="state.visible" class="confirm-overlay" @click.self="handleCancel" @keydown="onKeydown">
        <div class="confirm-box">
          <div class="confirm-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <p class="confirm-msg">{{ state.message }}</p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="handleCancel">取消</button>
            <button class="btn-confirm" @click="handleConfirm">确认</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(22, 19, 16, 0.55);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.confirm-box {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: 1.75rem;
  min-width: 320px;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  text-align: center;
}
.confirm-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(220, 38, 38, 0.12);
  color: var(--color-danger);
  margin-bottom: 1rem;
}
.confirm-msg {
  margin: 0 0 1.5rem;
  font-size: 1rem;
  color: var(--color-text);
  line-height: 1.6;
}
.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 0.6rem;
}
.confirm-actions button {
  padding: 0.55rem 1.4rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-confirm {
  background: var(--color-danger);
  color: #fff;
  border: none;
}
.btn-confirm:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
.btn-cancel {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}
.btn-cancel:hover {
  border-color: var(--color-text);
  color: var(--color-text);
}

.confirm-enter-active {
  transition: opacity 0.2s ease;
}
.confirm-enter-active .confirm-box {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}
.confirm-leave-active {
  transition: opacity 0.2s ease;
}
.confirm-leave-active .confirm-box {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.confirm-enter-from,
.confirm-leave-to {
  opacity: 0;
}
.confirm-enter-from .confirm-box,
.confirm-leave-to .confirm-box {
  transform: scale(0.92) translateY(10px);
  opacity: 0;
}
</style>
