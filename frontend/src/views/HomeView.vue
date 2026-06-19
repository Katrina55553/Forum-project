<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getTopics } from "../api/topic";
import { getTags } from "../api/tag";

const route = useRoute();
const router = useRouter();

const topics = ref([]);
const total = ref(0);
const pages = ref(0);
const page = ref(1);
const searchInput = ref(route.query.q || "");
const loading = ref(true);
const error = ref("");
const tags = ref([]);
const currentTag = computed(() => route.query.tag || "");

const q = computed(() => route.query.q || "");
const size = 10;

async function fetchTopics() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getTopics(page.value, size, q.value, currentTag.value);
    topics.value = res.data.items;
    total.value = res.data.total;
    pages.value = res.data.pages;
  } catch {
    error.value = "加载失败，请稍后重试";
  } finally {
    loading.value = false;
  }
}

async function fetchTags() {
  try {
    const res = await getTags();
    tags.value = res.data;
  } catch {
    // ignore
  }
}

function goPage(p) {
  page.value = p;
}

function doSearch() {
  const val = searchInput.value.trim();
  page.value = 1;
  const query = {};
  if (val) query.q = val;
  if (currentTag.value) query.tag = currentTag.value;
  router.push({ name: "home", query });
}

function filterByTag(slug) {
  page.value = 1;
  const query = { ...route.query };
  if (slug === currentTag.value) {
    delete query.tag;
  } else {
    query.tag = slug;
  }
  router.push({ name: "home", query });
}

