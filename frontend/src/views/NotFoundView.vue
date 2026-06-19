<template>
  <div class="not-found">
    <div class="nf-inner">
      <div class="nf-eyebrow">迷失方向 · LOST</div>
      <h1 class="nf-code">4<span class="nf-mark">✦</span>4</h1>
      <p class="nf-title">页面未找到</p>
      <p class="nf-subtitle">你访问的页面可能已被移除、重命名，或从未存在。</p>
      <div class="nf-actions">
        <router-link to="/" class="nf-primary">返回首页</router-link>
        <router-link to="/" class="nf-ghost">浏览话题</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 1.5rem;
}
.nf-inner {
  text-align: center;
  max-width: 520px;
}
.nf-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}
.nf-code {
  font-family: var(--font-display);
  font-size: clamp(5rem, 18vw, 9rem);
  font-weight: 600;
  line-height: 0.9;
  letter-spacing: -0.04em;
  margin: 0 0 1rem;
  color: var(--color-text);
}
.nf-mark {
  display: inline-block;
  color: var(--color-primary);
  transform: translateY(-0.1em);
  font-size: 0.7em;
}
.nf-title {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 500;
  margin: 0 0 0.75rem;
  color: var(--color-text);
}
.nf-subtitle {
  color: var(--color-text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 2.5rem;
}
.nf-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}
.nf-primary {
  display: inline-flex;
  align-items: center;
  padding: 0.7rem 1.6rem;
  background: var(--color-primary);
  color: #fff;
  border-radius: 999px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 14px rgba(184, 67, 31, 0.25);
}
.nf-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(184, 67, 31, 0.35);
}
.nf-ghost {
  display: inline-flex;
  align-items: center;
  padding: 0.7rem 1.6rem;
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: border-color 0.2s ease, background 0.2s ease;
}
.nf-ghost:hover {
  border-color: var(--color-text);
  background: var(--color-bg-elevated);
}
</style>
