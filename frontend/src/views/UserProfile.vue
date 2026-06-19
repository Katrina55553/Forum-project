<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getUserProfile } from "../api/user";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const profile = ref(null);
const loading = ref(true);
const error = ref("");

async function fetchProfile() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getUserProfile(route.params.username);
    profile.value = res.data;
  } catch {
    error.value = "用户不存在或加载失败";
  } finally {
    loading.value = false;
  }
}

// 防止 javascript: 等 XSS 协议
function isSafeUrl(url) {
  try {
    const u = new URL(url, window.location.origin);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

// 路由参数变化时重新加载（同组件复用场景）
watch(() => route.params.username, (newName) => {
  if (newName) fetchProfile();
});

onMounted(fetchProfile);
</script>

<template>
  <div class="user-profile">
    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchProfile">重试</button>
    </div>
    <div v-else-if="profile">
      <div class="profile-header">
        <div class="avatar">
          <img v-if="profile.avatar" :src="profile.avatar" :alt="profile.username" />
          <span v-else class="avatar-initial">{{ profile.username[0]?.toUpperCase() }}</span>
        </div>
        <p class="profile-eyebrow">成员 · MEMBER</p>
        <h1>{{ profile.username }}</h1>
        <div class="stats">
          <div class="stat">
            <span class="stat-num">{{ profile.topic_count || 0 }}</span>
            <span class="stat-label">帖子</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-num">{{ profile.comment_count || 0 }}</span>
            <span class="stat-label">回复</span>
          </div>
        </div>
        <p v-if="profile.bio" class="bio">{{ profile.bio }}</p>
        <div class="profile-meta">
          <a v-if="profile.github_url && isSafeUrl(profile.github_url)" :href="profile.github_url" target="_blank" rel="noopener noreferrer" class="github-link">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            GitHub
          </a>
          <span class="join-date">加入于 {{ new Date(profile.created_at).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
        </div>
        <button
          v-if="auth.user && auth.user.username !== profile.username"
          class="btn-message"
          @click="router.push(`/messages/${profile.username}`)"
        >
          发私信
        </button>
      </div>
      <section class="user-topics">
        <h2>帖子</h2>
        <div v-if="profile.topics?.length">
          <article v-for="t in profile.topics" :key="t.id" class="card">
            <router-link :to="`/topic/${t.id}`" class="card-link" :aria-label="t.title"></router-link>
            <h3 class="title">{{ t.title }}</h3>
            <div class="meta">
              <span>{{ new Date(t.created_at).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
              <span class="meta-dot">·</span>
              <span class="meta-stat">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                {{ t.comment_count || 0 }}
              </span>
              <span class="meta-dot">·</span>
              <span class="meta-stat">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                {{ t.likes_count || 0 }}
              </span>
            </div>
          </article>
        </div>
        <p v-else class="state">暂无帖子</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.user-profile { max-width: 720px; margin: 0 auto; }
.state { text-align: center; padding: 3rem; color: var(--color-text-muted); }
.error { color: var(--color-danger); }
.btn-retry {
  margin-top: 0.8rem;
  padding: 0.5rem 1.4rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-bg-elevated);
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.88rem;
  transition: all 0.2s ease;
}
.btn-retry:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.profile-header {
  text-align: center;
  padding: 2.5rem 1rem 2rem;
  margin-bottom: 2.5rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}
.profile-header::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 80px;
  background: linear-gradient(135deg, var(--color-primary-soft), transparent);
  opacity: 0.6;
}
.avatar {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid var(--color-bg-elevated);
  box-shadow: var(--shadow-md);
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-initial {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 700;
  color: #fff;
}
.profile-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin: 0 0 0.3rem;
  font-weight: 500;
  position: relative;
}
h1 {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 1rem;
  letter-spacing: -0.02em;
  position: relative;
}
.stats {
  display: inline-flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.6rem 1.5rem;
  background: var(--color-bg-secondary);
  border-radius: 999px;
  margin-bottom: 1.2rem;
  position: relative;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
}
.stat-num {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.stat-label {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  letter-spacing: 0.05em;
}
.stat-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
}
.bio {
  color: var(--color-text-secondary);
  max-width: 440px;
  margin: 0 auto 1rem;
  font-size: 0.95rem;
  line-height: 1.6;
  position: relative;
}
.profile-meta {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  position: relative;
}
.github-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.3rem 0.8rem;
  background: var(--color-bg-secondary);
  border-radius: 999px;
  transition: all 0.2s ease;
}
.github-link:hover {
  color: var(--color-text);
  background: var(--color-border-light);
}
.join-date {
  color: var(--color-text-muted);
  font-size: 0.82rem;
}
.btn-message {
  margin-top: 0.5rem;
  padding: 0.6rem 1.8rem;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}
.btn-message:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.user-topics h2 {
  margin-bottom: 1.2rem;
  color: var(--color-text);
  font-size: 1.3rem;
  font-weight: 600;
}

.card {
  position: relative;
  padding: 1.2rem 1.4rem;
  margin-bottom: 0.6rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
}
.card:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
.card-link {
  position: absolute;
  inset: 0;
  z-index: 1;
}
.title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.4rem 0;
  letter-spacing: -0.01em;
  transition: color 0.2s ease;
}
.card:hover .title { color: var(--color-primary); }
.meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}
.meta-dot { opacity: 0.5; }
.meta-stat { font-variant-numeric: tabular-nums; }
</style>
