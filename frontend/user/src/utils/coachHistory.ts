export interface CoachHistoryItem {
  session_id: string;
  style_id: string;
  summary: string;
  ended_at: string;
}

const MAX_HISTORY_ITEMS = 30;

function keyForUser(userId: string): string {
  return `mc_coach_history_${userId}`;
}

export function loadCoachHistory(userId: string): CoachHistoryItem[] {
  const raw = localStorage.getItem(keyForUser(userId));
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw) as CoachHistoryItem[];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item) => Boolean(item.session_id && item.summary && item.ended_at));
  } catch {
    return [];
  }
}

export function saveCoachHistory(userId: string, item: CoachHistoryItem): void {
  const current = loadCoachHistory(userId);
  const deduplicated = current.filter((existing) => existing.session_id !== item.session_id);
  const next = [item, ...deduplicated].slice(0, MAX_HISTORY_ITEMS);
  localStorage.setItem(keyForUser(userId), JSON.stringify(next));
}
