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
        {{ tag }}
        <button type="button" @click="removeTag(index)" class="tag-remove">&times;</button>
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
      <span class="suggestions-label">热门标签：</span>
      <button
        v-for="tag in suggestions"
        :key="tag.id"
        type="button"
        class="suggestion-tag"
        :class="{ active: tags.includes(tag.name) }"
        @click="addSuggestion(tag)"
      >
        {{ tag.name }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.tag-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-bg);
  min-height: 42px;
  align-items: center;
}
.tags-display:focus-within {
  border-color: var(--color-primary);
}
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.6rem;
  background: var(--color-primary);
  color: #fff;
  border-radius: 4px;
  font-size: 0.85rem;
}
.tag-remove {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  opacity: 0.7;
}
.tag-remove:hover {
  opacity: 1;
}
.tag-field {
  flex: 1;
  min-width: 120px;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.95rem;
  padding: 0.2rem;
  color: var(--color-text);
}
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}
.suggestions-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.suggestion-tag {
  padding: 0.2rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-bg-secondary);
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.8rem;
}
.suggestion-tag:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.suggestion-tag.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
</style>
