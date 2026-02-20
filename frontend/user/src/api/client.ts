const API_BASE = import.meta.env.VITE_API_BASE ?? '';

class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    const msg = typeof detail === 'string' ? detail : JSON.stringify(detail);
    super(msg);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const init: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  };

  const response = await fetch(url, init);
  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(response.status, body.detail ?? body.error ?? 'Request failed');
  }

  return body as T;
}

export const api = {
  get<T>(path: string) {
    return request<T>(path);
  },
  post<T>(path: string, body?: unknown) {
    return request<T>(path, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  },
};

export { ApiError };
