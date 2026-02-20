# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend/user

COPY frontend/user/package.json frontend/user/package-lock.json ./
RUN npm ci

COPY frontend/user/ ./
RUN npm run build


FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend/src \
    BACKEND_HOST=127.0.0.1 \
    BACKEND_PORT=8000 \
    NGINX_PORT=8080

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "fastapi>=0.115.0,<1.0.0" "uvicorn>=0.30.0,<1.0.0" "httpx>=0.27.0,<1.0.0"

COPY backend/src /app/backend/src
COPY --from=frontend-builder /app/frontend/user/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p /run/nginx

EXPOSE 8080

CMD ["/entrypoint.sh"]
