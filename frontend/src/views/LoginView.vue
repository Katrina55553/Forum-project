<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function handleLogin() {
  error.value = "";
  if (!username.value || !password.value) {
    error.value = "请填写用户名和密码";
    return;
  }
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    const redirect = route.query.redirect;
    const safeRedirect = (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')) ? redirect : '/';
    router.push(safeRedirect);
  } catch (e) {
    error.value = e.response?.data?.detail || "登录失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="form-page">
    <div class="form-card">
      <div class="form-header">
        <div class="form-mark">✦</div>
        <p class="form-eyebrow">欢迎回来</p>
        <h1>登录</h1>
        <p class="form-sub">继续你未完成的话题。</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div v-if="error" class="error">{{ error }}</div>
        <label>
          <span>用户名</span>
          <input v-model="username" type="text" autocomplete="username" placeholder="输入你的用户名" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" autocomplete="current-password" placeholder="输入你的密码" />
        </label>
        <button type="submit" :disabled="loading">
          {{ loading ? "登录中..." : "登录" }}
        </button>
      </form>
      <p class="switch">
        还没有账号？<router-link to="/register">立即注册 →</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.form-page {
  max-width: 420px;
  margin: 3rem auto;
  padding: 0 1rem;
}
.form-card {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: 2.5rem 2.2rem;
  box-shadow: var(--shadow-md);
}
.form-header {
  text-align: center;
  margin-bottom: 2rem;
}
.form-mark {
  font-size: 1.6rem;
  color: var(--color-primary);
  margin-bottom: 0.6rem;
}
.form-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin: 0 0 0.4rem;
}
h1 {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  margin: 0 0 0.4rem;
  color: var(--color-text);
  letter-spacing: -0.02em;
}
.form-sub {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.92rem;
}
form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
label span {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  letter-spacing: 0.02em;
}
input {
  width: 100%;
  padding: 0.75rem 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.95rem;
  box-sizing: border-box;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
input::placeholder { color: var(--color-text-muted); }
input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}
button {
  margin-top: 0.4rem;
  padding: 0.85rem;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: var(--radius);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.error {
  color: var(--color-danger);
  background: var(--color-danger-bg);
  padding: 0.7rem 0.9rem;
  border-radius: var(--radius);
  font-size: 0.88rem;
  border-left: 3px solid var(--color-danger);
}
.switch {
  text-align: center;
  margin: 1.5rem 0 0;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}
.switch a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}
.switch a:hover { color: var(--color-primary-hover); }
</style>
