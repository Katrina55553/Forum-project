<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getMessages, sendMessage, markMessagesRead } from "../api/message";
import { useAuthStore } from "../stores/auth";
import { showToast } from "../composables/toast";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const messages = ref([]);
const otherUser = ref(null);
const loading = ref(true);
const error = ref("");
const newMessage = ref("");
const sending = ref(false);
const messagesContainer = ref(null);

let pollTimer = null;

async function fetchMessages() {
  try {
    const res = await getMessages(route.params.username);
    messages.value = res.data.messages;
    otherUser.value = res.data.other_user;
    await nextTick();
    scrollToBottom();
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = "用户不存在";
    } else {
      error.value = "加载失败";
    }
  } finally {
    loading.value = false;
  }
}

async function handleSend() {
  const content = newMessage.value.trim();
  if (!content || sending.value) return;

  sending.value = true;
  try {
    await sendMessage(route.params.username, content);
    newMessage.value = "";
    await fetchMessages();
  } catch (e) {
    showToast.error(e.response?.data?.detail || "发送失败");
  } finally {
    sending.value = false;
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function formatTime(t) {
  if (!t) return "";
  const date = new Date(t);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  const time = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (isToday) return time;
  return `${date.toLocaleDateString()} ${time}`;
}

function onKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    handleSend();
  }
}

onMounted(() => {
  fetchMessages();
  // 每 10 秒轮询新消息
  pollTimer = setInterval(fetchMessages, 10000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});
</script>

<template>
  <div class="chat-page">
    <div class="chat-header">
      <button class="btn-back" @click="router.push('/messages')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        返回
      </button>
      <div v-if="otherUser" class="user-info">
        <div class="avatar">
          <img v-if="otherUser.avatar" :src="otherUser.avatar" :alt="otherUser.username" />
          <span v-else class="avatar-initial">{{ otherUser.username[0]?.toUpperCase() }}</span>
        </div>
        <span class="username">{{ otherUser.username }}</span>
      </div>
    </div>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchMessages">重试</button>
    </div>

    <template v-else>
      <div class="messages" ref="messagesContainer">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message"
          :class="{ mine: msg.sender_id === auth.user?.id }"
        >
          <div class="bubble">{{ msg.content }}</div>
          <div class="time">{{ formatTime(msg.created_at) }}</div>
        </div>
        <div v-if="messages.length === 0" class="empty-hint">
          <div class="empty-mark">✦</div>
          <p>暂无消息，发送第一条吧</p>
        </div>
      </div>

      <div class="input-area">
        <textarea
          v-model="newMessage"
          placeholder="输入消息..."
          rows="2"
          @keydown="onKeydown"
        ></textarea>
        <button class="btn-send" :disabled="sending || !newMessage.trim()" @click="handleSend">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          {{ sending ? "发送中..." : "发送" }}
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.chat-page {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 130px);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.chat-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.4rem;
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-elevated);
}
.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 0.4rem 0.6rem;
  border-radius: var(--radius);
  transition: all 0.2s ease;
}
.btn-back:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
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
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
}
.username {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.98rem;
}
.state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-muted);
}
.state.error { color: var(--color-danger); }
.btn-retry {
  margin-top: 0.8rem;
  padding: 0.5rem 1.4rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.88rem;
  transition: all 0.2s ease;
}
.btn-retry:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  background: var(--color-bg);
}
.message {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}
.message.mine {
  align-self: flex-end;
  align-items: flex-end;
}
.message:not(.mine) {
  align-self: flex-start;
  align-items: flex-start;
}
.bubble {
  padding: 0.7rem 1.1rem;
  border-radius: var(--radius-lg);
  font-size: 0.95rem;
  line-height: 1.5;
  word-break: break-word;
}
.message.mine .bubble {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: var(--radius-sm);
}
.message:not(.mine) .bubble {
  background: var(--color-bg-elevated);
  color: var(--color-text);
  border: 1px solid var(--color-border-light);
  border-bottom-left-radius: var(--radius-sm);
}
.time {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-top: 0.3rem;
  font-variant-numeric: tabular-nums;
}
.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: 3rem 1rem;
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.empty-mark {
  font-size: 2rem;
  color: var(--color-primary);
  opacity: 0.5;
}
.input-area {
  display: flex;
  gap: 0.7rem;
  padding: 1rem 1.4rem;
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-elevated);
}
.input-area textarea {
  flex: 1;
  padding: 0.7rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  resize: none;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  line-height: 1.5;
}
.input-area textarea::placeholder { color: var(--color-text-muted); }
.input-area textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}
.btn-send {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.7rem 1.4rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}
.btn-send:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
