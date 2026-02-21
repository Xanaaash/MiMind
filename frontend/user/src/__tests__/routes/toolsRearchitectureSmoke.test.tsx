import React, { Suspense } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { routes } from '../../router';
import { useAuthStore } from '../../stores/auth';
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
    i18n: { language: 'en-US', changeLanguage: vi.fn() },
  }),
}));

vi.mock('../../utils/ambientAudioService', () => ({
  toggleAmbientPlayback: ambientServiceMocks.toggleAmbientPlayback,
  setAmbientPlaybackVolume: ambientServiceMocks.setAmbientPlaybackVolume,
  setAmbientPlaybackTimer: ambientServiceMocks.setAmbientPlaybackTimer,
  stopAllAmbientPlayback: ambientServiceMocks.stopAllAmbientPlayback,
}));

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  return render(
    <Suspense fallback={<div>loading</div>}>
      <RouterProvider router={router} />
    </Suspense>,
  );
}

describe('tools rearchitecture smoke routes', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({
      userId: 'u-1',
      email: 'u1@example.com',
      locale: 'en-US',
      channel: 'GREEN',
      isAuthenticated: true,
      isLoading: false,
      isInitialized: true,
    });
    useToolStore.getState().resetTools();
    ambientServiceMocks.toggleAmbientPlayback.mockReset();
    ambientServiceMocks.setAmbientPlaybackVolume.mockReset();
    ambientServiceMocks.setAmbientPlaybackTimer.mockReset();
    ambientServiceMocks.stopAllAmbientPlayback.mockReset();
  });

  it('redirects /tools to /relief during transition period', async () => {
    renderAt('/tools');
    expect(await screen.findByText('tools.rescue.title')).toBeInTheDocument();
  });

  it('keeps toolbar open and does not stop ambient playback when navigating /home -> /coach -> /relief', async () => {
    renderAt('/home');
    fireEvent.click(await screen.findByRole('button', { name: 'tools.title' }));
    fireEvent.click(screen.getByRole('button', { name: 'tools.audio_title' }));
    fireEvent.click(screen.getByRole('button', { name: 'tools.sound_rain' }));

    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(true);
    expect(ambientServiceMocks.toggleAmbientPlayback).toHaveBeenCalledWith('rain');

    const coachNav = screen.getAllByRole('link', { name: /nav\.coach/ })[0];
    fireEvent.click(coachNav);

    fireEvent.click(screen.getAllByRole('link', { name: /nav\.rescue/ })[0]);
    expect(await screen.findByText('tools.rescue.title')).toBeInTheDocument();
    expect(useToolStore.getState().ui.isRightSidebarOpen).toBe(true);
    expect(ambientServiceMocks.stopAllAmbientPlayback).not.toHaveBeenCalled();
  });

  it('keeps pomodoro mini timer visible and counting down across routes', async () => {
    renderAt('/home');
    act(() => {
      useToolStore.getState().startPomodoro('work', 5);
    });

    expect(await screen.findByRole('button', { name: 'tools.pomo_floating_open' })).toBeInTheDocument();

    const coachNav = screen.getAllByRole('link', { name: /nav\.coach/ })[0];
    fireEvent.click(coachNav);
    fireEvent.click(screen.getAllByRole('link', { name: /nav\.rescue/ })[0]);
    expect(await screen.findByText('tools.rescue.title')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'tools.pomo_floating_open' })).toBeInTheDocument();

    const before = useToolStore.getState().pomodoro.remainingSec;
    await act(async () => {
      await new Promise((resolve) => {
        setTimeout(resolve, 1100);
      });
    });
    const after = useToolStore.getState().pomodoro.remainingSec;
    expect(after).toBeLessThan(before);
  });

  it('starts relief quick action with one click and reaches sensory page', async () => {
    renderAt('/relief');
    const quickStartText = await screen.findByText('tools.rescue.quick_pink_start');
    fireEvent.click(quickStartText.closest('button') as HTMLButtonElement);

    expect(ambientServiceMocks.setAmbientPlaybackVolume).toHaveBeenCalledWith('pink_noise', 0.45);
    expect(ambientServiceMocks.toggleAmbientPlayback).toHaveBeenCalledWith('pink_noise');
    expect(await screen.findByText('sensory.title')).toBeInTheDocument();
  });

  it('renders key mindfulness routes', async () => {
    const first = renderAt('/mindfulness/meditation');
    expect(await screen.findByText('tools.meditation_page_title')).toBeInTheDocument();
    first.unmount();

    renderAt('/mindfulness/manifestation');
    expect(await screen.findByText('tools.manifestation.title')).toBeInTheDocument();
  });
});
