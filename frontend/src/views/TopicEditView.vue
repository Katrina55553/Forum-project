<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { createTopic, updateTopic, getTopicById, getTopicForEdit } from "../api/topic";
import { getTags } from "../api/tag";
import { showToast } from "../composables/toast";
import TagInput from "../components/TagInput.vue";

const route = useRoute();
const router = useRouter();

const isEdit = computed(() => !!route.params.id);
const title = ref("");
const content = ref("");
const tags = ref([]);
const allTags = ref([]);
const loading = ref(false);
const pageLoading = ref(false);
const error = ref("");

const previewHtml = computed(() => {
  if (!content.value) return "<em>暂无内容</em>";
  return DOMPurify.sanitize(marked(content.value));
});

async function init() {
  // 获取热门标签
  try {
    const tagsRes = await getTags();
    allTags.value = tagsRes.data;
  } catch {
    // ignore
  }

  if (isEdit.value) {
    pageLoading.value = true;
    try {
      const res = await getTopicForEdit(route.params.id);
      title.value = res.data.title;
      content.value = res.data.content;
      tags.value = res.data.tags?.map(t => t.name) || [];
    } catch {
      error.value = "加载失败";
    } finally {
      pageLoading.value = false;
    }
  }
}

async function handleSubmit() {
  if (!title.value.trim()) {
    error.value = "标题不能为空";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    const data = {
      title: title.value.trim(),
      content: content.value,
      tags: tags.value,
    };
    if (isEdit.value) {
      const res = await updateTopic(route.params.id, data);
      router.push(`/topic/${res.data.id}`);
      showToast.success("更新成功");
    } else {
      const res = await createTopic(data);
      router.push(`/topic/${res.data.id}`);
      showToast.success("发帖成功");
    }
  } catch (e) {
    error.value = e.response?.data?.detail || "操作失败";
  } finally {
    loading.value = false;
  }
}

// 路由参数变化时重新加载（同组件复用场景）
watch(() => route.params.id, (newId) => {
  if (newId) init();
});

onMounted(init);
</script>

<template>
  <div class="topic-edit">
    <header class="edit-header">
      <p class="edit-eyebrow">{{ isEdit ? "编辑" : "新建" }} · DRAFT</p>
      <h1>{{ isEdit ? "编辑帖子" : "发布新帖" }}</h1>
    </header>

    <div v-if="pageLoading" class="skeleton-form">
      <div class="skeleton-line w-100 h-40"></div>
      <div class="skeleton-line w-100 h-200"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="edit-form">
      <div class="field">
        <label for="title">标题</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="一个引人入胜的标题..."
          maxlength="200"
        />
      </div>

      <div class="field">
        <label>标签</label>
        <TagInput v-model="tags" :suggestions="allTags" />
      </div>

      <div class="field">
        <label for="content">内容 <span class="hint">支持 Markdown</span></label>
        <div class="editor-wrap">
          <div class="editor-pane">
            <div class="pane-label">撰写</div>
            <textarea
              id="content"
              v-model="content"
              placeholder="开始你的故事..."
              rows="18"
            ></textarea>
          </div>
          <div class="preview-pane">
            <div class="pane-label">预览</div>
            <div class="preview" v-html="previewHtml"></div>
          </div>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="actions">
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? "提交中..." : (isEdit ? "更新" : "发布") }}
        </button>
        <button type="button" class="btn-cancel" @click="router.back()">取消</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.topic-edit { max-width: 900px; margin: 0 auto; }

.edit-header { margin-bottom: 2rem; }
.edit-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin: 0 0 0.4rem;
  font-weight: 500;
}
h1 {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.skeleton-form { display: flex; flex-direction: column; gap: 1rem; }
.skeleton-line {
  background: linear-gradient(90deg, var(--color-border-light) 0%, var(--color-border) 50%, var(--color-border-light) 100%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: shimmer 1.6s infinite linear;
}
.skeleton-line.w-100 { width: 100%; }
.skeleton-line.h-40 { height: 40px; }
.skeleton-line.h-200 { height: 200px; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.field { margin-bottom: 1.5rem; }
.field label {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.92rem;
}
.hint {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 400;
  color: var(--color-text-muted);
  letter-spacing: 0.05em;
}
.field input {
  width: 100%;
  padding: 0.85rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 1rem;
  box-sizing: border-box;
  background: var(--color-bg-elevated);
  color: var(--color-text);
  font-family: var(--font-sans);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.field input::placeholder { color: var(--color-text-muted); }
.field input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}

.editor-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.editor-wrap:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}
.editor-pane, .preview-pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.pane-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
  font-weight: 500;
}
.editor-wrap textarea {
  flex: 1;
  min-height: 420px;
  padding: 0.5rem 0;
  border: none;
  font-size: 0.95rem;
  line-height: 1.7;
  background: transparent;
  color: var(--color-text);
  resize: vertical;
  font-family: var(--font-mono);
  outline: none;
}
.preview {
  flex: 1;
  min-height: 420px;
  overflow-y: auto;
  padding: 0.5rem 0;
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--color-text);
}
.preview :deep(h1),
.preview :deep(h2),
.preview :deep(h3) {
  font-family: var(--font-display);
  margin: 1em 0 0.5em;
}
.preview :deep(p) { margin: 0.8em 0; }
.preview :deep(pre) {
  background: var(--color-pre-bg);
  padding: 0.9rem;
  border-radius: var(--radius);
  overflow-x: auto;
  font-size: 0.85rem;
}
.preview :deep(code) { font-family: var(--font-mono); }
.preview :deep(p > code) {
  background: var(--color-code-bg);
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  font-size: 0.88em;
}
.preview :deep(blockquote) {
  border-left: 3px solid var(--color-primary);
  padding-left: 1rem;
  margin: 0.8em 0;
  color: var(--color-text-secondary);
}
.preview :deep(img) { max-width: 100%; border-radius: var(--radius); }
.preview :deep(ul), .preview :deep(ol) { padding-left: 1.5em; }
.preview :deep(a) { color: var(--color-primary); }

.error {
  color: var(--color-danger);
  background: var(--color-danger-bg);
  padding: 0.7rem 0.9rem;
  border-radius: var(--radius);
  font-size: 0.88rem;
  border-left: 3px solid var(--color-danger);
}
.actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 1.5rem;
}
.btn-primary {
  padding: 0.75rem 2rem;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel {
  padding: 0.75rem 1.5rem;
  background: none;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.92rem;
  transition: all 0.2s ease;
}
.btn-cancel:hover {
  color: var(--color-text);
  border-color: var(--color-text);
}

@media (max-width: 768px) {
  .editor-wrap { grid-template-columns: 1fr; }
  .editor-wrap textarea, .preview { min-height: 280px; }
}
</style>
