<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  suggestions: { type: Array, default: () => [] },
});

const emit = defineEmits(["update:modelValue"]);

const input = ref("");
const tags = ref([...props.modelValue]);

watch(() => props.modelValue, (val) => {
  tags.value = [...val];
});

function addTag(name) {
  name = name.trim();
  if (!name || tags.value.includes(name)) {
    input.value = "";
    return;
  }
  tags.value.push(name);
  emit("update:modelValue", tags.value);
  input.value = "";
}

function removeTag(index) {
  tags.value.splice(index, 1);
  emit("update:modelValue", tags.value);
}

function onKeydown(e) {
  if (e.key === "Enter" || e.key === ",") {
    e.preventDefault();
    addTag(input.value);
  }
  if (e.key === "Backspace" && !input.value && tags.value.length) {
    tags.value.pop();
    emit("update:modelValue", tags.value);
  }
}

function addSuggestion(tag) {
  if (!tags.value.includes(tag.name)) {
    tags.value.push(tag.name);
    emit("update:modelValue", tags.value);
  }
}
</script>

<template>
  <div class="tag-input">
    <div class="tags-display">
      <span v-for="(tag, index) in tags" :key="index" class="tag">
        <span class="tag-hash">#</span>{{ tag }}
        <button type="button" @click="removeTag(index)" class="tag-remove" aria-label="移除标签">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </span>
      <input
        v-model="input"
        type="text"
        placeholder="输入标签，按回车添加..."
        @keydown="onKeydown"
        class="tag-field"
      />
    </div>
    <div v-if="suggestions.length" class="suggestions">
      <span class="suggestions-label">热门标签</span>
      <button
        v-for="tag in suggestions"
        :key="tag.id"
        type="button"
        class="suggestion-tag"
        :class="{ active: tags.includes(tag.name) }"
        @click="addSuggestion(tag)"
      >
        #{{ tag.name }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.tag-input {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0.55rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-bg);
  min-height: 46px;
  align-items: center;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.tags-display:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.4rem 0.25rem 0.55rem;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 500;
  font-family: var(--font-mono);
}
.tag-hash {
  opacity: 0.6;
}
.tag-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  padding: 0;
  margin-left: 0.1rem;
  border-radius: 50%;
  opacity: 0.6;
  transition: opacity 0.2s, background 0.2s;
}
.tag-remove:hover {
  opacity: 1;
  background: rgba(184, 67, 31, 0.2);
}
.tag-field {
  flex: 1;
  min-width: 140px;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.92rem;
  padding: 0.2rem;
  color: var(--color-text);
  font-family: inherit;
}
.tag-field::placeholder {
  color: var(--color-text-muted);
}
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}
.suggestions-label {
  font-size: 0.72rem;
  font-family: var(--font-mono);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-right: 0.2rem;
}
.suggestion-tag {
  padding: 0.25rem 0.7rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font-mono);
  transition: all 0.2s;
}
.suggestion-tag:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-soft);
}
.suggestion-tag.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
</style>
