# 第九章：Docker 部署

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 分层构建：利用 Docker 缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

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

## 搭配 docker-compose

```yaml
# docker-compose.yml（项目根目录）
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: blog
      POSTGRES_USER: blog
      POSTGRES_PASSWORD: blog

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://blog:blog@db:5432/blog
      SECRET_KEY: your-production-secret-key
    depends_on:
      - db
```

## 开发时单独启动数据库

```bash
docker compose up db -d       # 只启动 PostgreSQL
uvicorn main:app --reload     # 本地运行后端
```
