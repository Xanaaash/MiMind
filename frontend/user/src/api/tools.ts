import { api } from './client';
import type { AudioTrack, MeditationItem, JournalEntry, JournalTrend, ToolUsageStats } from '../types';

export function getAudioLibrary() {
  return api.get<Record<string, { name: string; category: string; duration_seconds: number }>>('/api/tools/audio/library');
}

export function startAudio(userId: string, trackId: string, minutes: number) {
  return api.post(`/api/tools/audio/${userId}/start`, { track_id: trackId, minutes });
}

export function completeBreathing(userId: string, cycles: number) {
  return api.post(`/api/tools/breathing/${userId}/complete`, { cycles });
}

export function getMeditationLibrary() {
  return api.get<Record<string, { name: string; category: string; duration_seconds: number }>>('/api/tools/meditation/library');
}

export function startMeditation(userId: string, meditationId: string) {
  return api.post(`/api/tools/meditation/${userId}/start`, { meditation_id: meditationId });
}

export function createJournalEntry(userId: string, mood: string, energy: number, note: string) {
  return api.post<JournalEntry>(`/api/tools/journal/${userId}/entries`, { mood, energy, note });
}

export function getJournalEntries(userId: string) {
  return api.get<JournalEntry[]>(`/api/tools/journal/${userId}/entries`);
}

export function getJournalTrend(userId: string, days = 7) {
  return api.get<JournalTrend>(`/api/tools/journal/${userId}/trend?days=${days}`);
}

export function getToolUsageStats(userId: string) {
  return api.get<ToolUsageStats>(`/api/tools/${userId}/stats`);
}

export type { AudioTrack, MeditationItem };
