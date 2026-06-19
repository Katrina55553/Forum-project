import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || "";
      // 登录/注册接口的 401 不重定向，让调用方处理错误信息
      const isAuthEndpoint = url.includes("/auth/login") || url.includes("/auth/register");
      if (!isAuthEndpoint) {
        // 清除本地存储
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        // 通知 Pinia store 清除状态
        window.dispatchEvent(new CustomEvent("auth-expired"));
        const currentPath = window.location.pathname;
        if (currentPath !== "/login" && currentPath !== "/register") {
          window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
        } else {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  },
);

export default client;
