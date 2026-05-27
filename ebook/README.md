# Forum 论坛系统 — 学习教程

> 从零到一，手把手带你理解 FastAPI + SQLAlchemy 全栈论坛后端

## 目录

| 章节 | 主题 | 文件 |
|------|------|------|
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

## 项目结构

```
forum-project/
├── backend/
│   ├── main.py         # 入口（路由、中间件）
│   ├── models.py       # 数据库表结构
│   ├── schemas.py      # 请求/响应数据格式
│   ├── crud.py         # 数据库操作
│   ├── auth.py         # 密码加密 + JWT
│   ├── database.py     # 数据库连接
│   ├── seed.py         # 测试数据
│   ├── Dockerfile      # 容器部署
│   └── migrations/     # 迁移记录
└── frontend/           # Vue 3 前端
```

## 后端代码量

| 文件 | 行数 | 职责 |
|------|------|------|
| main.py | ~260 | 路由、中间件、错误处理 |
| crud.py | ~215 | 数据库操作 |
| schemas.py | ~105 | Pydantic 模型 |
| models.py | ~65 | ORM 表定义 |
| auth.py | ~55 | 密码 + JWT |
| database.py | ~40 | 数据库连接 |
| seed.py | ~25 | 测试数据 |
| **总计** | **~770** | 完整论坛后端 |
