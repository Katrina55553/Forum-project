# Inkwell · 论坛系统

![Vue 3](https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Vue Router](https://img.shields.io/badge/Vue_Router-42B883?style=flat-square&logo=vuedotjs&logoColor=white)
![Pinia](https://img.shields.io/badge/Pinia-FFC43D?style=flat-square&logo=pinia&logoColor=black)
![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat-square&logo=axios&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL_16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)

A minimalist, high-performance community forum powered by **Vue 3** + **FastAPI**.

基于 **Vue 3** + **FastAPI** 的极简社区论坛，支持标签、楼中楼评论、私信、通知与管理员置顶/加精。

## Tech Stack / 技术栈

| Layer 层 | Technology 技术 |
| ------------ | ----------------------------------------- |
| Frontend 前端 | Vue 3 · Vite · Vue Router · Pinia · Axios |
| Backend 后端 | FastAPI · SQLAlchemy 2.0 · Pydantic |
| Database 数据库 | PostgreSQL 16（dev + prod，无回退方案） |
| Auth 认证 | JWT（HS256，24h 过期）· bcrypt |
| Markdown | marked（渲染）· DOMPurify（前端过滤）· bleach（后端过滤） |
| 限流 | slowapi |
| 文件上传 | python-multipart · 本地 `backend/uploads/` |
| Deploy 部署 | Docker · docker-compose · nginx |

## Getting Started / 快速开始

### Option A: Docker (recommended) / Docker 部署

```bash
cp .env.example .env
# 编辑 .env —— 至少填 SECRET_KEY 与 DB_PASSWORD
docker compose up -d
```

App: `http://localhost:80` · API: `http://localhost:8000`

### Option B: Manual / 手动启动

**Prerequisites / 环境要求:** Python 3.12（Docker 镜像用 3.12-slim）/ Node.js 24+ / **PostgreSQL 必须可用**

```bash
# 数据库 —— 用 Docker 起一个 PG，或使用本地 PostgreSQL
docker compose up db -d

# 后端
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

API: `http://localhost:8000` · Swagger: `http://localhost:8000/docs` · App: `http://localhost:5173`

> 后端启动时会连接 PostgreSQL 并在缺失时自动建表、补齐新增列（`ensure_schema()`）。数据库连不上会直接启动失败，不会自动降级到 SQLite。

### Seed Data / 测试数据

```bash
cd backend
source venv/Scripts/activate
python seed.py                 # 幂等：admin / admin123 + 一个欢迎帖
```

## API Overview / API 概览

共 29 个端点，全部挂在 `/api/` 前缀下（另有 `GET /` 返回服务标识）。

### Public / 公开

| Method | Path | Description / 说明 |
| ------ | --------------------- | ---------------------------------------- |
| GET | `/api/topics` | 帖子列表（`?page=&size=&q=&tag=`） |
| GET | `/api/topics/{id}` | 帖子详情 + 评论树 + 点赞状态 + 标签 |
| GET | `/api/tags` | 全部标签及各自的帖子数 |
| GET | `/api/users/{username}` | 用户主页 + TA 的帖子 |
| POST | `/api/auth/register` | 注册（5/min 限流） |
| POST | `/api/auth/login` | 登录 → JWT（10/min 限流） |

### Authenticated / 需登录

| Method | Path | Description / 说明 |
| ------ | ------------------------------- | ------------------------------------ |
| GET | `/api/auth/me` | 当前用户信息 |
| PUT | `/api/auth/me` | 更新 avatar / bio / github_url |
| PUT | `/api/auth/password` | 修改密码（5/min 限流） |
| POST | `/api/upload/avatar` | 上传头像（10/min，≤2MB，JPG/PNG/GIF/WebP） |
| GET | `/api/topics/{id}/edit` | 取帖子用于编辑（作者或管理员） |
| POST | `/api/topics` | 发帖（10/min 限流，可带 tags） |
| PUT | `/api/topics/{id}` | 编辑帖子（作者或管理员） |
| DELETE | `/api/topics/{id}` | 删除帖子（作者或管理员） |
| POST | `/api/comments` | 发表评论或回复（10/min 限流，触发通知） |
| DELETE | `/api/comments/{id}` | 删除评论（作者或管理员） |
| POST | `/api/likes/{topic_id}` | 点赞（幂等） |
| DELETE | `/api/likes/{topic_id}` | 取消点赞 |
| GET | `/api/notifications` | 通知列表（`?page=&size=`） |
| GET | `/api/notifications/unread-count` | 未读通知数 |
| PUT | `/api/notifications/{id}/read` | 标记单条已读 |
| PUT | `/api/notifications/read-all` | 全部标记已读 |
| POST | `/api/messages` | 发送私信 `{receiver, content}`（10/min 限流） |
| GET | `/api/messages` | 会话列表（含每会话未读数） |
| GET | `/api/messages/unread-count` | 未读私信总数 |
| GET | `/api/messages/{username}` | 与某用户的私信记录（读取后自动标记已读） |
| PUT | `/api/messages/{username}/read` | 标记与该用户的私信为已读 |

### Admin only / 仅管理员

| Method | Path | Description / 说明 |
| ------ | -------------------------- | ------------------ |
| PUT | `/api/topics/{id}/pin` | 切换置顶 |
| PUT | `/api/topics/{id}/featured` | 切换加精 |

## Project Structure / 项目结构

```
forum-project/
├── backend/
│   ├── main.py          # FastAPI app、29 个路由、中间件、上传与错误处理
│   ├── models.py        # ORM: User, Topic, Comment, Notification, Message, Tag, likes, topic_tags
│   ├── schemas.py       # Pydantic 请求/响应模型 + field_validator
│   ├── crud.py          # 纯数据库操作 + build_comment_tree()
│   ├── auth.py          # bcrypt、JWT、get_current_user / get_optional_user / require_admin
│   ├── database.py      # engine、SessionLocal、Base、ensure_schema()
│   ├── seed.py          # 幂等测试数据
│   ├── uploads/avatars/ # 头像存储（运行时创建，已 gitignore）
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue      # 导航栏、主题切换、未读角标轮询、全局组件挂载
│   │   ├── style.css    # 60 条 CSS 变量声明，暖纸 / 深墨双主题
│   │   ├── router/      # 12 条路由、认证守卫、标题与滚动行为
│   │   ├── stores/      # Pinia auth store
│   │   ├── api/         # 10 个 Axios 模块
│   │   ├── components/  # 5 个全局组件
│   │   ├── composables/ # toast / confirm
│   │   └── views/       # 11 个页面
│   ├── nginx.conf       # 生产 SPA 回退 + /api 与 /uploads 反代
│   └── vite.config.js   # dev 代理 /api 与 /uploads → :8000
├── docker-compose.yml   # PostgreSQL 16 + backend + frontend
├── deploy.sh            # 一键部署（生成 .env → 构建 → seed）
└── .env.example
```

### Frontend detail / 前端明细

| 目录 | 文件 |
| ----------- | ----------------------------------------------------------------------------------- |
| `views/` | HomeView · TopicDetailView · TopicEditView · MessagesView · ChatView · LoginView · RegisterView · UserProfile · ProfileEdit · NotFoundView |
| `components/` | AppToast · ConfirmDialog · BackToTop · CommentItem · TagInput |
| `api/` | client · auth · topic · tag · comment · like · notification · message · upload · user |

> `/notifications` 已重定向到 `/messages`：通知与私信合并进统一收件箱（`MessagesView`）。曾经的死代码 `NotificationsView.vue` 已于 2026-09-26 删除。

## Features / 功能

| Feature / 功能 | Description / 说明 |
| ----------------------------- | ------------------------------------------------- |
| Topic CRUD / 帖子管理 | Markdown 编辑（textarea + 实时预览） |
| Tags / 标签 | 发帖打标签、首页标签栏筛选、热门标签建议 |
| Nested comments / 评论嵌套 | 多级楼中楼，`CommentItem` 递归渲染 |
| Likes / 点赞 | 复合主键保证幂等 |
| Full-text search / 全文搜索 | 标题 + 正文，`ILIKE` 且转义 `%` `_` |
| Notifications / 通知 | 回复通知 + 未读角标 |
| Private messages / 私信 | 会话列表、气泡对话、10s 轮询新消息 |
| Unified inbox / 统一收件箱 | 通知与私信合并按时间排序 |
| Moderation / 内容管理 | 管理员置顶、加精；作者/管理员可编辑删除 |
| User profiles / 用户主页 | 头像、简介、GitHub、发帖与评论数 |
| Avatar upload / 头像上传 | 魔数字节校验 + UUID 文件名 + 静态托管 |
| JWT auth / JWT 认证 | 24h 过期，401 拦截并回跳登录 |
| Toast / 消息提示 | 替代 alert 的成功/失败/提示条 |
| Confirm dialog / 确认弹窗 | Promise 化的模态确认 |
| Back to top / 回到顶部 | 滚动 >400px 出现 |
| Responsive / 响应式 | ≤640px 折叠为汉堡菜单 |
| Dark mode / 暗色模式 | 切换 + 首次跟随系统偏好 |
| Skeleton loading / 骨架屏 | 列表、详情、表单 |
| Rate limiting / 限流 | slowapi 覆盖注册/登录/发帖/评论/改密/上传 |
| HTML sanitization / HTML 过滤 | 后端 bleach 白名单 + 前端 DOMPurify |
| Request logging / 请求日志 | 方法、路径、状态码、耗时 |
| Docker deploy / 容器化部署 | PG + 后端 + nginx 多服务编排 |
