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
    <h1>编辑资料</h1>

    <form @submit.prevent="handleSave" class="edit-form">
      <div v-if="success" class="success">保存成功</div>
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

    <hr class="divider" />

    <h2>修改密码</h2>
    <form @submit.prevent="handleChangePassword" class="edit-form">
      <div v-if="pwSuccess" class="success">密码已更新</div>
      <div v-if="pwError" class="error">{{ pwError }}</div>

      <label>
        <span>旧密码</span>
        <input v-model="oldPassword" type="password" autocomplete="current-password" />
      </label>
      <label>
        <span>新密码</span>
        <input v-model="newPassword" type="password" autocomplete="new-password" />
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
.profile-edit { max-width: 480px; margin: 0 auto; }
h1 { margin-bottom: 1.5rem; color: var(--color-text); }
.edit-form { display: flex; flex-direction: column; gap: 1rem; }
.success {
  color: #2e7d32;
  background: #e8f5e9;
  padding: 0.5rem;
  border-radius: var(--radius);
  font-size: 0.9rem;
}
.error {
  color: var(--color-danger);
  background: var(--color-danger-bg);
  padding: 0.5rem;
  border-radius: var(--radius);
  font-size: 0.9rem;
}
label span {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}
input, textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 1rem;
  box-sizing: border-box;
  font-family: inherit;
  background: var(--color-bg);
  color: var(--color-text);
}
textarea { resize: vertical; }
.form-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-top: 0.5rem;
}
.btn-save {
  padding: 0.6rem 2rem;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: var(--radius);
  font-size: 1rem;
  cursor: pointer;
}
.btn-save:disabled { opacity: 0.5; }
.btn-cancel { color: var(--color-text-muted); text-decoration: none; font-size: 0.95rem; }
.btn-cancel:hover { color: var(--color-text); }

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--color-bg-secondary);
  border-radius: var(--radius);
}
.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-initial {
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--color-text-muted);
}
.avatar-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.btn-upload {
  display: inline-block;
  padding: 0.5rem 1.2rem;
  background: var(--color-text);
  color: var(--color-bg);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-upload:hover { opacity: 0.9; }
.hint {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin: 0;
}
.url-input {
  width: 100%;
  margin-top: 0.5rem;
}
.url-input summary {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  cursor: pointer;
}
.url-input summary:hover { color: var(--color-text); }
.url-input input {
  margin-top: 0.5rem;
}

.divider {
  margin: 2.5rem 0 1.5rem;
  border: none;
  border-top: 1px solid var(--color-border);
}
h2 { color: var(--color-text); font-size: 1.2rem; margin-bottom: 1rem; }
</style>
