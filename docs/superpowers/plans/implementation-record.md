# 改造实施记录

> 本文件原为 `2026-05-15-blog-to-forum.md` —— 一份 15 个 Task、含完整代码清单的逐步实施计划（2703 行）。改造早已完成，计划中的代码清单全部过期失效，继续保留只会误导。
>
> 现改写为**实施记录**：记录那次改造实际落地了什么、与原计划偏离在哪、以及此后系统又演进了哪些。当前系统设计见 `../specs/system-design.md`。

## 1. 改造前的起点

项目原本是个人技术博客（对应提交 `ab3ffc7` 之前）。数据模型为 `posts` / `comments` / `likes` / `tags` / `post_tags` / `users`，路由为 `/post/:slug` 与 `/admin/posts/*`，编辑器是 ByteMD（`b70cb49`，2026-05-13 引入）。

改造目标：**渐进改造**，把博客变成无版块扁平论坛，复用认证、主题、composable 等基础设施，保持项目随时可运行。

## 2. 原 15 个 Task 的实际落地

| Task | 内容 | 落地提交 | 结果 |
| --- | --- | --- | --- |
| 1 | 数据库迁移 SQL | `25368e1` → 修正 `154ed15` | ✅ `backend/migrations/001_blog_to_forum.sql` |
| 2 | `models.py`：Post→Topic，删 Tag，加 Notification | `8b8ef89` | ⚠️ 见偏差 A |
| 3 | `schemas.py` 适配 | `c25624e` | ✅ |
| 4 | `crud.py` 适配 + 通知 CRUD | `5ab5c2c` | ✅ |
| 5 | `main.py` 路由更新 | `5d844da` | ✅ |
| 6 | 前端 API 层 | `fc22501` | ✅ |
| 7–13 | 路由 / App.vue / HomeView / TopicDetailView / TopicEditView / NotificationsView / UserProfile | `6f2393a` | ⚠️ 见偏差 B、C |
| 14 | 清理旧文件 | `6f2393a` | ✅ 删除 AdminDashboard、AdminPostEdit、PostDetailView |
| 15 | 端到端验证 | `b33ef33` | ⚠️ 见偏差 D |

Task 7–13 本应逐个提交，实际合并为一个 `6f2393a "complete frontend conversion to forum"`（2026-05-16 00:05）。

## 3. 与原计划的偏差

### 偏差 A — 标签经历了一次完整的"删除再发明"

Task 2 的标题就是 `remove Tag`，设计文档第 2.7 节明确写着「`GET /api/tags` — 删除」。改造时确实照做了。

但 **12 天后（`b7beb27`，2026-05-28）标签系统被重新加了回来**，且是重新设计过的版本：`tags` 表带 `slug` 唯一索引、新增 `topic_tags` 关联表、前端新增 `TagInput.vue` 组件与首页标签筛选栏、新增 `GET /api/tags` 端点。

所以"删掉标签"是当时的真实决策，但只维持了 12 天。当前系统**有**标签功能。

### 偏差 B — ByteMD 编辑器被静默换掉，依赖成了孤儿

设计文档第 1 节写「编辑器：ByteMD（Markdown）」，第 3.3 节写「ByteMD 编辑器保留」。但 `6f2393a` 里新建的 `TopicEditView.vue` 用的是 `marked` + 实时预览，**完全没有 ByteMD**：

```javascript
// 6f2393a 的 TopicEditView.vue（至今未变）
import { marked } from "marked";
```

同时 `package.json` 没有被更新，于是 `@bytemd/vue-next`、`@bytemd/plugin-gfm`、`@bytemd/plugin-highlight` 以及 `highlight.js` 四个依赖留在了清单里，`src/` 中零引用。这属于改造时漏做的收尾。

### 偏差 C — NotificationsView 先建后废

Task 12 专门新建了 `NotificationsView.vue`。它确实上线过，但 15 天后（`6ae6ea4`，2026-05-31）通知与私信合并为统一收件箱 `/messages`，`/notifications` 变成重定向，该视图失去路由——文件却一直没删，至今仍留在 `views/` 中。

### 偏差 D — 验证环节无痕迹

Task 15 要求端到端验证，但没有任何自动化测试留下，后续提交 `b33ef33` 只是更新了文档。至今项目仍无测试与 linter。

