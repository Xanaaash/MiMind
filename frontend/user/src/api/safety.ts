import { api } from './client';

export function assessMessage(userId: string, text: string) {
  return api.post<{ level: string; reasons: string[] }>(`/api/safety/${userId}/assess`, { text });
}

export function getHotlineCache() {
  return api.get<{ hotlines: Array<{ label: string; number: string; region: string }> }>('/api/safety/hotline-cache');
}
