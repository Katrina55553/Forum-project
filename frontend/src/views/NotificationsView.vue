<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getNotifications, markRead, markAllRead } from "../api/notification";

const router = useRouter();

const items = ref([]);
const total = ref(0);
const pages = ref(0);
const page = ref(1);
const loading = ref(true);
const error = ref("");
const size = 20;

async function fetchNotifications() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getNotifications(page.value, size);
    items.value = res.data.items;
    total.value = res.data.total;
    pages.value = res.data.pages;
  } catch {
    error.value = "加载失败";
  } finally {
    loading.value = false;
  }
}

async function goTopic(notif) {
  if (!notif.is_read) {
    await markRead(notif.id);
    notif.is_read = true;
  }
  if (notif.topic_id) {
    router.push(`/topic/${notif.topic_id}`);
  }
}

async function handleMarkAll() {
  await markAllRead();
  items.value.forEach((n) => (n.is_read = true));
}

function goPage(p) {
  page.value = p;
}

function formatTime(t) {
  if (!t) return "";
  const diff = Date.now() - new Date(t).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins}分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}小时前`;
  return new Date(t).toLocaleDateString();
}

onMounted(fetchNotifications);
</script>

<template>
  <div class="notifications">
    <div class="notif-header">
      <div>
        <p class="page-eyebrow">通知 · INBOX</p>
        <h1>通知</h1>
      </div>
      <button v-if="items.some((n) => !n.is_read)" class="btn-mark-all" @click="handleMarkAll">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        全部已读
      </button>
    </div>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchNotifications">重试</button>
    </div>
    <div v-else-if="items.length === 0" class="state empty">
      <div class="empty-mark">✦</div>
      <p>暂无通知</p>
    </div>

    <div v-else class="notif-list">
      <div
        v-for="n in items"
        :key="n.id"
        class="notif-item"
        :class="{ unread: !n.is_read }"
        @click="goTopic(n)"
      >
        <div class="notif-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <div class="notif-body">
          <span class="notif-text">有人回复了你的帖子</span>
          <span class="notif-time">{{ formatTime(n.created_at) }}</span>
        </div>
        <span v-if="!n.is_read" class="unread-dot"></span>
      </div>

      <div v-if="pages > 1" class="pagination">
        <button :disabled="page <= 1" @click="goPage(page - 1)" class="page-nav">上一页</button>
        <span v-for="p in pages" :key="p" class="page-num-wrap">
          <button :class="{ current: p === page }" @click="goPage(p)" class="page-num">{{ p }}</button>
        </span>
        <button :disabled="page >= pages" @click="goPage(pages)" class="page-nav">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications { max-width: 720px; margin: 0 auto; }
.notif-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
}
.page-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin: 0 0 0.3rem;
  font-weight: 500;
}
.notif-header h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 2.2rem);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}
.btn-mark-all {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.1rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
}
.btn-mark-all:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--color-text-muted);
}
.state.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.empty-mark {
  font-size: 2.5rem;
  color: var(--color-primary);
  opacity: 0.5;
}
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

.notif-list { display: flex; flex-direction: column; gap: 0.4rem; }
.notif-item {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 1.2rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}
.notif-item:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
.notif-item.unread {
  background: var(--color-primary-soft);
  border-color: var(--color-primary-soft);
}
.notif-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notif-item.unread .notif-icon {
  background: var(--color-primary);
  color: #fff;
}
.notif-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}
.notif-text {
  font-size: 0.92rem;
  color: var(--color-text);
  font-weight: 500;
}
.notif-time {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  flex-shrink: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.4rem;
  margin-top: 2.5rem;
}
.page-num-wrap { display: inline-flex; }
.page-num {
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  background: none;
  color: var(--color-text-secondary);
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}
.page-num:hover { background: var(--color-bg-secondary); color: var(--color-text); }
.page-num.current {
  background: var(--color-text);
  color: var(--color-bg);
  font-weight: 600;
}
.page-nav {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}
.page-nav:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.page-nav:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
