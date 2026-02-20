import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, ApiError } from '../../api/client';

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  vi.stubGlobal('fetch', mockFetch);
});

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('api.get', () => {
  it('returns parsed JSON on success', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));
    const result = await api.get<{ ok: boolean }>('/test');
    expect(result).toEqual({ ok: true });
    expect(mockFetch).toHaveBeenCalledWith(
      '/test',
      expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'application/json' }) })
    );
  });

  it('throws ApiError on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ detail: 'Not found' }, 404));
    await expect(api.get('/missing')).rejects.toThrow(ApiError);

    try {
      mockFetch.mockResolvedValueOnce(jsonResponse({ detail: 'Forbidden' }, 403));
      await api.get('/forbidden');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(403);
    }
  });
});

describe('api.post', () => {
  it('sends JSON body', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ id: 1 }));
    const result = await api.post<{ id: number }>('/items', { name: 'test' });
    expect(result).toEqual({ id: 1 });

    const [, init] = mockFetch.mock.calls[0];
    expect(init.method).toBe('POST');
    expect(init.body).toBe(JSON.stringify({ name: 'test' }));
  });

  it('sends without body when not provided', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));
    await api.post('/empty');
    const [, init] = mockFetch.mock.calls[0];
    expect(init.body).toBeUndefined();
  });

  it('includes credentials', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.post('/auth');
    const [, init] = mockFetch.mock.calls[0];
    expect(init.credentials).toBe('include');
  });
});

describe('ApiError', () => {
  it('stores status and detail', () => {
    const err = new ApiError(422, 'Validation failed');
    expect(err.name).toBe('ApiError');
    expect(err.status).toBe(422);
    expect(err.detail).toBe('Validation failed');
    expect(err.message).toBe('Validation failed');
  });

  it('stringifies non-string detail', () => {
    const err = new ApiError(500, { error: 'Internal' });
    expect(err.message).toBe('{"error":"Internal"}');
  });
});
