import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
import FloatingToolbar from '../../components/FloatingToolbar/FloatingToolbar';
import { useToolStore } from '../../stores/useToolStore';

const ambientServiceMocks = vi.hoisted(() => ({
  toggleAmbientPlayback: vi.fn(),
  setAmbientPlaybackVolume: vi.fn(),
  setAmbientPlaybackTimer: vi.fn(),
  stopAllAmbientPlayback: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

vi.mock('../../utils/ambientAudioService', () => ({
  toggleAmbientPlayback: ambientServiceMocks.toggleAmbientPlayback,
  setAmbientPlaybackVolume: ambientServiceMocks.setAmbientPlaybackVolume,
  setAmbientPlaybackTimer: ambientServiceMocks.setAmbientPlaybackTimer,
  stopAllAmbientPlayback: ambientServiceMocks.stopAllAmbientPlayback,
}));

describe('FloatingToolbar', () => {
  beforeEach(() => {
    localStorage.removeItem('mc_tool_store');
    useToolStore.getState().resetTools();
    ambientServiceMocks.toggleAmbientPlayback.mockReset();
    ambientServiceMocks.setAmbientPlaybackVolume.mockReset();
    ambientServiceMocks.setAmbientPlaybackTimer.mockReset();
    ambientServiceMocks.stopAllAmbientPlayback.mockReset();
  });

  it('toggles right toolbar open state from floating button', () => {
    render(<FloatingToolbar />);
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(false);

    fireEvent.click(screen.getByRole('button', { name: 'tools.title' }));
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(true);
    expect(screen.getByRole('complementary')).toHaveAttribute('aria-hidden', 'false');

    fireEvent.click(screen.getAllByRole('button', { name: 'tools.stop' })[0]);
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(false);
  });

  it('triggers ambient playback toggle when sound chip is clicked', () => {
    useToolStore.setState((state) => ({
      ...state,
      ui: {
        ...state.ui,
        isRightSidebarOpen: true,
        activePanel: 'ambient',
      },
    }));

    render(<FloatingToolbar />);
    fireEvent.click(screen.getByRole('button', { name: 'tools.sound_rain' }));

    expect(ambientServiceMocks.toggleAmbientPlayback).toHaveBeenCalledTimes(1);
    expect(ambientServiceMocks.toggleAmbientPlayback).toHaveBeenCalledWith('rain');
  });

  it('updates ambient volume and timer and supports stop-all action', () => {
    useToolStore.setState((state) => ({
      ...state,
      ui: {
        ...state.ui,
        isRightSidebarOpen: true,
        activePanel: 'ambient',
      },
      ambient: {
        ...state.ambient,
        activeSoundIds: ['rain'],
        isPlaying: true,
        volumes: {
          ...state.ambient.volumes,
          rain: 0.42,
        },
      },
    }));

    render(<FloatingToolbar />);

    fireEvent.change(screen.getByRole('slider', { name: 'tools.sound_rain' }), {
      target: { value: '0.35' },
    });
    expect(ambientServiceMocks.setAmbientPlaybackVolume).toHaveBeenCalledWith('rain', 0.35);

    fireEvent.click(screen.getByRole('button', { name: '15tools.minutes' }));
    expect(ambientServiceMocks.setAmbientPlaybackTimer).toHaveBeenCalledWith(15);

    fireEvent.click(screen.getByText('tools.stop'));
    expect(ambientServiceMocks.stopAllAmbientPlayback).toHaveBeenCalledTimes(1);
  });

  it('shows running pomodoro mini widget and supports minimize / expand / open panel', () => {
    act(() => {
      useToolStore.getState().startPomodoro('work', 65);
    });
    render(<FloatingToolbar />);

    expect(screen.getByRole('button', { name: 'tools.pomo_floating_open' })).toBeInTheDocument();
    expect(screen.getAllByText('01:05').length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole('button', { name: 'tools.pomo_floating_minimize' }));
    expect(screen.getByRole('button', { name: 'tools.pomo_floating_expand' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'tools.pomo_floating_open' }));
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(true);
    expect(useToolStore.getState().ui.activePanel).toBe('pomodoro');

    act(() => {
      useToolStore.getState().stopPomodoro();
    });
    expect(screen.queryByRole('button', { name: 'tools.pomo_floating_open' })).not.toBeInTheDocument();
  });
});
