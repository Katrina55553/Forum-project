<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getConversations } from "../api/message";

const router = useRouter();
const conversations = ref([]);
const loading = ref(true);
const error = ref("");

async function fetchConversations() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getConversations();
    conversations.value = res.data;
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

function openChat(username) {
  router.push(`/messages/${username}`);
}

onMounted(fetchConversations);
</script>

<template>
  <div class="messages-page">
    <h1>私信</h1>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button @click="fetchConversations">重试</button>
    </div>
    <div v-else-if="conversations.length === 0" class="state empty">
      <p>暂无私信</p>
      <p class="hint">访问其他用户主页，点击"发私信"开始聊天</p>
    </div>

    <div v-else class="conversation-list">
      <div
        v-for="c in conversations"
        :key="c.username"
        class="conversation-item"
        :class="{ unread: c.unread_count > 0 }"
        @click="openChat(c.username)"
      >
        <div class="avatar">
          <img v-if="c.avatar" :src="c.avatar" :alt="c.username" />
          <span v-else class="avatar-initial">{{ c.username[0]?.toUpperCase() }}</span>
        </div>
        <div class="info">
          <div class="header">
            <span class="username">{{ c.username }}</span>
            <span class="time">{{ formatTime(c.last_message_at) }}</span>
          </div>
          <div class="preview">{{ c.last_message }}</div>
        </div>
        <div v-if="c.unread_count > 0" class="badge">{{ c.unread_count }}</div>
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
.hint {
  font-size: 0.85rem;
  margin-top: 0.5rem;
}
.conversation-list {
  display: flex;
  flex-direction: column;
}
.conversation-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background 0.2s;
}
.conversation-item:hover {
  background: var(--color-bg-secondary);
}
.conversation-item.unread {
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
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}
</style>
