# AGENTS.md

本文件面向**在本仓库工作的 AI 编码助手与贡献者**，说明「在这里改代码需要知道什么」：命令、架构地图、编码约定、必须避开的坑、以及当前已确认的缺陷。

> 产品介绍、功能清单、快速开始请见 `README.md`。两者有意分工：README 面向使用者，本文件面向改动代码的人。

## 项目概览 / Project Overview

一个极简社区论坛系统，品牌名 **Inkwell**。全栈实现：Vue 3 前端 + FastAPI 后端 + PostgreSQL + JWT 认证 + Docker 部署。

它是从一个**个人技术博客渐进改造**而来，因此数据库名与容器用户名仍叫 `blog`，`docs/superpowers/` 保留着改造过程记录——**不要"顺手"把这些历史命名重命名掉**。

当前功能集：帖子、标签、楼中楼评论、点赞、回复通知、私信、管理员置顶/加精、头像上传。

## 命令 / Commands

```bash
# 后端
cd backend
source venv/Scripts/activate   # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev                     # :5173，代理 /api 与 /uploads → :8000
npm run build                   # 生产构建 → dist/
npm run preview                 # 本地预览生产构建

# 种子数据（后端 venv，幂等）
cd backend && python seed.py    # admin / admin123

# 只起本地 PostgreSQL
docker compose up db -d
```

- 前后端必须**同时运行**。前端 dev server 通过 `vite.config.js` 把 `/api` 与 `/uploads` 代理到后端。
- Swagger 在 `http://localhost:8000/docs`，开发期调接口很方便。
- 数据库连不上后端会**直接启动失败**，不会降级到 SQLite（PostgreSQL 是唯一路径）。
- **当前没有测试套件，也没有 linter。** 改动后请手工验证，最低限度：
  ```bash
  cd backend && ./venv/Scripts/python.exe -c "import main"   # 无输出即通过
  cd frontend && npm run build
  ```

## 后端架构 / Backend Architecture

```
backend/
├── main.py          # FastAPI app、全部 29 个路由、中间件（CORS / 日志 / 限流）、上传处理
├── models.py        # SQLAlchemy ORM: User, Topic, Comment, Notification, Message, Tag, likes, topic_tags
├── schemas.py       # Pydantic 请求/响应模型 + field_validator
├── crud.py          # 纯数据库操作（不掺 HTTP 逻辑）+ build_comment_tree()
├── auth.py          # bcrypt 哈希、JWT 签发/校验、get_current_user / get_optional_user / require_admin
├── database.py      # SQLAlchemy engine、SessionLocal、Base、ensure_schema()
├── migrations/      # 001_blog_to_forum.sql（历史一次性脚本，非日常迁移手段）
├── seed.py          # 幂等测试数据
├── uploads/avatars/ # 运行时创建的头像存储，经 /uploads 静态托管
└── requirements.txt
```

### 关键约定 / Key patterns

- 全部路由挂在 `/api/` 前缀下，**没有单独的管理端路径**。
- **`get_current_user`**：从 JWT 解析 User，所有需登录路由都用它（未登录 401）。
- **`get_optional_user`**：返回 User 或 None，用于"未登录也能看、但要算 `is_liked`"这类公开路由。
- **`require_admin`**：包一层 `get_current_user`，非管理员 403。仅管理员路由用它。
- **`get_db`**：每请求一个 SQLAlchemy session。
- **权限收口只有三处**：`_author_or_admin(topic, user)`、`_comment_author_or_admin(comment, user)`、`require_admin`。**加新端点时复用它们，不要新写 if 判断。**
- 内容经 `bleach` 白名单过滤，统一走 `sanitize()` helper，作用于帖子、评论、私信的写入。
- 限流用 `slowapi`：注册与改密 5/min；登录、发帖、评论、发私信、上传 10/min。
- 请求日志中间件记录方法、路径、状态码、耗时。
- 404 / 500 / 429 统一为 JSON 错误响应。
- 建评论前先校验帖子存在（不存在 404）；`parent_id` 必须属于同一 `topic_id`（不符则 `ValueError` → 400）。
- `users.topic_count` / `comment_count` 用 SQL 表达式原子增减（`User.topic_count + 1`）；递减用 `case()` 兜底不小于 0。
- 详情页访问时 `view_count` 自增。
- **路由声明顺序很关键**：`/api/messages/unread-count` 必须声明在 `/api/messages/{username}` **之前**，否则 FastAPI 会把 `unread-count` 当用户名匹配掉、返回 404。任何新增"字面量路径与路径参数并存"的路由都要注意同样的问题。
- 标签 slug 生成规则是 `name.lower().replace(" ", "-")`，`get_or_create_tags()` 按 slug 去重。

