# 第九章：Docker 部署

前面八章把后端跑在了本地。这一章讲怎么把它和前端、数据库一起打包，用一条命令部署到服务器。

## 后端 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`--host 0.0.0.0` 很关键：容器内的服务必须绑定到 `0.0.0.0` 才能被容器外部访问，绑 `127.0.0.1` 的话只有容器自己连得上。

## 层缓存技巧

```dockerfile
# ❌ 不推荐：源码和依赖一起复制，改源码也重装依赖
COPY . .
RUN pip install -r requirements.txt

# ✅ 推荐：分层复制
COPY requirements.txt .          # 依赖文件很少改
RUN pip install -r requirements.txt  # 缓存这一层
COPY . .                         # 源码经常改，只影响这一层
```

`requirements.txt` 很少改，但源码频繁变更。分层复制让 Docker 缓存住"安装依赖"那一层，下次构建跳过下载，加速数倍。

## docker-compose.yml — 三服务编排

项目根目录的 `docker-compose.yml` 定义了三个服务：

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=blog
      - POSTGRES_PASSWORD=${DB_PASSWORD:-change-me}
      - POSTGRES_DB=blog
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U blog"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    restart: unless-stopped
    environment:
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - CORS_ORIGIN=${CORS_ORIGIN:-http://localhost}
      - DATABASE_URL=postgresql://blog:${DB_PASSWORD:-change-me}@db:5432/blog
    volumes:
      - ./backend/uploads:/app/uploads
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  data:
  db-data:
```

### db 服务 — 数据库 + 健康检查

- **`postgres:16-alpine`** — alpine 版本体积小，适合生产
- **`restart: unless-stopped`** — 容器异常退出自动重启（除非是人为停的）
- **数据持久化**：把容器里的 `/var/lib/postgresql/data` 挂到命名卷 `db-data` 上。**没有这个挂载，容器一重建数据就全没了**
- **healthcheck** — 关键设计。用 `pg_isready -U blog` 探测数据库是否真的**可以接受连接**，每 5 秒一次、最多重试 5 次

### backend 服务 — 依赖健康检查

```yaml
depends_on:
  db:
    condition: service_healthy
```

这行是整份编排里最重要的细节。普通写法是：

```yaml
depends_on:
  - db      # ❌ 只保证"容器启动了"
```

`depends_on` 的简单形式只保证**容器进程启动了**，但 PostgreSQL 从"进程启动"到"能接受连接"中间有好几秒（初始化数据目录、预热）。如果后端这时就去连，会连不上、启动失败、然后被 `restart` 拉起、再失败……陷入重启循环。

加上 `condition: service_healthy` 后，Docker 会**等 healthcheck 通过**才启动 backend。后端的 `ensure_schema()`（第二章）依赖数据库可连接，所以这层等待是必须的。

- **环境变量**：`SECRET_KEY`、`CORS_ORIGIN`、`DATABASE_URL` 三个都从宿主的 `.env` 读取，用 `${VAR:-默认值}` 提供兜底。注意 `DATABASE_URL` 的主机名是 **`db`**——在 compose 网络里，各服务用**服务名当主机名**互相访问，不是 `localhost`
- **挂载上传目录**：`./backend/uploads:/app/uploads` 把宿主的目录挂进容器。**为什么不用命名卷？** 因为 `uploads/` 在宿主上是真实目录，备份/迁移时直接拷贝文件夹就行，比操作 Docker 卷直观。**没有这个挂载，容器重建时用户上传的头像全丢**

### frontend 服务 — 只暴露它

```yaml
ports:
  - "80:80"
```

整份编排里**只有 frontend 映射了端口**。backend 和 db 都只在内部网络可见——这是更安全的做法：外部只能访问 80 端口的 nginx，再由 nginx 反代到 backend。数据库和 API 都不直接暴露在公网。

## 前端镜像 — 多阶段构建

```dockerfile
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**多阶段构建**是这里的关键：第一个阶段用 Node 把 Vue 源码编译成静态文件（`dist/`），第二个阶段只把 `dist/` 拷进 nginx 镜像。

结果是**最终镜像里没有 node_modules，也没有 Node 运行时**——只有 nginx 和一堆静态文件，体积从几百 MB 降到几十 MB。构建工具只在"造零件"时用，交付的成品不需要它们。

## nginx.conf — 静态托管 + 反向代理

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # API proxy to backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Uploads proxy to backend
    location /uploads/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    # Vue Router SPA - fallback to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gzip
    gzip on;
    gzip_types text/css application/javascript text/javascript image/svg+xml;
    gzip_vary on;
}
```

四块职责，逐一看：

1. **`/api/` 反代到 backend** —— 前端发起的 `/api/...` 请求转发给 `http://backend:8000`。和 compose 里一样，用**服务名 `backend`** 当主机名。这一层让生产环境和开发环境的前端代码完全一致：开发时 Vite 代理转发，生产时 nginx 转发，前端都只写 `baseURL: "/api"`
2. **`/uploads/` 反代到 backend** —— 头像图片交给后端（后端的 `StaticFiles` 挂在 `/uploads`）。同样保持了开发/生产一致
3. **SPA 回退** —— `try_files $uri $uri/ /index.html`。Vue Router 用的 history 模式，访问 `/topic/5` 时服务器上并没有这个文件。这行的意思是"先找文件、再找目录、都没有就返回 `index.html`"，让前端路由自己解析 URL。**没有这行，用户刷新页面或直接访问子路由就会 404**
4. **gzip 压缩** —— 对 CSS/JS/SVG 开启压缩传输，减小带宽