function formatTime(t) {
  if (!t) return "";
  const date = new Date(t);
  const diff = Date.now() - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins}分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}小时前`;
  return date.toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" });
}

onMounted(() => {
  fetchTopics();
  fetchTags();
});
watch(page, fetchTopics);
// query 变化时只重置 page，由 page watcher 触发 fetchTopics，避免双重请求竞态
watch(() => route.query, () => {
  if (page.value !== 1) {
    page.value = 1;
  } else {
    fetchTopics();
  }
}, { deep: true });
</script>

<template>
  <div class="home">
    <!-- Editorial masthead -->
    <header class="masthead">
      <p class="masthead-eyebrow">论坛 · FORUM</p>
      <h1 class="masthead-title">
        <template v-if="currentTag">标签 · {{ tags.find(t => t.slug === currentTag)?.name || currentTag }}</template>
        <template v-else-if="q">搜索 · {{ q }}</template>
        <template v-else>思想的栖息地</template>
      </h1>
      <p class="masthead-sub">
        <template v-if="(q || currentTag) && !loading">
          找到 {{ total }} 篇帖子
          <router-link to="/" class="btn-clear">清除筛选</router-link>
        </template>
        <template v-else>
          在这里，每一篇帖子都是一次真诚的对话。
        </template>
      </p>
    </header>

    <form class="search-bar" @submit.prevent="doSearch">
      <svg class="search-icon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input v-model="searchInput" type="search" placeholder="搜索帖子、作者或关键词..." class="search-input" />
    </form>

    <!-- 标签筛选栏 -->
    <div v-if="tags.length" class="tags-bar">
      <button
        v-for="tag in tags"
        :key="tag.id"
        class="tag-chip"
        :class="{ active: currentTag === tag.slug }"
        @click="filterByTag(tag.slug)"
      >
        <span class="tag-hash">#</span>{{ tag.name }}
        <span class="tag-count">{{ tag.count }}</span>
      </button>
    </div>

    <div v-if="loading" class="skeleton-list">
      <div v-for="n in 5" :key="n" class="skeleton-row">
        <div class="skeleton-line w-70"></div>
        <div class="skeleton-line w-40"></div>
      </div>
    </div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchTopics">重试</button>
    </div>
    <div v-else-if="topics.length === 0" class="state empty">
      <div class="empty-mark">✦</div>
      <p>这里还很安静，写下第一篇吧。</p>
      <router-link to="/topic/new" class="btn-cta">发布新帖</router-link>
    </div>

    <div v-else class="topic-list">
      <article v-for="(t, idx) in topics" :key="t.id" class="topic-row" :class="{ pinned: t.is_pinned }">
        <div class="topic-index">{{ String(idx + 1 + (page - 1) * size).padStart(2, '0') }}</div>
        <div class="topic-main">
          <div class="topic-title-row">
            <span v-if="t.is_pinned" class="badge pin">置顶</span>
            <span v-if="t.is_featured" class="badge featured">精华</span>
            <router-link :to="`/topic/${t.id}`" class="topic-title">{{ t.title }}</router-link>
          </div>
          <div v-if="t.tags?.length" class="topic-tags">
            <span
              v-for="tag in t.tags"
              :key="tag.id"
              class="topic-tag"
              @click.prevent="filterByTag(tag.slug)"
            >
              #{{ tag.name }}
            </span>
          </div>
          <div class="topic-meta">
            <router-link :to="`/user/${t.author?.username}`" class="author">{{ t.author?.username }}</router-link>
            <span class="meta-dot">·</span>
            <span>{{ formatTime(t.created_at) }}</span>
          </div>
        </div>
        <div class="topic-stats">
          <span class="stat" title="回复">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            {{ t.comment_count }}
          </span>
          <span class="stat" title="点赞">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            {{ t.likes_count }}
          </span>
        </div>
      </article>

      <div v-if="pages > 1" class="pagination">
        <button :disabled="page <= 1" @click="goPage(page - 1)" class="page-nav">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          上一页
        </button>
        <span v-for="p in pages" :key="p" class="page-num-wrap">
          <button :class="{ current: p === page }" @click="goPage(p)" class="page-num">{{ p }}</button>
        </span>
        <button :disabled="page >= pages" @click="goPage(page + 1)" class="page-nav">
          下一页
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home { max-width: 760px; margin: 0 auto; }

/* Editorial masthead */
.masthead {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
}
.masthead-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin: 0 0 0.6rem;
  font-weight: 500;
}
.masthead-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 2.8rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin: 0 0 0.6rem;
  color: var(--color-text);
}
.masthead-sub {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.98rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

/* Search */
.search-bar {
  position: relative;
  margin-bottom: 1.5rem;
}
.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.7rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 0.95rem;
  box-sizing: border-box;
  background: var(--color-bg-elevated);
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  font-family: var(--font-sans);
}
.search-input::placeholder { color: var(--color-text-muted); }
.search-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}

.btn-clear {
  display: inline-flex;
  align-items: center;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0.15rem 0.7rem;
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 0.78rem;
  text-decoration: none;
  transition: all 0.2s ease;
}
.btn-clear:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

/* Tag chips */
.tags-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
}
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
}
.tag-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-1px);
}
.tag-chip.active {
  background: var(--color-text);
  color: var(--color-bg);
  border-color: var(--color-text);
}
.tag-hash {
  color: var(--color-text-muted);
  font-weight: 400;
}
.tag-chip.active .tag-hash { color: var(--color-bg); opacity: 0.6; }
.tag-count {
  font-size: 0.72rem;
  opacity: 0.6;
  font-variant-numeric: tabular-nums;
  margin-left: 0.15rem;
}

/* Topic list */
.topic-list { display: flex; flex-direction: column; }
.topic-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1.2rem;
  padding: 1.4rem 0.5rem;
  border-bottom: 1px solid var(--color-border-light);
  transition: background 0.2s ease;
  position: relative;
}
.topic-row:hover { background: var(--color-bg-secondary); }
.topic-row:hover .topic-index { color: var(--color-primary); }
.topic-row.pinned {
  background: var(--color-primary-soft);
  border-radius: var(--radius-lg);
  padding-left: 1.2rem;
  padding-right: 1.2rem;
  border-bottom: 1px solid var(--color-border-light);
  margin: 0.3rem 0;
}
.topic-row.pinned .topic-index { color: var(--color-primary); }

.topic-index {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-muted);
  opacity: 0.5;
  line-height: 1;
  transition: color 0.2s ease, opacity 0.2s ease;
  min-width: 2.2rem;
}

.topic-main { min-width: 0; }
.topic-title-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.badge {
  padding: 0.15rem 0.55rem;
  border-radius: 4px;
  font-size: 0.7rem;
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
.topic-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.01em;
  transition: color 0.2s ease;
}
.topic-title:hover { color: var(--color-primary); }

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.45rem;
}
.topic-tag {
  padding: 0.1rem 0;
  background: none;
  border: none;
  font-size: 0.78rem;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color 0.2s ease;
}
.topic-tag:hover {
  color: var(--color-primary);
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  margin-top: 0.45rem;
}
.author {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}
.author:hover { color: var(--color-primary); }
.meta-dot { opacity: 0.5; }

.topic-stats {
  display: flex;
  gap: 0.9rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.stat {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: color 0.2s ease;
}
.stat:hover { color: var(--color-primary); }

/* States */
.state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--color-text-muted);
}
.state.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
}
.empty-mark {
  font-size: 2.5rem;
  color: var(--color-primary);
  opacity: 0.5;
  margin-bottom: 0.5rem;
}
.btn-cta {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.6rem 1.5rem;
  background: var(--color-text);
  color: var(--color-bg);
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-cta:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
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

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 0; }
.skeleton-row {
  padding: 1.4rem 0.5rem;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, var(--color-border-light) 0%, var(--color-border) 50%, var(--color-border-light) 100%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: shimmer 1.6s infinite linear;
}
.skeleton-line.w-70 { width: 70%; }
.skeleton-line.w-40 { width: 40%; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.4rem;
  margin-top: 3rem;
  padding-top: 1.5rem;
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
  font-variant-numeric: tabular-nums;
  transition: all 0.2s ease;
}
.page-num:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}
.page-num.current {
  background: var(--color-text);
  color: var(--color-bg);
  font-weight: 600;
}
.page-nav {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
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

@media (max-width: 640px) {
  .topic-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 1.2rem 0.3rem;
  }
  .topic-index { display: none; }
  .topic-stats { margin-left: 0; }
  .pagination { flex-wrap: wrap; }
}
</style>