### API 端点 / API endpoints

| Method | Path | Auth | 说明 |
|--------|------|------|---------|
| GET | `/api/topics` | 否 | 帖子列表（`?page=&size=&q=&tag=`） |
| GET | `/api/topics/{id}` | 否 | 帖子详情 + 评论 + 点赞数 + `is_liked` + 标签 |
| GET | `/api/tags` | 否 | 全部标签及帖子数 |
| GET | `/api/users/{username}` | 否 | 用户主页 + TA 的帖子 |
| POST | `/api/auth/register` | 否 | 注册 |
| POST | `/api/auth/login` | 否 | 登录 → JWT |
| GET | `/api/auth/me` | 是 | 当前用户信息 |
| PUT | `/api/auth/me` | 是 | 更新 avatar / bio / github_url |
| PUT | `/api/auth/password` | 是 | 修改密码 |
| POST | `/api/upload/avatar` | 是 | 上传头像（≤2MB，校验图片魔术字节） |
| GET | `/api/topics/{id}/edit` | 是 | 取帖子用于编辑（作者或管理员） |
| POST | `/api/topics` | 是 | 发帖 |
| PUT | `/api/topics/{id}` | 是 | 编辑帖子（作者或管理员，否则 403） |
| DELETE | `/api/topics/{id}` | 是 | 删除帖子（作者或管理员，否则 403） |
| PUT | `/api/topics/{id}/pin` | 管理员 | 切换置顶 |
| PUT | `/api/topics/{id}/featured` | 管理员 | 切换加精 |
| POST | `/api/comments` | 是 | 发表评论（触发通知） |
| DELETE | `/api/comments/{id}` | 是 | 删除评论（作者或管理员） |
| POST | `/api/likes/{topic_id}` | 是 | 点赞（幂等） |
| DELETE | `/api/likes/{topic_id}` | 是 | 取消点赞 |
| GET | `/api/notifications` | 是 | 通知列表（`?page=&size=`） |
| GET | `/api/notifications/unread-count` | 是 | 未读通知数 |
| PUT | `/api/notifications/{id}/read` | 是 | 标记单条通知已读 |
| PUT | `/api/notifications/read-all` | 是 | 全部标记已读 |
| POST | `/api/messages` | 是 | 发私信 `{receiver, content}` |
| GET | `/api/messages` | 是 | 会话列表（含每会话未读数） |
| GET | `/api/messages/unread-count` | 是 | 未读私信总数 |
| GET | `/api/messages/{username}` | 是 | 与某用户的私信记录（**读取后自动标记已读**） |
| PUT | `/api/messages/{username}/read` | 是 | 标记与该用户的私信为已读 |

另有 `GET /` 返回服务标识。

## 前端架构 / Frontend Architecture

```
frontend/src/
├── App.vue           # 导航栏、主题切换、汉堡菜单、用户下拉、30s 未读轮询、全局组件挂载
├── main.js           # 应用启动：Pinia + Router
├── style.css         # 全局样式：约 60 条 CSS 变量声明，暖纸 / 深墨双主题
├── router/index.js   # 12 条路由，全部懒加载，beforeEach 认证守卫，scrollBehavior，afterEach 设标题
├── stores/auth.js    # Pinia：user、token、localStorage 持久化，登录后调 restoreUser()
├── api/
│   ├── client.js     # Axios 实例、请求头注入、401 处理 + auth-expired 事件
│   ├── auth.js       # register() / login() / getMe() / updateMe() / changePassword()
│   ├── topic.js      # 帖子 CRUD + pinTopic() + featureTopic()
│   ├── tag.js        # getTags()
│   ├── comment.js    # createComment(topicId, content, parentId?) / deleteComment()
│   ├── like.js       # likeTopic() / unlikeTopic()
│   ├── notification.js # getNotifications() / getUnreadCount() / markRead() / markAllRead()
│   ├── message.js    # sendMessage() / getConversations() / getMessages() / markMessagesRead() / getUnreadMessageCount()
│   ├── upload.js     # uploadAvatar(file)
│   └── user.js       # getUserProfile()
├── components/
│   ├── AppToast.vue       # 消息提示条（success/error/info），自动消失 + 滑入动画
│   ├── BackToTop.vue      # 回到顶部，滚动 >400px 出现，平滑滚动
│   ├── CommentItem.vue    # 递归楼中楼，内联回复表单与内联删除
│   ├── ConfirmDialog.vue  # 模态确认框，ESC / 点遮罩取消，Promise 化
│   └── TagInput.vue       # v-model 标签编辑器：回车/逗号添加、Backspace 删末尾、热门标签建议
├── composables/
│   ├── toast.js     # 模块级响应式状态，showToast.success/error/info()
│   └── confirm.js   # 模块级响应式状态，showConfirm(msg) → Promise<boolean>
└── views/
    ├── HomeView.vue         # 帖子列表、标签筛选栏、分页、全文搜索
    ├── TopicDetailView.vue  # Markdown 渲染、楼中楼评论、点赞、标签、置顶/加精操作
    ├── TopicEditView.vue    # Markdown 编辑（textarea + 实时预览）、标签输入、新建/编辑双模式
    ├── MessagesView.vue     # 统一收件箱：通知与私信按时间合并
    ├── ChatView.vue         # 私信会话，10s 轮询，Enter 发送
    ├── LoginView.vue        # 登录表单，支持 ?redirect=
    ├── RegisterView.vue     # 注册表单
    ├── UserProfile.vue      # 用户信息 + 统计 + TA 的帖子 + 「发私信」入口
    ├── ProfileEdit.vue      # 头像上传（blob 预览）、bio、github_url、改密码
    └── NotFoundView.vue     # 404
```

