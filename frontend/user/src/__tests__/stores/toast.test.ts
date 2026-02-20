import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useToastStore, toast } from '../../stores/toast';

describe('useToastStore', () => {
  beforeEach(() => {
    useToastStore.setState({ toasts: [] });
    vi.useFakeTimers();
  });

  it('add creates a toast with correct type and message', () => {
    useToastStore.getState().add('success', 'Done!');
    const toasts = useToastStore.getState().toasts;
    expect(toasts).toHaveLength(1);
    expect(toasts[0].type).toBe('success');
    expect(toasts[0].message).toBe('Done!');
  });

  it('auto-dismisses after duration', () => {
    useToastStore.getState().add('error', 'Oops', 1000);
    expect(useToastStore.getState().toasts).toHaveLength(1);

    vi.advanceTimersByTime(1000);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it('dismiss removes a specific toast', () => {
    useToastStore.getState().add('warning', 'A', 0);
    useToastStore.getState().add('success', 'B', 0);

    const idToRemove = useToastStore.getState().toasts[0].id;
    useToastStore.getState().dismiss(idToRemove);

    const remaining = useToastStore.getState().toasts;
    expect(remaining).toHaveLength(1);
    expect(remaining[0].message).toBe('B');
  });
});

describe('toast helpers', () => {
  beforeEach(() => {
    useToastStore.setState({ toasts: [] });
    vi.useFakeTimers();
  });

  it('toast.success creates a success toast', () => {
    toast.success('Yay');
    expect(useToastStore.getState().toasts[0].type).toBe('success');
  });

  it('toast.error creates an error toast', () => {
    toast.error('Nope');
    expect(useToastStore.getState().toasts[0].type).toBe('error');
  });

  it('toast.warning creates a warning toast', () => {
    toast.warning('Careful');
    expect(useToastStore.getState().toasts[0].type).toBe('warning');
  });
});
