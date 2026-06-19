<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { marked } from "marked";
import DOMPurify from "dompurify";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";
import { getTopicById, deleteTopic, pinTopic, featureTopic } from "../api/topic";
import { createComment } from "../api/comment";
import { likeTopic, unlikeTopic } from "../api/like";
import { useAuthStore } from "../stores/auth";
import CommentItem from "../components/CommentItem.vue";
import { showConfirm } from "../composables/confirm";
import { showToast } from "../composables/toast";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const topic = ref(null);
const loading = ref(true);
const error = ref("");

const commentText = ref("");
const commentLoading = ref(false);
const commentError = ref("");

const likeLoading = ref(false);

function isLiked() {
  return topic.value?.is_liked || false;
}

async function handleLike() {
  if (!auth.user) {
    router.push("/login");
    return;
  }
  likeLoading.value = true;
  try {
    if (isLiked()) {
      const res = await unlikeTopic(topic.value.id);
      topic.value.likes_count = res.data.likes_count;
      topic.value.is_liked = false;
    } else {
      const res = await likeTopic(topic.value.id);
      topic.value.likes_count = res.data.likes_count;
      topic.value.is_liked = true;
    }
  } catch {
    // ignore duplicate
  } finally {
    likeLoading.value = false;
  }
}

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
});

const isAuthor = computed(() =>
  auth.user && topic.value && auth.user.id === topic.value.author?.id,
);

const isAdmin = computed(() => auth.user?.is_admin);

const renderedContent = computed(() => {
  if (!topic.value?.content) return "";
  return DOMPurify.sanitize(marked(topic.value.content));
});

function handleEdit() {
  router.push(`/topic/${topic.value.id}/edit`);
}

async function handleDelete() {
  if (!await showConfirm("确定删除这个帖子？")) return;
  try {
    await deleteTopic(topic.value.id);
    router.push("/");
    showToast.success("删除成功");
  } catch {
    showToast.error("删除失败");
  }
}

async function handlePin() {
  try {
    const res = await pinTopic(topic.value.id);
    topic.value.is_pinned = res.data.is_pinned;
    showToast.success(res.data.is_pinned ? "已置顶" : "已取消置顶");
  } catch {
    showToast.error("操作失败");
  }
}

async function handleFeature() {
  try {
    const res = await featureTopic(topic.value.id);
    topic.value.is_featured = res.data.is_featured;
    showToast.success(res.data.is_featured ? "已设为精华" : "已取消精华");
  } catch {
    showToast.error("操作失败");
  }
}

async function fetchTopic() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getTopicById(route.params.id);
    topic.value = res.data;
  } catch {
    error.value = "帖子不存在或加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleComment(parentId = null, content = null) {
  const text = content || commentText.value;
  if (!text.trim()) return;
  commentLoading.value = true;
  commentError.value = "";
  try {
    await createComment(topic.value.id, text, parentId);
    if (!parentId) commentText.value = "";
    await fetchTopic();
  } catch (e) {
    commentError.value = e.response?.data?.detail || "评论失败";
  } finally {
    commentLoading.value = false;
  }
}

function handleReplyCreated({ parentId, content }) {
  handleComment(parentId, content);
}

async function handleCommentDeleted() {
  await fetchTopic();
}

onMounted(fetchTopic);
</script>

