import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useToolStore } from '../../stores/useToolStore';
import {
  setAmbientPlaybackTimer,
  setAmbientPlaybackVolume,
  stopAllAmbientPlayback,
  toggleAmbientPlayback,
} from '../../utils/ambientAudioService';

const ambientEngineMocks = vi.hoisted(() => ({
  clearTimer: vi.fn(),
  isPlaying: vi.fn(),
  isSoundPlaying: vi.fn(),
  setAmbientVolume: vi.fn(),
  setTimer: vi.fn(),
  startAmbient: vi.fn(),
  stopAmbient: vi.fn(),
  stopAmbientSound: vi.fn(),
}));

vi.mock('../../utils/ambientAudio', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../utils/ambientAudio')>();
  return {
    ...actual,
    clearTimer: ambientEngineMocks.clearTimer,
    isPlaying: ambientEngineMocks.isPlaying,
    isSoundPlaying: ambientEngineMocks.isSoundPlaying,
    setAmbientVolume: ambientEngineMocks.setAmbientVolume,
    setTimer: ambientEngineMocks.setTimer,
    startAmbient: ambientEngineMocks.startAmbient,
    stopAmbient: ambientEngineMocks.stopAmbient,
    stopAmbientSound: ambientEngineMocks.stopAmbientSound,
  };
});

describe('ambientAudioService', () => {
  beforeEach(() => {
    localStorage.removeItem('mc_tool_store');
    useToolStore.getState().resetTools();

    ambientEngineMocks.clearTimer.mockReset();
    ambientEngineMocks.isPlaying.mockReset();
    ambientEngineMocks.isSoundPlaying.mockReset();
    ambientEngineMocks.setAmbientVolume.mockReset();
    ambientEngineMocks.setTimer.mockReset();
    ambientEngineMocks.startAmbient.mockReset();
    ambientEngineMocks.stopAmbient.mockReset();
    ambientEngineMocks.stopAmbientSound.mockReset();
  });

  it('starts ambient sound and syncs store state on toggle-on', () => {
    useToolStore.getState().setAmbientVolume('rain', 0.34);
    ambientEngineMocks.isSoundPlaying.mockReturnValue(false);

    toggleAmbientPlayback('rain');

    expect(ambientEngineMocks.startAmbient).toHaveBeenCalledWith('rain', 0.34);
    expect(useToolStore.getState().ambient.activeSoundIds).toEqual(['rain']);
    expect(useToolStore.getState().ambient.isPlaying).toBe(true);
    expect(useToolStore.getState().ambient.startedAtMs).not.toBeNull();
  });

  it('stops a single active sound and clears timer fields when last sound is removed', () => {
    useToolStore.setState((state) => ({
      ...state,
      ambient: {
        ...state.ambient,
        activeSoundIds: ['rain'],
        isPlaying: true,
        timerMin: 15,
        startedAtMs: 1000,
      },
    }));
    ambientEngineMocks.isSoundPlaying.mockReturnValue(true);

    toggleAmbientPlayback('rain');

    expect(ambientEngineMocks.stopAmbientSound).toHaveBeenCalledWith('rain');
    expect(ambientEngineMocks.clearTimer).toHaveBeenCalledTimes(1);
    expect(useToolStore.getState().ambient.activeSoundIds).toEqual([]);
    expect(useToolStore.getState().ambient.isPlaying).toBe(false);
    expect(useToolStore.getState().ambient.timerMin).toBe(0);
    expect(useToolStore.getState().ambient.startedAtMs).toBeNull();
  });

  it('stops only one sound without clearing timer when other sounds remain', () => {
    useToolStore.setState((state) => ({
      ...state,
      ambient: {
        ...state.ambient,
        activeSoundIds: ['rain', 'ocean'],
        isPlaying: true,
        timerMin: 30,
        startedAtMs: 2000,
      },
    }));
    ambientEngineMocks.isSoundPlaying.mockReturnValue(true);

    toggleAmbientPlayback('rain');

    expect(ambientEngineMocks.clearTimer).not.toHaveBeenCalled();
    expect(useToolStore.getState().ambient.activeSoundIds).toEqual(['ocean']);
    expect(useToolStore.getState().ambient.timerMin).toBe(30);
    expect(useToolStore.getState().ambient.startedAtMs).toBe(2000);
  });

  it('updates store volume and forwards volume to engine only when sound is playing', () => {
    ambientEngineMocks.isSoundPlaying.mockReturnValue(false);
    setAmbientPlaybackVolume('rain', 0.25);
    expect(useToolStore.getState().ambient.volumes.rain).toBe(0.25);
    expect(ambientEngineMocks.setAmbientVolume).not.toHaveBeenCalled();

    ambientEngineMocks.isSoundPlaying.mockReturnValue(true);
    setAmbientPlaybackVolume('rain', 0.66);
    expect(useToolStore.getState().ambient.volumes.rain).toBe(0.66);
    expect(ambientEngineMocks.setAmbientVolume).toHaveBeenCalledWith('rain', 0.66);
  });

  it('sets playback timer and calls engine timer only when ambient is playing', () => {
    ambientEngineMocks.isPlaying.mockReturnValue(false);
    setAmbientPlaybackTimer(10);
    expect(useToolStore.getState().ambient.timerMin).toBe(10);
    expect(ambientEngineMocks.setTimer).not.toHaveBeenCalled();

    ambientEngineMocks.isPlaying.mockReturnValue(true);
    setAmbientPlaybackTimer(5);
    expect(ambientEngineMocks.setTimer).toHaveBeenCalledTimes(1);
    expect(ambientEngineMocks.setTimer.mock.calls[0][0]).toBe(5);

    setAmbientPlaybackTimer(0);
    expect(ambientEngineMocks.clearTimer).toHaveBeenCalledTimes(1);
  });

  it('stopAllAmbientPlayback clears both engine and store state', () => {
    useToolStore.setState((state) => ({
      ...state,
      ambient: {
        ...state.ambient,
        activeSoundIds: ['rain', 'ocean'],
        isPlaying: true,
        timerMin: 5,
        startedAtMs: 1234,
      },
    }));

    stopAllAmbientPlayback();

    expect(ambientEngineMocks.stopAmbient).toHaveBeenCalledTimes(1);
    expect(useToolStore.getState().ambient.activeSoundIds).toEqual([]);
    expect(useToolStore.getState().ambient.isPlaying).toBe(false);
    expect(useToolStore.getState().ambient.timerMin).toBe(0);
    expect(useToolStore.getState().ambient.startedAtMs).toBeNull();
  });
});
