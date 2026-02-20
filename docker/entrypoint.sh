#!/bin/sh
set -eu

backend_host="${BACKEND_HOST:-127.0.0.1}"
backend_port="${BACKEND_PORT:-8000}"

uvicorn app:app --app-dir /app/backend/src --host "${backend_host}" --port "${backend_port}" &
backend_pid=$!

nginx -g "daemon off;" &
nginx_pid=$!

cleanup() {
  kill "${backend_pid}" "${nginx_pid}" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

while true; do
  if ! kill -0 "${backend_pid}" 2>/dev/null; then
    wait "${backend_pid}" || true
    exit 1
  fi
  if ! kill -0 "${nginx_pid}" 2>/dev/null; then
    wait "${nginx_pid}" || true
    exit 1
  fi
  sleep 1
done