<template>
  <div class="topic-detail">
    <div v-if="loading" class="skeleton-detail">
      <div class="skeleton-line w-70 h-32"></div>
      <div class="skeleton-line w-40 h-14"></div>
      <div class="skeleton-line w-100 h-14"></div>
      <div class="skeleton-line w-100 h-14"></div>
      <div class="skeleton-line w-80 h-14"></div>
    </div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchTopic">重试</button>
    </div>

    <article v-else>
      <div class="title-section">
        <div v-if="topic.is_pinned || topic.is_featured" class="badges">
          <span v-if="topic.is_pinned" class="badge pin">置顶</span>
          <span v-if="topic.is_featured" class="badge featured">精华</span>
        </div>
        <h1>{{ topic.title }}</h1>
      </div>
      <div v-if="topic.tags?.length" class="topic-tags">
        <router-link
          v-for="tag in topic.tags"
          :key="tag.id"
          :to="{ name: 'home', query: { tag: tag.slug } }"
          class="topic-tag"
        >
          #{{ tag.name }}
        </router-link>
      </div>
      <div class="meta">
        <router-link :to="`/user/${topic.author?.username}`" class="author">
          <span class="author-avatar">{{ topic.author?.username?.[0]?.toUpperCase() }}</span>
          {{ topic.author?.username }}
        </router-link>
        <span class="meta-dot">·</span>
        <span>{{ new Date(topic.created_at).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
        <span class="meta-dot">·</span>
        <span class="meta-stat">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          {{ topic.view_count || 0 }}
        </span>
        <button
          class="like-btn"
          :class="{ liked: isLiked() }"
          :disabled="likeLoading"
          @click="handleLike"
        >
          <svg v-if="isLiked()" width="15" height="15" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          {{ topic.likes_count || 0 }}
        </button>
      </div>
      <div v-if="isAuthor || isAdmin" class="author-actions">
        <button class="btn-action btn-edit" @click="handleEdit">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          编辑
        </button>
        <button class="btn-action btn-delete" @click="handleDelete">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          删除
        </button>
        <template v-if="isAdmin">
          <button class="btn-action btn-pin" :class="{ active: topic.is_pinned }" @click="handlePin">
            {{ topic.is_pinned ? '取消置顶' : '置顶' }}
          </button>
          <button class="btn-action btn-feature" :class="{ active: topic.is_featured }" @click="handleFeature">
            {{ topic.is_featured ? '取消精华' : '精华' }}
          </button>
        </template>
      </div>
      <div class="content" v-html="renderedContent"></div>

      <section class="comments">
        <h3>
          <span>回复</span>
          <span class="comments-count">{{ topic.comments?.length || 0 }}</span>
        </h3>

        <div v-if="auth.user" class="comment-form">
          <div class="comment-avatar">
            <img v-if="auth.user.avatar" :src="auth.user.avatar" />
            <span v-else>{{ auth.user.username?.[0]?.toUpperCase() }}</span>
          </div>
          <div class="comment-form-body">
            <textarea
              v-model="commentText"
              placeholder="写下你的回复..."
              rows="3"
            ></textarea>
            <div class="comment-actions">
              <button :disabled="commentLoading || !commentText.trim()" @click="handleComment()">
                {{ commentLoading ? "提交中..." : "发表回复" }}
              </button>
              <span v-if="commentError" class="error">{{ commentError }}</span>
            </div>
          </div>
        </div>
        <p v-else class="login-hint">
          <router-link to="/login">登录</router-link> 后发表回复
        </p>

        <div v-if="topic.comments?.length" class="comment-list">
          <CommentItem
            v-for="c in topic.comments"
            :key="c.id"
            :comment="c"
            :auth="auth.user"
            @reply-created="handleReplyCreated"
            @comment-deleted="handleCommentDeleted"
          />
        </div>
        <p v-else class="state">还没有回复，来说点什么吧。</p>
      </section>
    </article>
  </div>
</template>

<style scoped>
.topic-detail { max-width: 720px; margin: 0 auto; }
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

.skeleton-detail {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.skeleton-line {
  background: linear-gradient(90deg, var(--color-border-light) 0%, var(--color-border) 50%, var(--color-border-light) 100%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: shimmer 1.6s infinite linear;
}
.skeleton-line.w-70 { width: 70%; }
.skeleton-line.w-40 { width: 40%; }
.skeleton-line.w-80 { width: 80%; }
.skeleton-line.w-100 { width: 100%; }
.skeleton-line.h-32 { height: 32px; }
.skeleton-line.h-14 { height: 14px; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.title-section {
  margin-bottom: 1rem;
}
.title-section .badges {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
}
.badge {
  padding: 0.2rem 0.65rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.02em;
}
.badge.pin {
  background: var(--color-primary);
  color: #fff;
}
.badge.featured {
  background: var(--color-warning);
  color: #fff;
}
h1 {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: var(--color-text);
  line-height: 1.2;
  letter-spacing: -0.025em;
}

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.2rem;
}
.topic-tag {
  padding: 0.2rem 0;
  background: none;
  border: none;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.2s ease;
}
.topic-tag:hover {
  color: var(--color-primary);
}

.meta {
  display: flex;
  gap: 0.6rem;
  color: var(--color-text-muted);
  font-size: 0.88rem;
  margin-bottom: 1.8rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
  flex-wrap: wrap;
  align-items: center;
}
.author {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}
.author:hover { color: var(--color-primary); }
.author-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
}
.meta-dot { opacity: 0.5; }
.meta-stat {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.like-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0.35rem 0.9rem;
  cursor: pointer;
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  transition: all 0.2s ease;
}
.like-btn:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}
.like-btn.liked {
  border-color: var(--color-danger);
  background: var(--color-danger-bg);
  color: var(--color-danger);
}
.like-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.author-actions {
  margin-bottom: 2rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  transition: all 0.2s ease;
}
.btn-action:hover {
  border-color: var(--color-text);
  color: var(--color-text);
}
.btn-edit:hover { border-color: var(--color-primary); color: var(--color-primary); }
.btn-delete { color: var(--color-danger); }
.btn-delete:hover { background: var(--color-danger-bg); border-color: var(--color-danger); }
.btn-pin.active { border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-soft); }
.btn-feature.active { border-color: var(--color-warning); color: var(--color-warning); background: rgba(184, 134, 11, 0.1); }

.content {
  line-height: 1.85;
  font-size: 1.05rem;
  color: var(--color-text);
  font-family: var(--font-sans);
}
.content :deep(h1),
.content :deep(h2),
.content :deep(h3) {
  font-family: var(--font-display);
  margin-top: 1.8em;
  margin-bottom: 0.6em;
  letter-spacing: -0.02em;
}
.content :deep(p) { margin: 1em 0; }
.content :deep(pre) {
  background: var(--color-pre-bg);
  padding: 1.2rem 1.4rem;
  border-radius: var(--radius-lg);
  overflow-x: auto;
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 1.5em 0;
}
.content :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.88rem;
}
.content :deep(p > code) {
  background: var(--color-code-bg);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  color: var(--color-primary);
}
.content :deep(blockquote) {
  border-left: 3px solid var(--color-primary);
  margin: 1.5em 0;
  padding: 0.5em 1.2em;
  color: var(--color-text-secondary);
  font-style: italic;
  background: var(--color-bg-secondary);
  border-radius: 0 var(--radius) var(--radius) 0;
}
.content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-lg);
  margin: 1.5em 0;
}
.content :deep(ul),
.content :deep(ol) { padding-left: 1.5em; margin: 1em 0; }
.content :deep(li) { margin: 0.4em 0; }
.content :deep(a) {
  color: var(--color-primary);
  text-decoration: underline;
  text-decoration-color: var(--color-primary-soft);
  text-underline-offset: 3px;
  transition: text-decoration-color 0.2s ease;
}
.content :deep(a:hover) { text-decoration-color: var(--color-primary); }
.content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1.5em 0;
  font-size: 0.95rem;
}
.content :deep(th),
.content :deep(td) {
  border: 1px solid var(--color-border);
  padding: 0.6em 0.9em;
  text-align: left;
}
.content :deep(th) {
  background: var(--color-bg-secondary);
  font-weight: 600;
}
.content :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: 2em 0;
}

