<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getConversations } from "../api/message";
import { getNotifications, markRead } from "../api/notification";

const router = useRouter();
const messages = ref([]);
const loading = ref(true);
const error = ref("");

async function fetchMessages() {
  loading.value = true;
  error.value = "";
  try {
    // 同时获取通知和私信
    const [notifRes, convRes] = await Promise.all([
      getNotifications(1, 50),
      getConversations(),
    ]);

    const notifications = (notifRes.data.items || []).map(n => ({
      type: "notification",
      id: `notif-${n.id}`,
      sourceId: n.id,
      username: "系统通知",
      avatar: "",
      preview: n.type === "reply" ? "有人回复了你的帖子" : "你有新通知",
      time: n.created_at,
      unread: !n.is_read,
      topicId: n.topic_id,
    }));

    const conversations = (convRes.data || []).map(c => ({
      type: "message",
      id: `msg-${c.username}`,
      username: c.username,
      avatar: c.avatar,
      preview: c.last_message,
      time: c.last_message_at,
      unread: c.unread_count > 0,
      unreadCount: c.unread_count,
    }));

    // 合并并按时间排序
    messages.value = [...notifications, ...conversations]
      .sort((a, b) => new Date(b.time) - new Date(a.time));
  } catch {
    error.value = "加载失败";
  } finally {
    loading.value = false;
  }
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

async function openMessage(msg) {
  if (msg.type === "notification") {
    // 标记通知已读
    if (msg.unread) {
      try { await markRead(msg.sourceId); } catch {}
    }
    if (msg.topicId) {
      router.push(`/topic/${msg.topicId}`);
    }
  } else {
    router.push(`/messages/${msg.username}`);
  }
}

onMounted(fetchMessages);
</script>

<template>
  <div class="messages-page">
    <header class="page-header">
      <p class="page-eyebrow">消息 · MESSAGES</p>
      <h1>消息</h1>
    </header>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchMessages">重试</button>
    </div>
    <div v-else-if="messages.length === 0" class="state empty">
      <div class="empty-mark">✦</div>
      <p>暂无消息</p>
    </div>

    <div v-else class="message-list">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message-item"
        :class="{ unread: msg.unread }"
        @click="openMessage(msg)"
      >
        <div class="avatar" :class="{ system: msg.type === 'notification' }">
          <img v-if="msg.avatar" :src="msg.avatar" :alt="msg.username" />
          <span v-else class="avatar-initial">{{ msg.type === 'notification' ? '✦' : msg.username[0]?.toUpperCase() }}</span>
        </div>
        <div class="info">
          <div class="header">
            <span class="username" :class="{ system: msg.type === 'notification' }">{{ msg.username }}</span>
            <span class="time">{{ formatTime(msg.time) }}</span>
          </div>
          <div class="preview">{{ msg.preview }}</div>
        </div>
        <div v-if="msg.unread" class="badge">
          {{ msg.type === 'message' && msg.unreadCount ? msg.unreadCount : '' }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.messages-page {
  max-width: 640px;
  margin: 0 auto;
}
.page-header {
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
h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 2.2rem);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
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
.state.error { color: var(--color-danger); }
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
.message-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.message-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.2rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}
.message-item:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
.message-item.unread {
  background: var(--color-primary-soft);
  border-color: var(--color-primary-soft);
}
.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-bg-secondary);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar.system {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  color: #fff;
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-initial {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-muted);
}
.avatar.system .avatar-initial {
  color: #fff;
}
.info {
  flex: 1;
  min-width: 0;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
  gap: 0.6rem;
}
.username {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.95rem;
}
.username.system {
  color: var(--color-primary);
}
.time {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.preview {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.badge {
  background: var(--color-primary);
  color: #fff;
  min-width: 22px;
  height: 22px;
  padding: 0 0.55rem;
  border-radius: 11px;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
</style>
