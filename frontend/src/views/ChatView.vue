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
      <button class="btn-back" @click="router.push('/messages')">← 返回</button>
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
        <div v-if="messages.length === 0" class="empty-hint">暂无消息，发送第一条吧</div>
      </div>

      <div class="input-area">
        <textarea
          v-model="newMessage"
          placeholder="输入消息..."
          rows="2"
          @keydown="onKeydown"
        ></textarea>
        <button class="btn-send" :disabled="sending || !newMessage.trim()" @click="handleSend">
          {{ sending ? "发送中..." : "发送" }}
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.chat-page {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
}
.chat-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1rem;
}
.btn-back {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 0.95rem;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-border);
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
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-muted);
}
.username {
  font-weight: 600;
  color: var(--color-text);
}
.state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-muted);
}
.state.error { color: var(--color-danger); }
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
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
  padding: 0.6rem 1rem;
  border-radius: 12px;
  font-size: 0.95rem;
  line-height: 1.5;
  word-break: break-word;
}
.message.mine .bubble {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.message:not(.mine) .bubble {
  background: var(--color-bg-secondary);
  color: var(--color-text);
  border-bottom-left-radius: 4px;
}
.time {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-top: 0.2rem;
}
.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem;
}
.input-area {
  display: flex;
  gap: 0.8rem;
  padding: 1rem 0;
  border-top: 1px solid var(--color-border);
}
.input-area textarea {
  flex: 1;
  padding: 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  resize: none;
  font-family: inherit;
  font-size: 0.95rem;
  background: var(--color-bg);
  color: var(--color-text);
}
.input-area textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}
.btn-send {
  padding: 0.6rem 1.5rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.95rem;
}
.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
