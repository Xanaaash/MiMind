import { api } from './client';
import type { CoachSession, CoachChatResponse } from '../types';

export function startSession(userId: string, styleId: string, subscriptionActive: boolean) {
  return api.post<{ session: CoachSession; mode: string; coach_message: string }>(
    `/api/coach/${userId}/start`,
    { style_id: styleId, subscription_active: subscriptionActive },
  );
}

export function chat(sessionId: string, userMessage: string) {
  return api.post<CoachChatResponse>(`/api/coach/${sessionId}/chat`, {
    user_message: userMessage,
  });
}

export function endSession(sessionId: string) {
  return api.post<{ session: CoachSession; summary?: string }>(`/api/coach/${sessionId}/end`);
}
