<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { updateMe, changePassword } from "../api/auth";
import { uploadAvatar } from "../api/upload";

const router = useRouter();
const auth = useAuthStore();

const avatar = ref("");
const avatarPreview = ref("");
const avatarFile = ref(null);
const uploading = ref(false);
const bio = ref("");
const githubUrl = ref("");
const saving = ref(false);
const error = ref("");
const success = ref(false);

const oldPassword = ref("");
const newPassword = ref("");
const pwSaving = ref(false);
const pwError = ref("");
const pwSuccess = ref(false);

onMounted(() => {
  if (auth.user) {
    avatar.value = auth.user.avatar || "";
    avatarPreview.value = auth.user.avatar || "";
    bio.value = auth.user.bio || "";
    githubUrl.value = auth.user.github_url || "";
  }
});

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  avatarFile.value = file;
  // 释放上一次的 ObjectURL 避免内存泄漏
  if (avatarPreview.value && avatarPreview.value.startsWith("blob:")) {
    URL.revokeObjectURL(avatarPreview.value);
  }
  avatarPreview.value = URL.createObjectURL(file);
}

async function handleSave() {
  error.value = "";
  success.value = false;
  saving.value = true;
  try {
    let avatarUrl = avatar.value;

    // 如果选择了新文件，先上传
    if (avatarFile.value) {
      uploading.value = true;
      const res = await uploadAvatar(avatarFile.value);
      avatarUrl = res.data.url;
      uploading.value = false;
    }

    const res = await updateMe({
      avatar: avatarUrl || null,
      bio: bio.value || null,
      github_url: githubUrl.value || null,
    });
    auth.user = res.data;
    localStorage.setItem("user", JSON.stringify(res.data));
    success.value = true;
  } catch (e) {
    uploading.value = false;
    error.value = e.response?.data?.detail || "保存失败";
  } finally {
    saving.value = false;
  }
}

async function handleChangePassword() {
  pwError.value = "";
  pwSuccess.value = false;
  if (!oldPassword.value || !newPassword.value) {
    pwError.value = "请填写旧密码和新密码";
    return;
  }
  pwSaving.value = true;
  try {
    await changePassword(oldPassword.value, newPassword.value);
    pwSuccess.value = true;
    oldPassword.value = "";
    newPassword.value = "";
  } catch (e) {
    pwError.value = e.response?.data?.detail || "修改失败";
  } finally {
    pwSaving.value = false;
  }
}
</script>

<template>
  <div class="profile-edit">
    <header class="edit-header">
      <p class="edit-eyebrow">个人资料 · PROFILE</p>
      <h1>编辑资料</h1>
    </header>

    <form @submit.prevent="handleSave" class="edit-form card">
      <div v-if="success" class="success">✓ 保存成功</div>
      <div v-if="error" class="error">{{ error }}</div>

      <!-- 头像上传区域 -->
      <div class="avatar-section">
        <div class="avatar-preview">
          <img v-if="avatarPreview" :src="avatarPreview" alt="头像预览" />
          <span v-else class="avatar-initial">{{ auth.user?.username?.[0]?.toUpperCase() }}</span>
        </div>
        <div class="avatar-actions">
          <label class="btn-upload">
            选择图片
            <input type="file" accept="image/jpeg,image/png,image/gif,image/webp" @change="handleFileSelect" hidden />
          </label>
          <p class="hint">支持 JPG、PNG、GIF、WebP，最大 2MB</p>
        </div>
        <details class="url-input">
          <summary>或输入图片 URL</summary>
          <input v-model="avatar" type="text" placeholder="https://..." />
        </details>
      </div>

      <label>
        <span>个人简介</span>
        <textarea v-model="bio" rows="3" placeholder="介绍一下自己..."></textarea>
      </label>

      <label>
        <span>GitHub</span>
        <input v-model="githubUrl" type="text" placeholder="https://github.com/..." />
      </label>

      <div class="form-actions">
        <button type="submit" :disabled="saving" class="btn-save">
          {{ saving ? "保存中..." : "保存" }}
        </button>
        <router-link to="/" class="btn-cancel">取消</router-link>
      </div>
    </form>

    <h2 class="section-title">修改密码</h2>
    <form @submit.prevent="handleChangePassword" class="edit-form card">
      <div v-if="pwSuccess" class="success">✓ 密码已更新</div>
      <div v-if="pwError" class="error">{{ pwError }}</div>

      <label>
        <span>旧密码</span>
        <input v-model="oldPassword" type="password" autocomplete="current-password" placeholder="输入当前密码" />
      </label>
      <label>
        <span>新密码</span>
        <input v-model="newPassword" type="password" autocomplete="new-password" placeholder="设置新密码" />
      </label>
      <div class="form-actions">
        <button type="submit" :disabled="pwSaving" class="btn-save">
          {{ pwSaving ? "修改中..." : "修改密码" }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.profile-edit { max-width: 540px; margin: 0 auto; }

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
  font-size: clamp(1.8rem, 4vw, 2.2rem);
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.card {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: 1.8rem;
  box-shadow: var(--shadow-sm);
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.success {
  color: var(--color-success);
  background: var(--color-success-bg);
  padding: 0.7rem 0.9rem;
  border-radius: var(--radius);
  font-size: 0.88rem;
  border-left: 3px solid var(--color-success);
  font-weight: 500;
}
.error {
  color: var(--color-danger);
  background: var(--color-danger-bg);
  padding: 0.7rem 0.9rem;
  border-radius: var(--radius);
  font-size: 0.88rem;
  border-left: 3px solid var(--color-danger);
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
label span {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  letter-spacing: 0.02em;
}
input, textarea {
  width: 100%;
  padding: 0.75rem 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.95rem;
  box-sizing: border-box;
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
input::placeholder, textarea::placeholder { color: var(--color-text-muted); }
input:focus, textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-soft);
}
textarea { resize: vertical; line-height: 1.6; }
.form-actions {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  margin-top: 0.3rem;
}
.btn-save {
  padding: 0.7rem 1.8rem;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: 999px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel {
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.92rem;
  padding: 0.7rem 1rem;
  transition: color 0.2s ease;
}
.btn-cancel:hover { color: var(--color-text); }

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}
.avatar-preview {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid var(--color-bg-elevated);
  box-shadow: var(--shadow-md);
}
.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-initial {
  font-family: var(--font-display);
  font-size: 2.6rem;
  font-weight: 700;
  color: #fff;
}
.avatar-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.btn-upload {
  display: inline-block;
  padding: 0.55rem 1.3rem;
  background: var(--color-text);
  color: var(--color-bg);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-upload:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.hint {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin: 0;
}
.url-input {
  width: 100%;
  margin-top: 0.3rem;
}
.url-input summary {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  cursor: pointer;
  text-align: center;
  transition: color 0.2s ease;
}
.url-input summary:hover { color: var(--color-text); }
.url-input input {
  margin-top: 0.6rem;
}

.section-title {
  font-family: var(--font-display);
  color: var(--color-text);
  font-size: 1.3rem;
  font-weight: 600;
  margin: 2.5rem 0 1rem;
  letter-spacing: -0.01em;
}
</style>
