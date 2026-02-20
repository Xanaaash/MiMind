import { describe, it, expect, beforeEach } from 'vitest';
import { useCoachStore } from '../../stores/coach';

const INITIAL = {
  sessionId: null,
  styleId: null,
  messages: [],
  isActive: false,
  isLoading: false,
  halted: false,
};

describe('useCoachStore', () => {
  beforeEach(() => {
    useCoachStore.setState(INITIAL);
  });

  it('starts idle with no session', () => {
    const s = useCoachStore.getState();
    expect(s.isActive).toBe(false);
    expect(s.messages).toHaveLength(0);
  });

  it('setSession activates and clears messages', () => {
    useCoachStore.getState().addMessage('user', 'stale');
    useCoachStore.getState().setSession('s-1', 'warm');

    const s = useCoachStore.getState();
    expect(s.sessionId).toBe('s-1');
    expect(s.styleId).toBe('warm');
    expect(s.isActive).toBe(true);
    expect(s.messages).toHaveLength(0);
  });

  it('addMessage appends and returns index', () => {
    const idx0 = useCoachStore.getState().addMessage('user', 'Hi');
    const idx1 = useCoachStore.getState().addMessage('coach', 'Hello');

    expect(idx0).toBe(0);
    expect(idx1).toBe(1);
    expect(useCoachStore.getState().messages).toHaveLength(2);
    expect(useCoachStore.getState().messages[0].content).toBe('Hi');
    expect(useCoachStore.getState().messages[1].role).toBe('coach');
  });

  it('updateMessage modifies content at index', () => {
    useCoachStore.getState().addMessage('coach', 'Hel');
    useCoachStore.getState().updateMessage(0, 'Hello!');
    expect(useCoachStore.getState().messages[0].content).toBe('Hello!');
  });

  it('setHalted deactivates session', () => {
    useCoachStore.getState().setSession('s-2', 'rational');
    useCoachStore.getState().setHalted(true);

    const s = useCoachStore.getState();
    expect(s.halted).toBe(true);
    expect(s.isActive).toBe(false);
  });

  it('endSession deactivates but keeps messages', () => {
    useCoachStore.getState().setSession('s-3', 'deep');
    useCoachStore.getState().addMessage('user', 'Bye');
    useCoachStore.getState().endSession();

    const s = useCoachStore.getState();
    expect(s.isActive).toBe(false);
    expect(s.sessionId).toBeNull();
    expect(s.messages).toHaveLength(1);
  });

  it('reset clears everything', () => {
    useCoachStore.getState().setSession('s-4', 'mindful');
    useCoachStore.getState().addMessage('user', 'Test');
    useCoachStore.getState().reset();

    expect(useCoachStore.getState()).toMatchObject(INITIAL);
  });
});
