# Forum 论坛系统 — 学习教程

> 从零到一，手把手带你理解 FastAPI + Vue 3 全栈论坛

## 目录

### 后端篇

| 章节 | 主题 | 文件 |
|:----:|------|------|
| 01 | 项目初始化 — 搭建骨架 | [ch01-项目初始化.md](ch01-项目初始化.md) |
| 02 | 数据库设计 — models.py | [ch02-数据库设计.md](ch02-数据库设计.md) |
| 03 | 数据校验 — schemas.py | [ch03-数据校验.md](ch03-数据校验.md) |
| 04 | 数据库操作层 — crud.py | [ch04-数据库操作.md](ch04-数据库操作.md) |
| 05 | 认证系统 — auth.py | [ch05-认证系统.md](ch05-认证系统.md) |
| 06 | 路由和中间件 — main.py | [ch06-路由与中间件.md](ch06-路由与中间件.md) |
| 07 | 测试数据填充 — seed.py | [ch07-测试数据.md](ch07-测试数据.md) |
| 08 | 数据库迁移 — migrations | [ch08-数据库迁移.md](ch08-数据库迁移.md) |
| 09 | Docker 部署 | [ch09-Docker部署.md](ch09-Docker部署.md) |
| 10 | 前端如何调用 API | [ch10-前后端对接.md](ch10-前后端对接.md) |
| 11 | 完整开发流程总结 | [ch11-总结.md](ch11-总结.md) |

### 前端篇

| 章节 | 主题 | 文件 |
|:----:|------|------|
| 12 | 前端项目概览 — 入口与架构 | [ch12-前端项目概览.md](ch12-前端项目概览.md) |
| 13 | 路由与认证状态 | [ch13-路由与认证状态.md](ch13-路由与认证状态.md) |
| 14 | 全局组件与 Composable 模式 | [ch14-全局组件与Composable模式.md](ch14-全局组件与Composable模式.md) |
| 15 | 核心视图详解 | [ch15-核心视图详解.md](ch15-核心视图详解.md) |
| 16 | 认证与用户页面 | [ch16-认证与用户页面.md](ch16-认证与用户页面.md) |
| 17 | 评论与通知系统 | [ch17-评论与通知系统.md](ch17-评论与通知系统.md) |

## 项目结构

```
forum-project/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 入口（路由、中间件、错误处理）
│   ├── models.py               # 数据库表结构
│   ├── schemas.py              # 请求/响应数据格式
│   ├── crud.py                 # 数据库操作
│   ├── auth.py                 # 密码加密 + JWT
│   ├── database.py             # 数据库连接
│   ├── seed.py                 # 测试数据
│   ├── Dockerfile              # 容器部署
│   └── migrations/             # 迁移记录
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── main.js             # 应用入口
│       ├── App.vue             # 根组件（导航栏、全局组件）
│       ├── style.css           # 样式 + 主题变量
│       ├── router/index.js     # 10 条路由 + 导航守卫
│       ├── stores/auth.js      # Pinia 认证状态
│       ├── api/                # Axios API 调用层
│       ├── components/         # 全局组件
│       ├── composables/        # 可复用逻辑
│       └── views/              # 页面组件
└── ebook/                      # ← 本教程
```

## 代码量统计

| 后端 | 行数 | 前端 | 行数 |
|:-----|:---:|:-----|:---:|
| main.py | ~260 | 视图 (9个) | ~1,592 |
| crud.py | ~215 | App.vue | ~390 |
| schemas.py | ~105 | 组件 (4个) | ~398 |
| models.py | ~65 | router + store | ~138 |
| auth.py | ~55 | api (7个) | ~126 |
| database.py | ~40 | composables (2个) | ~46 |
| seed.py | ~25 | main.js + style.css | ~101 |
| **后端总计** | **~770** | **前端总计** | **~2,791** |