### 关键约定 / Key patterns

- **认证守卫**：`router.beforeEach` 在 `meta.requiresAuth` 且无 localStorage token 时**返回重定向对象**（Vue Router 4 写法，不是 `next()` 回调），并保留 `?redirect=`。
- **401 处理**：`api/client.js` 响应拦截器清 localStorage → 派发 `auth-expired` CustomEvent（App.vue 据此清 Pinia 状态并停轮询）→ 硬跳 `/login?redirect=...`。**登录/注册两个端点例外，不跳转**，否则用户看不到"密码错误"提示。
- **主题系统**：CSS 自定义属性，暖纸 / 深墨双色板。导航栏切换按钮持久化到 localStorage，首次访问跟随 `prefers-color-scheme`。切换写 `data-theme="dark"` 或 `""`。
- **轮询**：App.vue 每 30s 拉未读通知 + 未读私信，`watch(() => auth.user)` 启停 interval，`onBeforeUnmount` 清理（这里修过一个内存泄漏）。ChatView 每 10s 轮询当前会话，卸载时清理。
- **响应式**：≤640px 折叠为汉堡菜单，导航栏 sticky，点外部关闭。
- **加载与错误态**：HomeView / TopicDetailView / TopicEditView 有骨架屏；所有取数视图在失败时给重试按钮。
- **Toast / Confirm**：用模块级响应式状态（`composables/`），组件在 App.vue 挂载一次，任何视图直接 import `showToast` / `showConfirm`。
- **楼中楼**：`Comment.parent_id` 自引用外键，`build_comment_tree()` 把扁平列表转成嵌套字典，`CommentItem.vue` 递归渲染并缩进，用 `v-if="depth < 10"` 在 10 层处停止渲染。**前端没有"回复 @用户名"标签。**
- **搜索**：HomeView 全宽搜索框；后端 `or_(Topic.title.ilike(), Topic.content.ilike())`，并转义 `%` / `_` / `\`。
- **标签筛选**：HomeView 标签 chip 写 `?tag=<slug>`；后端用 `Topic.tags.any(Tag.slug == tag)` 过滤。
- **点赞**：`likes` 表（user_id + topic_id 复合主键）；`like_topic()` 吞掉 `IntegrityError` 实现幂等；`is_liked` 由服务端算。
- **通知**：发表评论时创建（通知帖子作者 + 被回复评论作者，排除自评与重复通知）。渲染在 MessagesView 的统一收件箱里，**不是独立页面**。
- **私信**：`send_message()` 拒绝给自己发或收件人不存在（返回 None → 400）。`get_conversations()` 用"按对方分组取最大消息 id"的相关子查询 + 独立的未读数子查询拼出会话列表。
- **Markdown**：`marked` 渲染，客户端再过一遍 `DOMPurify.sanitize()`；服务端写入时已用 `bleach` 过滤，所以库里存的是**已过滤的 Markdown 源码**（不是 HTML）。
- **分页**：参数用 snake_case（page、size），响应返回 items / total / page / size / pages。
- **页面标题**：`router.afterEach` 依据 route meta 设置 `document.title`，格式为 `"页面名 · Inkwell"`。

## 数据库 / Database

开发与生产都用 PostgreSQL。默认连接串 `postgresql://blog:blog@localhost:5432/blog`。

