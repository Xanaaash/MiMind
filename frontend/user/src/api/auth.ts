import { api } from './client';
import type { User } from '../types';

export function register(email: string, locale: string, policyVersion: string) {
  return api.post<{ user_id: string; triage?: unknown }>('/api/register', {
    email,
    locale,
    policy_version: policyVersion,
  });
}

export function submitAssessment(userId: string, responses: Record<string, unknown>) {
  return api.post<{ scores: unknown; triage: unknown; schedule: unknown }>(
    `/api/assessment/${userId}`,
    { responses },
  );
}

export function getEntitlements(userId: string) {
  return api.get<{ channel: string; entitlements: unknown }>(`/api/entitlements/${userId}`);
}

export function adminLogin(username: string, password: string) {
  return api.post<{ ok: boolean }>('/api/admin/login', { username, password });
}

export function adminLogout() {
  return api.post<{ ok: boolean }>('/api/admin/logout');
}

export function adminSession() {
  return api.get<{ authenticated: boolean; username?: string; auth_config?: unknown }>('/api/admin/session');
}

export type { User };
