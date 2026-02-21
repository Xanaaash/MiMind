import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AMBIENT_SOUNDS, type AmbientSoundId } from '../../utils/ambientAudio';
import {
  setAmbientPlaybackTimer,
  setAmbientPlaybackVolume,
  stopAllAmbientPlayback,
  toggleAmbientPlayback,
} from '../../utils/ambientAudioService';
import { useToolStore } from '../../stores/useToolStore';

const POMODORO_PRESETS = [
  { work: 25, break: 5, label: '25 / 5' },
  { work: 15, break: 3, label: '15 / 3' },
  { work: 50, break: 10, label: '50 / 10' },
];

const TIMER_OPTIONS = [0, 5, 15, 30, 60];

function formatTime(totalSec: number): string {
  const safe = Math.max(totalSec, 0);
  const min = Math.floor(safe / 60);
  const sec = safe % 60;
  return `${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
}

export default function FloatingToolbar() {
  const { t } = useTranslation();
  const [isPomodoroMiniCollapsed, setPomodoroMiniCollapsed] = useState(false);
  const isOpen = useToolStore((s) => s.ui.isRightSidebarOpen);
  const activePanel = useToolStore((s) => s.ui.activePanel);
  const setActivePanel = useToolStore((s) => s.setActivePanel);
  const setRightSidebarOpen = useToolStore((s) => s.setRightSidebarOpen);
  const toggleRightSidebar = useToolStore((s) => s.toggleRightSidebar);

  const pomodoro = useToolStore((s) => s.pomodoro);
  const setPomodoroPreset = useToolStore((s) => s.setPomodoroPreset);
  const startPomodoro = useToolStore((s) => s.startPomodoro);
  const syncPomodoroDate = useToolStore((s) => s.syncPomodoroDate);
  const stopPomodoro = useToolStore((s) => s.stopPomodoro);

  const ambient = useToolStore((s) => s.ambient);

  useEffect(() => {
    syncPomodoroDate();
  }, [syncPomodoroDate]);

  useEffect(() => {
    if (!pomodoro.isRunning) return;

    const timer = window.setInterval(() => {
      const state = useToolStore.getState();
      const current = state.pomodoro;
      if (!current.isRunning) return;

      if (current.remainingSec <= 1) {
        if (current.mode === 'work') {
          state.incrementPomodoroCompleted();
          state.startPomodoro('break', current.preset.breakMin * 60);
        } else {
          state.stopPomodoro();
        }
        return;
      }

      state.setPomodoroRemaining(current.remainingSec - 1);
    }, 1000);

    return () => window.clearInterval(timer);
  }, [pomodoro.isRunning]);

  const displaySec = pomodoro.mode === 'idle'
    ? pomodoro.preset.workMin * 60
    : pomodoro.remainingSec;
  const showPomodoroMini = pomodoro.isRunning && !isOpen;

  useEffect(() => {
    if (!pomodoro.isRunning) {
      setPomodoroMiniCollapsed(false);
    }
  }, [pomodoro.isRunning]);

  const openPomodoroPanel = () => {
    setActivePanel('pomodoro');
    setRightSidebarOpen(true);
  };

  return (
    <>
      {showPomodoroMini && (
        <div
          className={`
            fixed right-4 bottom-20 z-40 rounded-2xl border border-line bg-panel/95 backdrop-blur-md shadow-soft p-2
            ${isPomodoroMiniCollapsed ? 'w-36' : 'w-[min(48vw,220px)] sm:w-52'}
          `}
        >
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={openPomodoroPanel}
              className="flex-1 min-w-0 text-left rounded-xl px-2 py-1.5 hover:bg-paper transition-colors"
              aria-label={t('tools.pomo_floating_open')}
            >
              <div className="text-[10px] uppercase tracking-wide text-muted">
                {t(`pomo.phase_${pomodoro.mode}`)}
              </div>
              <div className="font-mono text-lg font-bold text-accent leading-tight">
                {formatTime(displaySec)}
              </div>
            </button>
            <button
              type="button"
              onClick={() => setPomodoroMiniCollapsed((prev) => !prev)}
              className="rounded-lg px-2 py-1 text-xs text-muted hover:bg-paper hover:text-ink transition-colors"
              aria-label={isPomodoroMiniCollapsed ? t('tools.pomo_floating_expand') : t('tools.pomo_floating_minimize')}
            >
              {isPomodoroMiniCollapsed ? '▣' : '—'}
            </button>
          </div>

          {!isPomodoroMiniCollapsed && (
            <div className="mt-2 grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={openPomodoroPanel}
                className="rounded-lg bg-accent text-white text-xs font-semibold py-1.5 hover:bg-accent-hover transition-colors"
              >
                {t('tools.open')}
              </button>
              <button
                type="button"
                onClick={stopPomodoro}
                className="rounded-lg bg-danger-soft text-danger text-xs font-semibold py-1.5 hover:bg-danger hover:text-white transition-colors"
              >
                {t('tools.stop')}
              </button>
            </div>
          )}
        </div>
      )}

      <button
        type="button"
        onClick={toggleRightSidebar}
        className="fixed right-4 bottom-6 z-40 rounded-full bg-accent text-white px-4 py-2 text-sm font-semibold shadow-soft hover:bg-accent-hover transition-colors"
        aria-label={isOpen ? t('tools.stop') : t('tools.title')}
      >
        {isOpen ? '✕' : '🧰'}
      </button>

      <aside
        className={`fixed right-4 top-20 bottom-20 z-40 w-[320px] max-w-[calc(100vw-2rem)] rounded-2xl border border-line bg-panel/95 backdrop-blur-md shadow-soft transition-all duration-300 ${
          isOpen ? 'translate-x-0 opacity-100 pointer-events-auto' : 'translate-x-[115%] opacity-0 pointer-events-none'
        }`}
        aria-hidden={!isOpen}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-line px-3 py-3">
            <div className="font-semibold text-sm">{t('tools.title')}</div>
            <button
              type="button"
              onClick={() => setRightSidebarOpen(false)}
              className="rounded-lg px-2 py-1 text-muted hover:bg-cream hover:text-ink transition-colors"
              aria-label={t('tools.stop')}
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2 px-3 pt-3">
            <button
              type="button"
              onClick={() => setActivePanel('pomodoro')}
              className={`rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${
                activePanel === 'pomodoro' ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
              }`}
            >
              {t('tools.pomo_title')}
            </button>
            <button
              type="button"
              onClick={() => setActivePanel('ambient')}
              className={`rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${
                activePanel === 'ambient' ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
              }`}
            >
              {t('tools.audio_title')}
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-3 py-3">
            {activePanel === 'pomodoro' ? (
              <section className="space-y-3">
                <div className="rounded-xl border border-line bg-paper px-3 py-3 text-center">
                  <div className="text-xs text-muted uppercase tracking-wider">
                    {pomodoro.mode === 'idle' ? t('pomo.ready') : t(`pomo.phase_${pomodoro.mode}`)}
                  </div>
                  <div className="mt-1 font-mono text-3xl font-bold text-accent">{formatTime(displaySec)}</div>
                  <div className="mt-2 text-xs text-muted">
                    {t('pomo.today')}: {pomodoro.completedToday} {t('tools.cycles')}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  {POMODORO_PRESETS.map((preset) => {
                    const active = pomodoro.preset.workMin === preset.work && pomodoro.preset.breakMin === preset.break;
                    return (
                      <button
                        key={preset.label}
                        type="button"
                        onClick={() => setPomodoroPreset({ workMin: preset.work, breakMin: preset.break, label: preset.label })}
                        className={`rounded-lg px-2 py-2 text-xs font-medium transition-colors ${
                          active ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
                        }`}
                      >
                        {preset.label}
                      </button>
                    );
                  })}
                </div>

                {pomodoro.isRunning ? (
                  <button
                    type="button"
                    onClick={stopPomodoro}
                    className="w-full rounded-xl bg-danger-soft py-2.5 text-sm font-semibold text-danger hover:bg-danger hover:text-white transition-colors"
                  >
                    {t('tools.stop')}
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => startPomodoro('work', pomodoro.preset.workMin * 60)}
                    className="w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white hover:bg-accent-hover transition-colors"
                  >
                    {t('tools.start')}
                  </button>
                )}
              </section>
            ) : (
              <section className="space-y-3">
                <p className="rounded-xl border border-line bg-paper px-3 py-2 text-xs text-muted">
                  {t('tools.audio_mix_hint')}
                </p>

                <div className="grid grid-cols-2 gap-2">
                  {AMBIENT_SOUNDS.map((sound) => {
                    const active = ambient.activeSoundIds.includes(sound.id);
                    return (
                      <button
                        key={sound.id}
                        type="button"
                        onClick={() => toggleAmbientPlayback(sound.id)}
                        className={`rounded-xl px-3 py-2 text-xs font-medium transition-colors ${
                          active ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
                        }`}
                      >
                        {t(`tools.sound_${sound.id}`)}
                      </button>
                    );
                  })}
                </div>

                {ambient.activeSoundIds.length > 0 && (
                  <div className="space-y-2 rounded-xl border border-line bg-paper px-3 py-3">
                    {ambient.activeSoundIds.map((soundId: AmbientSoundId) => (
                      <div key={soundId}>
                        <div className="mb-1 text-xs font-medium text-ink">{t(`tools.sound_${soundId}`)}</div>
                        <input
                          type="range"
                          min={0}
                          max={1}
                          step={0.01}
                          value={ambient.volumes[soundId] ?? 0.7}
                          onChange={(e) => setAmbientPlaybackVolume(soundId, Number(e.target.value))}
                          className="w-full accent-accent"
                          aria-label={t(`tools.sound_${soundId}`)}
                        />
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex flex-wrap gap-2">
                  {TIMER_OPTIONS.map((min) => (
                    <button
                      key={min}
                      type="button"
                      onClick={() => setAmbientPlaybackTimer(min)}
                      className={`rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors ${
                        ambient.timerMin === min ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
                      }`}
                    >
                      {min === 0 ? t('tools.timer_unlimited') : `${min}${t('tools.minutes')}`}
                    </button>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={stopAllAmbientPlayback}
                  className="w-full rounded-xl bg-danger-soft py-2.5 text-sm font-semibold text-danger hover:bg-danger hover:text-white transition-colors"
                >
                  {t('tools.stop')}
                </button>
              </section>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