.comments {
  margin-top: 3.5rem;
  border-top: 1px solid var(--color-border-light);
  padding-top: 2rem;
}
.comments h3 {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.5rem;
  color: var(--color-text);
  font-size: 1.3rem;
}
.comments-count {
  font-family: var(--font-sans);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--color-bg-secondary);
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  font-variant-numeric: tabular-nums;
}
.login-hint {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  padding: 1.2rem;
  text-align: center;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.comment-form {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 2rem;
  align-items: flex-start;
}
.comment-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.95rem;
  overflow: hidden;
  flex-shrink: 0;
}
.comment-avatar img { width: 100%; height: 100%; object-fit: cover; }
.comment-form-body { flex: 1; min-width: 0; }
.comment-form textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  resize: vertical;
  font-size: 0.95rem;
  box-sizing: border-box;
  background: var(--color-bg-elevated);
  color: var(--color-text);
  font-family: var(--font-sans);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  min-height: 80px;
}
.comment-form textarea::placeholder { color: var(--color-text-muted); }
.comment-form textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}
.comment-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.6rem;
}
.comment-actions button {
  padding: 0.55rem 1.4rem;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.comment-actions button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.comment-actions button:disabled { opacity: 0.5; cursor: not-allowed; }
.comment-list { margin-top: 1rem; }
</style>
