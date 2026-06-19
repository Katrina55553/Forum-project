<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";
import { getUnreadCount } from "./api/notification";
import { getUnreadMessageCount } from "./api/message";
import AppToast from "./components/AppToast.vue";
import BackToTop from "./components/BackToTop.vue";
import ConfirmDialog from "./components/ConfirmDialog.vue";

const router = useRouter();
const auth = useAuthStore();

const isDark = ref(false);
const menuOpen = ref(false);
const navRef = ref(null);
const userMenuOpen = ref(false);
const userMenuRef = ref(null);
const unreadCount = ref(0);
const unreadMessageCount = ref(0);

const totalUnread = computed(() => unreadCount.value + unreadMessageCount.value);

let notifTimer = null;

function onDocClick(e) {
  if (menuOpen.value && navRef.value && !navRef.value.contains(e.target)) {
    closeMenu();
  }
  if (userMenuOpen.value && userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    userMenuOpen.value = false;
  }
}

function initTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
    isDark.value = true;
    document.documentElement.setAttribute("data-theme", "dark");
  }
}

function toggleTheme() {
  isDark.value = !isDark.value;
  document.documentElement.setAttribute("data-theme", isDark.value ? "dark" : "");
  localStorage.setItem("theme", isDark.value ? "dark" : "light");
}

function closeMenu() {
  menuOpen.value = false;
}

function userInitial() {
  return auth.user?.username?.[0]?.toUpperCase() || "?";
}

function goProfile() {
  userMenuOpen.value = false;
  router.push("/profile/edit");
}

function logout() {
  auth.logout();
  closeMenu();
  userMenuOpen.value = false;
  router.push("/");
}

async function fetchUnreadCount() {
  try {
    const res = await getUnreadCount();
    unreadCount.value = res.data.count;
  } catch {
    // ignore
  }
}

async function fetchUnreadMessageCount() {
  try {
    const res = await getUnreadMessageCount();
    unreadMessageCount.value = res.data.count;
  } catch {
    // ignore
  }
}

function startPolling() {
  if (notifTimer) clearInterval(notifTimer);
  fetchUnreadCount();
  fetchUnreadMessageCount();
  notifTimer = setInterval(() => {
    fetchUnreadCount();
    fetchUnreadMessageCount();
  }, 30000);
}

function stopPolling() {
  if (notifTimer) {
    clearInterval(notifTimer);
    notifTimer = null;
  }
}

// 监听登录状态变化
watch(() => auth.user, (newUser, oldUser) => {
  if (newUser && !oldUser) {
    startPolling();
  } else if (!newUser && oldUser) {
    stopPolling();
  }
});

function onAuthExpired() {
  auth.clearAuth();
  stopPolling();
}

onMounted(async () => {
  initTheme();
  await auth.restoreUser();
  document.addEventListener("click", onDocClick);
  window.addEventListener("auth-expired", onAuthExpired);
  if (auth.user) {
    startPolling();
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
  window.removeEventListener("auth-expired", onAuthExpired);
  if (notifTimer) clearInterval(notifTimer);
});
</script>

<template>
  <header class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand" @click="closeMenu">
        <span class="brand-mark">✦</span>
        <span class="brand-text">Inkwell</span>
      </router-link>

      <button class="hamburger" @click="menuOpen = !menuOpen" :aria-label="menuOpen ? '关闭菜单' : '打开菜单'">
        <span></span><span></span><span></span>
      </button>

      <nav ref="navRef" :class="{ open: menuOpen }">
        <router-link to="/" class="nav-link" @click="closeMenu">首页</router-link>

        <template v-if="auth.user">
          <router-link to="/topic/new" class="nav-link nav-link-cta" @click="closeMenu">
            <span class="cta-plus">+</span> 发帖
          </router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-link" @click="closeMenu">登录</router-link>
          <router-link to="/register" class="nav-link nav-link-cta" @click="closeMenu">注册</router-link>
        </template>

        <!-- Messages (notifications + messages) -->
        <router-link v-if="auth.user" to="/messages" class="nav-icon-btn nav-messages" :aria-label="'消息'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
          </svg>
          <span v-if="totalUnread > 0" class="notif-badge">{{ totalUnread > 99 ? '99+' : totalUnread }}</span>
        </router-link>

        <!-- User avatar + dropdown -->
        <div v-if="auth.user" ref="userMenuRef" class="user-menu">
          <button class="avatar-btn" @click="userMenuOpen = !userMenuOpen" :aria-label="'用户菜单'">
            <img v-if="auth.user.avatar" :src="auth.user.avatar" class="avatar-img" />
            <span v-else class="avatar-text">{{ userInitial() }}</span>
          </button>
          <Transition name="dropdown">
            <div v-if="userMenuOpen" class="dropdown">
              <div class="dropdown-header">
                <div class="dropdown-avatar">
                  <img v-if="auth.user.avatar" :src="auth.user.avatar" />
                  <span v-else>{{ userInitial() }}</span>
                </div>
                <div class="dropdown-user">
                  <div class="dropdown-username">{{ auth.user.username }}</div>
                  <div class="dropdown-role">{{ auth.user.is_admin ? '管理员' : '成员' }}</div>
                </div>
              </div>
              <button class="dropdown-item" @click="goProfile">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                编辑信息
              </button>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout" @click="logout">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                退出账号
              </button>
            </div>
          </Transition>
        </div>

        <button class="nav-icon-btn theme-toggle" @click="toggleTheme" :aria-label="isDark ? '切换亮色' : '切换暗色'">
          <svg v-if="isDark" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          <svg v-else width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>

        <a
          href="https://github.com/Katrina55553/Forum-project"
          target="_blank"
          rel="noopener noreferrer"
          class="nav-icon-btn github-link"
          :aria-label="'GitHub'"
        >
          <svg width="17" height="17" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
        </a>
      </nav>
    </div>
  </header>
  <main class="container">
    <router-view />
  </main>
  <BackToTop />
  <AppToast />
  <ConfirmDialog />
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(247, 243, 236, 0.82);
  backdrop-filter: saturate(180%) blur(14px);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid var(--color-border-light);
  transition: background 0.4s ease, border-color 0.4s ease;
}
[data-theme="dark"] .navbar {
  background: rgba(22, 19, 16, 0.82);
}
.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 64px;
  max-width: 1080px;
  margin: 0 auto;
}

