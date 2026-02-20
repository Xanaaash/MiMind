import { describe, it, expect, beforeEach } from 'vitest';
import { loadCoachHistory, saveCoachHistory, type CoachHistoryItem } from '../../utils/coachHistory';

const USER = 'test-user';

function makeItem(id: string): CoachHistoryItem {
  return { session_id: id, style_id: 'warm', summary: `Session ${id}`, ended_at: new Date().toISOString() };
}

describe('coachHistory', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns empty array for new user', () => {
    expect(loadCoachHistory(USER)).toEqual([]);
  });

  it('saves and loads a history item', () => {
    const item = makeItem('s-1');
    saveCoachHistory(USER, item);

    const loaded = loadCoachHistory(USER);
    expect(loaded).toHaveLength(1);
    expect(loaded[0].session_id).toBe('s-1');
  });

  it('deduplicates by session_id', () => {
    saveCoachHistory(USER, makeItem('s-1'));
    saveCoachHistory(USER, { ...makeItem('s-1'), summary: 'Updated' });

    const loaded = loadCoachHistory(USER);
    expect(loaded).toHaveLength(1);
    expect(loaded[0].summary).toBe('Updated');
  });

  it('newest item appears first', () => {
    saveCoachHistory(USER, makeItem('s-1'));
    saveCoachHistory(USER, makeItem('s-2'));

    const loaded = loadCoachHistory(USER);
    expect(loaded[0].session_id).toBe('s-2');
    expect(loaded[1].session_id).toBe('s-1');
  });

  it('caps at 30 items', () => {
    for (let i = 0; i < 35; i++) {
      saveCoachHistory(USER, makeItem(`s-${i}`));
    }
    expect(loadCoachHistory(USER)).toHaveLength(30);
  });

  it('handles corrupted localStorage gracefully', () => {
    localStorage.setItem(`mc_coach_history_${USER}`, '{invalid');
    expect(loadCoachHistory(USER)).toEqual([]);
  });

  it('filters out incomplete items', () => {
    localStorage.setItem(`mc_coach_history_${USER}`, JSON.stringify([
      { session_id: '', summary: 'x', ended_at: 'y' },
      makeItem('valid'),
    ]));
    const loaded = loadCoachHistory(USER);
    expect(loaded).toHaveLength(1);
    expect(loaded[0].session_id).toBe('valid');
  });
});
