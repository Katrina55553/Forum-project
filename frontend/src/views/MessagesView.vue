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
    <h1>消息</h1>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button @click="fetchMessages">重试</button>
    </div>
    <div v-else-if="messages.length === 0" class="state empty">
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
          <span v-else class="avatar-initial">{{ msg.type === 'notification' ? '🔔' : msg.username[0]?.toUpperCase() }}</span>
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
  max-width: 600px;
  margin: 0 auto;
}
h1 {
  margin-bottom: 1.5rem;
  color: var(--color-text);
}
.state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-muted);
}
.state.error { color: var(--color-danger); }
.state button {
  margin-top: 0.5rem;
  padding: 0.4rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
}
.message-list {
  display: flex;
  flex-direction: column;
}
.message-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background 0.2s;
}
.message-item:hover {
  background: var(--color-bg-secondary);
}
.message-item.unread {
  background: var(--color-bg-secondary);
}
.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-border);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar.system {
  background: var(--color-primary);
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-initial {
  font-size: 1.2rem;
  font-weight: 600;
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
}
.username {
  font-weight: 600;
  color: var(--color-text);
}
.username.system {
  color: var(--color-primary);
}
.time {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.preview {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.badge {
  background: var(--color-primary);
  color: #fff;
  min-width: 20px;
  height: 20px;
  padding: 0 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
