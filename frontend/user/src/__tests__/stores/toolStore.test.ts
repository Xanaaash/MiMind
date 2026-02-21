import { beforeEach, describe, expect, it } from 'vitest';
import { useToolStore } from '../../stores/useToolStore';

describe('useToolStore', () => {
  beforeEach(() => {
    localStorage.removeItem('mc_tool_store');
    useToolStore.getState().resetTools();
  });

  it('starts with required T-701 contract fields', () => {
    const state = useToolStore.getState();
    expect(state.ui.isRightSidebarOpen).toBe(false);
    expect(state.ui.activePanel).toBe('pomodoro');
    expect(state.pomodoro.mode).toBe('idle');
    expect(state.pomodoro.isRunning).toBe(false);
    expect(state.pomodoro.remainingSec).toBe(0);
    expect(state.pomodoro.preset.workMin).toBe(25);
    expect(state.ambient.activeSoundIds).toEqual([]);
    expect(state.ambient.isPlaying).toBe(false);
    expect(state.ambient.timerMin).toBe(0);
  });

  it('toggles toolbar state', () => {
    useToolStore.getState().toggleRightSidebar();
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(true);

    useToolStore.getState().setRightSidebarOpen(false);
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(false);

    useToolStore.getState().setActivePanel('ambient');
    expect(useToolStore.getState().ui.activePanel).toBe('ambient');
  });

  it('updates ambient active sounds and clamps sound volume', () => {
    useToolStore.getState().toggleAmbientSound('rain');
    expect(useToolStore.getState().ambient.activeSoundIds).toEqual(['rain']);
    expect(useToolStore.getState().ambient.isPlaying).toBe(true);

    useToolStore.getState().toggleAmbientSound('rain');
    expect(useToolStore.getState().ambient.activeSoundIds).toEqual([]);
    expect(useToolStore.getState().ambient.isPlaying).toBe(false);

    useToolStore.getState().setAmbientVolume('rain', 2);
    expect(useToolStore.getState().ambient.volumes.rain).toBe(1);

    useToolStore.getState().setAmbientVolume('rain', -1);
    expect(useToolStore.getState().ambient.volumes.rain).toBe(0);
  });

  it('increments pomodoro count and rolls date when stale', () => {
    useToolStore.setState((state) => ({
      pomodoro: {
        ...state.pomodoro,
        completedDateKey: 'Mon Jan 01 2001',
        completedToday: 7,
      },
    }));

    useToolStore.getState().incrementPomodoroCompleted();

    const state = useToolStore.getState();
    expect(state.pomodoro.completedToday).toBe(1);
    expect(state.pomodoro.completedDateKey).toBe(new Date().toDateString());
  });

  it('syncPomodoroDate clears stale count and keeps current day data', () => {
    useToolStore.setState((state) => ({
      pomodoro: {
        ...state.pomodoro,
        completedDateKey: 'Mon Jan 01 2001',
        completedToday: 3,
      },
    }));
    useToolStore.getState().syncPomodoroDate();
    expect(useToolStore.getState().pomodoro.completedToday).toBe(0);

    useToolStore.setState((state) => ({
      pomodoro: {
        ...state.pomodoro,
        completedDateKey: new Date().toDateString(),
        completedToday: 5,
      },
    }));
    useToolStore.getState().syncPomodoroDate();
    expect(useToolStore.getState().pomodoro.completedToday).toBe(5);
  });

  it('starts and stops pomodoro with clamped remainingSec', () => {
    useToolStore.getState().setPomodoroPreset({ workMin: 15, breakMin: 3, label: '15 / 3' });
    useToolStore.getState().startPomodoro('work', 901);
    expect(useToolStore.getState().pomodoro.mode).toBe('work');
    expect(useToolStore.getState().pomodoro.isRunning).toBe(true);
    expect(useToolStore.getState().pomodoro.remainingSec).toBe(901);

    useToolStore.getState().setPomodoroRemaining(-5);
    expect(useToolStore.getState().pomodoro.remainingSec).toBe(0);

    useToolStore.getState().stopPomodoro();
    expect(useToolStore.getState().pomodoro.mode).toBe('idle');
    expect(useToolStore.getState().pomodoro.isRunning).toBe(false);
  });
});
