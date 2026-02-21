# MiMind 生产部署指南

## 1. 部署目标

当前仓库提供两种部署方式：

1. 单容器部署（`Dockerfile`）：`FastAPI + Nginx + 前端静态资源`
2. Compose 部署（`docker-compose.yml`）：`app + db` 一键启动

> 说明：当前后端默认使用 SQLite（`MIMIND_DB_PATH`），Compose 中的 PostgreSQL 服务为后续数据库迁移任务预留。

---

## 2. 前置条件

- Docker 24+
- Docker Compose v2
- 可用的 `.env` 文件（从 `.env.example` 复制）

```bash
cp .env.example .env
```

生产至少要修改：

- `ADMIN_PASSWORD`
- `AUTH_JWT_SECRET`
- `MIMIND_DATA_ENCRYPTION_KEY`

若模型 provider 使用 `openai`，还需设置：

- `OPENAI_API_KEY`

若支付 provider 使用 `stripe`，还需设置：

- `BILLING_PROVIDER=stripe`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID_BASE`
- `STRIPE_PRICE_ID_COACH`
- `STRIPE_CHECKOUT_SUCCESS_URL`
- `STRIPE_CHECKOUT_CANCEL_URL`

若支付 provider 使用 `domestic`（支付宝/微信），还需设置：

- `BILLING_PROVIDER=domestic`
- `ALIPAY_GATEWAY_URL`
- `ALIPAY_NOTIFY_SECRET`
- `WECHAT_PAY_GATEWAY_URL`
- `WECHAT_PAY_NOTIFY_SECRET`

---

## 3. 方式 A：单容器部署

### 3.1 构建镜像

```bash
docker build -t mimind:latest .
```

### 3.2 启动容器

```bash
docker run -d \
  --name mimind \
  --env-file .env \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  mimind:latest
```

### 3.3 验证

```bash
curl http://127.0.0.1:8080/healthz
```

---

## 4. 方式 B：Compose 一键启动

### 4.1 启动

```bash
docker compose up -d --build
```

### 4.2 查看状态

```bash
docker compose ps
docker compose logs -f app
```

### 4.3 关闭

```bash
docker compose down
```

---

## 5. 升级与回滚

### 升级

```bash
git pull
docker compose up -d --build
```

### 回滚

```bash
git checkout <previous-tag-or-commit>
docker compose up -d --build
```

---

## 6. 生产建议

- 在公网前加一层反向代理（Nginx/Traefik）并开启 HTTPS
- 将 `.env` 放在受控目录，不要提交到仓库
- 定期备份 `data/`（SQLite 文件）及数据库卷
- 若开启 `AUTH_COOKIE_SECURE=true`，请确保外层 HTTPS 正常

---

## 7. 常见问题

### Q1: 容器启动后页面空白

- 检查 `docker logs mimind` 或 `docker compose logs app`
- 确认 `frontend/user/dist` 已在镜像构建阶段成功生成

### Q2: `/api/*` 请求失败

- 检查 `app` 容器内 `uvicorn` 是否启动
- 检查 Nginx 反代配置：`docker/nginx.conf`

### Q3: 登录态 Cookie 不生效

- 开发环境建议 `AUTH_COOKIE_SECURE=false`
- 生产环境走 HTTPS 并设置 `AUTH_COOKIE_SECURE=true`
