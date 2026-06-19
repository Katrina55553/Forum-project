<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";

const visible = ref(false);

function onScroll() {
  visible.value = window.scrollY > 400;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => window.addEventListener("scroll", onScroll));
onBeforeUnmount(() => window.removeEventListener("scroll", onScroll));
</script>

<template>
  <Transition name="fade">
    <button v-if="visible" class="back-to-top" @click="scrollToTop" aria-label="回到顶部">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="19" x2="12" y2="5"/>
        <polyline points="5 12 12 5 19 12"/>
      </svg>
    </button>
  </Transition>
</template>

<style scoped>
.back-to-top {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 999;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transition: transform 0.25s ease, border-color 0.2s, color 0.2s, box-shadow 0.2s;
}
.back-to-top:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(184, 67, 31, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