## 环境变量：四个变量撑起整份配置

| 变量 | 用在何处 | 打包进部署脚本的默认值来源 |
|------|---------|--------------------------|
| `SECRET_KEY` | backend（JWT 签名，第五章） | `openssl rand -hex 32` |
| `CORS_ORIGIN` | backend（跨域允许来源） | `http://localhost` |
| `DATABASE_URL` | backend（数据库连接） | 由 `DB_PASSWORD` 拼出 |
| `DB_PASSWORD` | db 与 backend 共用 | `openssl rand -hex 16` |

`.env.example` 是这四个变量的模板，把文件复制成 `.env` 填上真实值即可。

## deploy.sh — 一键部署

```bash
#!/bin/bash
# Blog project deployment script
# Usage: ./deploy.sh

set -e

echo "Deploying Blog Project..."

# Generate random passwords if not set
if [ ! -f .env ]; then
    echo "Creating .env..."
    cat > .env <<EOF
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGIN=http://localhost
DB_PASSWORD=$(openssl rand -hex 16)
EOF
    echo ".env created with random secrets."
fi

# Pull latest code
git pull origin main

# Build and start
docker compose up -d --build

# Wait for backend to be ready
echo "Waiting for backend..."
sleep 5

# Run seed data
docker compose exec -T backend python seed.py

echo ""
echo "Deployed!"
echo ""
echo "Default login: admin / admin123"
echo "Change password immediately: 右上角用户名 → 编辑资料 → 修改密码"
```

逐段解读：

- **`set -e`** —— 任何一条命令失败就立即退出脚本。部署脚本里绝不能"这步失败了还继续往下跑"
- **首次部署自动生成密钥** —— 如果 `.env` 不存在，用 `openssl rand -hex 32` 生成 32 字节随机 `SECRET_KEY`、`openssl rand -hex 16` 生成数据库密码。**这就是"绝不硬编码密钥"的落地方式**（呼应第五章）：开发机上的默认值只是占位符，真实部署的密钥是现场随机的
- **`git pull origin main`** —— 拉取最新代码
- **`docker compose up -d --build`** —— `-d` 后台运行，`--build` 强制重新构建镜像（否则会复用旧镜像，改了代码不生效）
- **`sleep 5` 后执行 seed** —— 等 backend 起来，再用 `docker compose exec -T backend python seed.py` 初始化数据。`-T` 表示不分配伪终端（脚本环境没有 tty，不加会报错）。因为 `seed.py` 是幂等的（第七章），**每次部署都跑一遍是安全的**——有新库就填充、已有数据就跳过
- **结尾打印默认账号并提醒改密码** —— 一个小而重要的细节，避免管理员账号一直用着 `admin123`

这条 `deploy.sh` 串起了前面所有章节的成果：第五章的"密钥不硬编码"、第七章的"seed 幂等"、第二章的"启动自动建表"，都在这几十行里各就各位。

## 开发时单独启动数据库

本地开发通常不想跑整个 stack（只要数据库）。一个很实用的做法：

```bash
docker compose up db -d       # 只启动 PostgreSQL（-d 后台）
```

然后本地直接跑后端：

```bash
cd backend
uvicorn main:app --reload
```

这样改代码即时生效（`--reload`），而数据库又不用在宿主机上装。注意本地跑时 `DATABASE_URL` 默认就是 `postgresql://blog:blog@localhost:5432/blog`——但 compose 里 db 的密码是 `${DB_PASSWORD}`，所以要么在 `.env` 里把 `DB_PASSWORD` 设成 `blog`，要么改一下 `DATABASE_URL`，两边得对上。

## 本章要点

- 三服务编排：`db`（postgres:16-alpine + `pg_isready` 健康检查）、`backend`（等 db 健康后才启动、挂载 uploads）、`frontend`（nginx，唯一对外的 80 端口）
- `depends_on: condition: service_healthy` 才是"等数据库真的能连"，普通 `depends_on` 只等进程启动，会导致后端重启循环
- 前端镜像用 node:24-alpine 多阶段构建到 nginx:alpine，成品不含 Node 与 node_modules
- nginx 负责四件事：`/api` 反代、`/uploads` 反代、SPA 回退（`try_files ... /index.html`）、gzip
- `deploy.sh`：无 `.env` 时用 openssl 生成随机密钥 → `git pull` → `compose up -d --build` → `exec` 跑幂等的 seed
- 数据库数据（`db-data` 卷）和用户上传（`./backend/uploads`）都必须持久化，否则重建容器即丢失