## 4. 计划完成后的演进

按时间顺序，改造（2026-05-16 完成）之后系统经历的实际迭代：

### 2026-05-16 ~ 05-27 · 文档期

| 提交 | 内容 |
| --- | --- |
| `b33ef33` | 更新 README / CLAUDE.md（该文件后更名为 `AGENTS.md`）为论坛状态 |
| `8d1408f` | 新增 `ebook/` 后端篇教程 |
| `c274574` | 新增 `ebook/` 前端篇教程 |

### 2026-05-28 · 三个新功能

| 提交 | 内容 |
| --- | --- |
| `8601029` | 头像上传（`/api/upload/avatar` + `uploads/` 静态托管） |
| `0075575` | Vite 补 `/uploads` 代理，否则头像预览 404 |
| `b7beb27` | **标签系统回归**（见偏差 A） |
| `0325cef` | 管理员置顶 / 加精（`is_pinned` / `is_featured`） |

置顶/加精同样与原计划相悖——设计文档第 1 节写的是「帖子管理：基础管理（**无置顶**/锁定/公告）」。

### 2026-05-31 · 私信系统与统一收件箱

| 提交 | 内容 |
| --- | --- |
| `67842c3` | 私信系统（`Message` 模型 + 5 个端点 + `ChatView`） |
| `098202a` | 修 JSON 序列化：ORM 对象需转 dict |
| `6ae6ea4` | 通知与私信合并为统一收件箱（`MessagesView`） |
| `5e6bc24` | 消息入口图标改为文字标签 |
| `578bef2` | 从用户下拉菜单移除冗余的消息链接 |

### 2026-06-12 · 代码审查修复

`a0c9029` 一次性修复安全、缺陷与性能问题（XSS、SECRET_KEY、分页、数据一致性等）。

### 2026-06-19 · UI 重构与收尾

| 提交 | 内容 |
| --- | --- |
| `802d8f5` | 前端 UI 重构为"编辑杂志风格"（暖纸 / 深墨双色板） |
| `a238e5e` | 加 GitHub Actions CI/CD |
| `6dd4147` | 撤销上面的 UI 重构 |
| `fccdb87` | 重新应用 UI 重构 |
| `6589241` | 修复 UI 重构的审查问题 |
| `139f5f5` | 移除 GitHub Actions 工作流 |
| `6f521c6` | 修复前后端多个 bug（分页 / 401 拦截 / 内存泄漏 / XSS / SECRET_KEY / 数据一致性 / 校验） |

`6dd4147` → `fccdb87` 是一次 revert 后立即 reapply，最终状态以 `fccdb87` 为准。CI 工作流加上后又在同一天被移除（`139f5f5`），所以仓库当前**没有** CI。

### 之后的本地改动

工作区曾有一处未提交改动：在 `database.py` 中加入「PostgreSQL 连不上则自动降级 SQLite」的逻辑。该改动已被还原，`database.py` 与仓库 HEAD 保持一致，**当前项目只有 PostgreSQL 一条路径**。

## 5. 与设计文档的最终差异

| 设计文档的原始决策 | 当前实际 |
| --- | --- |
| 标签表删除、`GET /api/tags` 删除 | 标签功能完整存在，见偏差 A |
| 编辑器用 ByteMD | textarea + marked + DOMPurify，ByteMD 依赖为孤儿 |
| 帖子管理无置顶 | 管理员可置顶 + 加精 |
| 无版块、无用户间私信 | 新增完整私信系统与统一收件箱 |
| — | 新增头像上传 |
| — | 新增 `NotificationsView` 后又废弃 |
| 计划加 CI/CD | CI 加上当天移除，当前无 CI |

## 6. 当前遗留问题

完整清单见 `../specs/system-design.md` 第 7 节，其中影响最大的三项：

1. **头像上传端点必然 500** —— 调用了不存在的 `imghdr.from_buffer()`，该功能从 `8601029` 引入起就没跑通过
2. **`crud.get_topics()` 的 N+1 查询** —— 每页 10 条会额外发 30+ 次查询
3. **`NotificationsView.vue` 死代码** —— 偏差 C 的残留

另有两项与本次改造直接相关的收尾欠账：`package.json` 中未使用的 ByteMD / highlight.js 依赖（偏差 B），以及完全没有测试与 linter（偏差 D）。