`ensure_schema()` 在启动时执行三件事：尝试 `GRANT CREATE ON SCHEMA public`（云数据库上会失败，只记 warning）→ `Base.metadata.create_all()` → 逐条执行 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` 补 `comments.parent_id`、`topics.is_pinned`、`topics.is_featured`。

**没有 Alembic**——schema 变更就是往那个 ALTER 列表里追加，且**只能加列，不能删列/改名/改类型**。

| 表 | 字段 |
|---|---|
| **users** | id, username, password_hash, avatar, bio, github_url, is_admin, topic_count, comment_count, created_at |
| **topics** | id, title, content, author_id (FK), view_count, is_pinned, is_featured, created_at, updated_at |
| **comments** | id, content, topic_id (FK), user_id (FK), parent_id (自引用 FK), created_at —— 索引 topic_id、parent_id |
| **likes** | user_id + topic_id（复合主键，用户与帖子的多对多） |
| **notifications** | id, user_id (FK, cascade), type, topic_id (FK, cascade), comment_id (FK, cascade), is_read, created_at —— 索引 (user_id, is_read) |
| **messages** | id, sender_id (FK), receiver_id (FK), content, is_read, created_at —— 索引 (sender_id, receiver_id) 与 (receiver_id, is_read) |
| **tags** | id, name (unique), slug (unique), created_at |
| **topic_tags** | topic_id + tag_id（复合主键） |

## 安全 / Security

- 密码用 **bcrypt 库**哈希（早期用 passlib，因版本不兼容换掉了）。
- JWT 走 python-jose，HS256，24h 过期。
- `SECRET_KEY` 取 `os.environ.get("SECRET_KEY") or "dev-only-change-me"` —— **生产必须设置**。
- HTML 过滤用 bleach（只放行白名单标签/属性），作用于帖子、评论、私信写入。
- `slowapi` 覆盖认证、写入、上传类端点。
- CORS origin 由 `CORS_ORIGIN` 环境变量控制，默认 `localhost:5173`。
- `get_current_user` 里把 JWT 的 `sub` 显式转成 `int`，避免类型不匹配。
- 通知的外键在数据库层 CASCADE 删除：删帖/删评论会自动清掉相关通知。
- 头像上传校验声明的 content-type、大小（≤2MB）与图片魔术字节，并以 UUID 重命名落盘。

## 已知缺陷 / Known issues

以下是当前代码树中**真实存在的缺陷**，不是设计取舍。**截至 2026-09-26 上一轮清点出的 P1–P3 缺陷均已修复**（见下方修复记录），本节目前没有未解决的条目。

> **2026-09-26 已修复的重要回归**：`backend/schemas.py` 曾缺 `Field` 导入（由 `6f521c6` 引入），导致 `import main` 抛 `NameError`、uvicorn 完全无法启动。已在导入行补上 `Field`，实测 `import main` 通过、`MessageCreate` 的长度校验生效。留此记录是因为它属于「给 Pydantic 模型加约束却忘了同步导入」的典型陷阱——加 `Field` / `conint` / `Annotated` 时记得检查导入行。

### 2026-09-26 修复记录

1. **头像上传 500（imghdr）**：`main.py` 原来调不存在的 `imghdr.from_buffer()`（`imghdr` 在 Python 3.13 已移除）。已改为模块级 `_detect_image_type()`，按魔术字节识别 jpeg/png/gif/webp，不再依赖 imghdr / Pillow / filetype。
2. **NotificationsView 死代码**：`views/NotificationsView.vue`（约 300 行，无路由无引用）已删除，`/notifications` 仍重定向到 `/messages`。
3. **`get_topics()` / `get_topics_by_user()` N+1**：原来每条帖子额外发 3 次查询。已抽 `_topic_stats()` 用 `GROUP BY` 聚合批量拿评论数、点赞数、最后评论时间，一页从 30+ 次往返降到固定 3 次。
4. **代码块高亮接线失效**：`marked` v5+ 移除了 `setOptions({highlight})`，原配置被静默忽略。已在 `TopicDetailView.vue` 改为 `marked.use({ renderer: { code({text, lang}) } })`，直接在 renderer 里跑 hljs 并输出带 `hljs language-*` class 的 `<pre><code>`。注：`TopicEditView` 的实时预览从未接 hljs，仍无高亮（历史行为，未改）。
5. **`@bytemd/*` 孤儿依赖**：`@bytemd/vue-next`、`@bytemd/plugin-gfm`、`@bytemd/plugin-highlight`（ByteMD 是博客时期编辑器的残留）已从 `package.json` 移除，`npm install` 实测卸载 115 个包、lockfile 已同步。