/* Brand */
.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-mark {
  font-size: 1.15rem;
  color: var(--color-primary);
  transform: translateY(-1px);
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.brand:hover .brand-mark {
  transform: translateY(-1px) rotate(72deg);
}
.brand-text {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

/* Hamburger */
.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
}
.hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--color-text);
  border-radius: 2px;
  transition: transform 0.25s ease, opacity 0.25s ease;
}

nav {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.nav-link {
  position: relative;
  color: var(--color-text-secondary);
  font-size: 0.92rem;
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  padding: 0.5rem 0.85rem;
  border-radius: var(--radius);
  transition: color 0.2s ease, background 0.2s ease;
}
.nav-link:hover {
  color: var(--color-text);
  background: var(--color-bg-secondary);
}
.nav-link.router-link-exact-active {
  color: var(--color-text);
}
.nav-link.router-link-exact-active::after {
  content: "";
  position: absolute;
  left: 0.85rem;
  right: 0.85rem;
  bottom: 0.25rem;
  height: 2px;
  background: var(--color-primary);
  border-radius: 2px;
}

/* CTA-style nav link (发帖 / 注册) */
.nav-link-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: var(--color-text);
  color: var(--color-bg);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.88rem;
  transition: transform 0.2s ease, background 0.2s ease;
}
.nav-link-cta:hover {
  background: var(--color-text);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.nav-link-cta.router-link-active::after { display: none; }
.cta-plus {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1;
}

/* Icon buttons (messages, theme, github) */
.nav-icon-btn {
  position: relative;
  background: none;
  border: 1px solid transparent;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  text-decoration: none;
  flex-shrink: 0;
  transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}
.nav-icon-btn:hover {
  color: var(--color-text);
  background: var(--color-bg-secondary);
  border-color: var(--color-border-light);
}

/* Notification badge */
.notif-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: var(--color-primary);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  min-width: 17px;
  height: 17px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid var(--color-bg);
  font-family: var(--font-sans);
}

/* User avatar + dropdown */
.user-menu {
  position: relative;
  flex-shrink: 0;
  margin-left: 0.25rem;
}
.avatar-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  cursor: pointer;
  padding: 0;
  overflow: hidden;
  transition: border-color 0.2s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-btn:hover {
  border-color: var(--color-text);
  transform: scale(1.05);
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
.avatar-text {
  color: #fff;
  font-weight: 700;
  font-size: 0.92rem;
  user-select: none;
}

.dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 220px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 200;
  overflow: hidden;
  padding: 0.4rem;
}
.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.7rem 0.7rem 0.9rem;
  border-bottom: 1px solid var(--color-border-light);
  margin-bottom: 0.3rem;
}
.dropdown-avatar {
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
.dropdown-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.dropdown-username {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--color-text);
  line-height: 1.2;
}
.dropdown-role {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-top: 0.15rem;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.6rem 0.7rem;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  white-space: nowrap;
  border-radius: var(--radius);
  transition: background 0.15s ease, color 0.15s ease;
}
.dropdown-item:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}
.dropdown-item.logout {
  color: var(--color-danger);
}
.dropdown-item.logout:hover {
  background: var(--color-danger-bg);
}
.dropdown-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 0.3rem 0;
}

/* Dropdown transition */
.dropdown-enter-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}

.container {
  max-width: 820px;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
}

/* Mobile */
@media (max-width: 640px) {
  .navbar-inner { padding: 0 1.1rem; height: 58px; }
  .hamburger { display: flex; }
  nav {
    display: none;
    position: absolute;
    top: 58px;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    background: var(--color-bg-elevated);
    border-bottom: 1px solid var(--color-border);
    box-shadow: var(--shadow-lg);
    padding: 0.6rem;
  }
  nav.open { display: flex; }
  .nav-link {
    padding: 0.85rem 1rem;
    border-radius: var(--radius);
    font-size: 1rem;
  }
  .nav-link.router-link-exact-active::after { display: none; }
  .nav-link.router-link-exact-active {
    background: var(--color-bg-secondary);
  }
  .nav-link-cta {
    justify-content: center;
    margin: 0.3rem 0;
  }
  .nav-icon-btn {
    align-self: flex-start;
  }
  .user-menu {
    padding: 0.5rem 0;
    margin-left: 0;
  }
  .dropdown {
    left: 0;
    right: 0;
    top: auto;
    position: relative;
    margin-top: 0.5rem;
    box-shadow: none;
    border: 1px solid var(--color-border-light);
  }
  .container {
    padding: 2rem 1.1rem 4rem;
  }
}
</style>
