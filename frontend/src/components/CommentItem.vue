<script setup>
import { ref } from "vue";
import { showConfirm } from "../composables/confirm";
import { showToast } from "../composables/toast";
import { deleteComment } from "../api/comment";

const props = defineProps({
  comment: { type: Object, required: true },
  depth: { type: Number, default: 0 },
  auth: { type: Object, default: null },
});

const emit = defineEmits(["reply-created", "comment-deleted"]);

const showReplyForm = ref(false);
const replyText = ref("");

function handleSubmit() {
  if (!replyText.value.trim()) return;
  emit("reply-created", {
    parentId: props.comment.id,
    content: replyText.value,
  });
  replyText.value = "";
  showReplyForm.value = false;
}

function canDelete() {
  if (!props.auth) return false;
  return props.auth.id === props.comment.user_id || props.auth.is_admin;
}

async function handleDelete() {
  const ok = await showConfirm("确定删除这条评论吗？");
  if (!ok) return;
  try {
    await deleteComment(props.comment.id);
    showToast.success("评论已删除");
    emit("comment-deleted", props.comment.id);
  } catch (e) {
    showToast.error(e.response?.data?.detail || "删除失败");
  }
}

function initials(name) {
  if (!name) return "?";
  return name.charAt(0).toUpperCase();
}
</script>

<template>
  <div class="comment-thread" :class="{ nested: depth > 0 }">
    <div class="comment-item">
      <div class="comment-avatar">{{ initials(comment.username) }}</div>
      <div class="comment-main">
        <div class="comment-header">
          <router-link :to="`/user/${comment.username}`" class="comment-author">{{ comment.username }}</router-link>
          <span class="comment-dot">·</span>
          <span class="comment-time">{{ new Date(comment.created_at).toLocaleDateString() }}</span>
        </div>
        <p class="comment-body">{{ comment.content }}</p>
        <div class="comment-actions">
          <button v-if="auth" class="btn-link" @click="showReplyForm = !showReplyForm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 17 4 12 9 7"/><path d="M20 18v-2a4 4 0 0 0-4-4H4"/></svg>
            回复
          </button>
          <button v-if="canDelete()" class="btn-link btn-danger" @click="handleDelete">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"/></svg>
            删除
          </button>
        </div>

        <div v-if="showReplyForm" class="reply-form">
          <textarea
            v-model="replyText"
            placeholder="写下你的回复..."
            rows="2"
          ></textarea>
          <div class="reply-actions">
            <button class="btn-submit" @click="handleSubmit">提交</button>
            <button class="btn-cancel" @click="showReplyForm = false">取消</button>
          </div>
        </div>
      </div>
    </div>

    <template v-if="depth < 10">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :depth="depth + 1"
        :auth="auth"
        @reply-created="emit('reply-created', $event)"
        @comment-deleted="emit('comment-deleted', $event)"
      />
    </template>
  </div>
</template>

<style scoped>
.comment-thread.nested {
  margin-left: 44px;
  border-left: 1px solid var(--color-border-light);
  padding-left: 16px;
}
.comment-item {
  display: flex;
  gap: 0.85rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--color-border-light);
}
.comment-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  font-family: var(--font-display);
}
.comment-main {
  flex: 1;
  min-width: 0;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  margin-bottom: 0.35rem;
}
.comment-author {
  color: var(--color-text);
  text-decoration: none;
  font-weight: 600;
}
.comment-author:hover { color: var(--color-primary); }
.comment-dot { color: var(--color-text-muted); }
.comment-time {
  color: var(--color-text-muted);
  font-size: 0.8rem;
  font-family: var(--font-mono);
}
.comment-body {
  margin: 0 0 0.4rem;
  font-size: 0.95rem;
  line-height: 1.65;
  color: var(--color-text-secondary);
}

.comment-actions {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.4rem;
}
.btn-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.3rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: color 0.2s, background 0.2s;
}
.btn-link:hover {
  color: var(--color-primary);
  background: var(--color-primary-soft);
}
.btn-link.btn-danger:hover {
  color: var(--color-danger);
  background: var(--color-bg-elevated);
}

.reply-form {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}
.reply-form textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  resize: vertical;
  font-size: 0.9rem;
  font-family: inherit;
  box-sizing: border-box;
  background: var(--color-bg);
  color: var(--color-text);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.reply-form textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}
.reply-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: flex-end;
}
.btn-submit {
  padding: 0.4rem 1.1rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: opacity 0.2s;
}
.btn-submit:hover { opacity: 0.9; }
.btn-cancel {
  padding: 0.4rem 1.1rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  transition: border-color 0.2s, color 0.2s;
}
.btn-cancel:hover {
  border-color: var(--color-text);
  color: var(--color-text);
}
</style>
