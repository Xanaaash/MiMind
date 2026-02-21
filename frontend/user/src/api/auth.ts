import { api } from './client';
import type { AuthSessionPayload, ReassessmentSchedulePayload, User } from '../types';

export function register(email: string, locale: string, policyVersion: string) {
  return api.post<{ user_id: string; triage?: unknown }>('/api/register', {
    email,
    locale,
    policy_version: policyVersion,
  });
}

export function authRegister(email: string, password: string, locale: string, policyVersion: string) {
  return api.post<AuthSessionPayload>('/api/auth/register', {
    email,
    password,
    locale,
    policy_version: policyVersion,
  });
}

export function authLogin(email: string, password: string) {
  return api.post<AuthSessionPayload>('/api/auth/login', { email, password });
}

export function authSession() {
  return api.get<AuthSessionPayload>('/api/auth/session');
}

export function authRefresh() {
  return api.post<AuthSessionPayload>('/api/auth/refresh');
}

export function authLogout() {
  return api.post<{ authenticated: boolean }>('/api/auth/logout');
}

export function requestPasswordReset(email: string) {
  return api.post<{ reset_requested: boolean }>('/api/auth/password/forgot', { email });
}

export function resetPassword(token: string, password: string) {
  return api.post<{ reset: boolean }>('/api/auth/password/reset', { token, password });
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

export function getReassessmentSchedule(userId: string) {
  return api.get<ReassessmentSchedulePayload>(`/api/reassessment/${userId}`);
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
