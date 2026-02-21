import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { AMBIENT_SOUNDS, type AmbientSoundId } from '../../utils/ambientAudio';
import {
  setAmbientPlaybackTimer,
  setAmbientPlaybackVolume,
  stopAllAmbientPlayback,
  toggleAmbientPlayback,
} from '../../utils/ambientAudioService';
import { getToolUsageStats } from '../../api/tools';
import { useAuthStore } from '../../stores/auth';
import { useToolStore } from '../../stores/useToolStore';
import Card from '../../components/Card/Card';
import type { ToolUsageStats } from '../../types';

const TIMER_OPTIONS = [0, 5, 15, 30, 60];

export default function ToolsHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const userId = useAuthStore((s) => s.userId);
  const activeSounds = useToolStore((s) => s.ambient.activeSoundIds);
  const soundVolumes = useToolStore((s) => s.ambient.volumes);
  const timerMin = useToolStore((s) => s.ambient.timerMin);
  const startedAtMs = useToolStore((s) => s.ambient.startedAtMs);

  const [elapsed, setElapsed] = useState(0);
  const [usageStats, setUsageStats] = useState<ToolUsageStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const playing = activeSounds.length > 0;

  useEffect(() => {
    return () => {
      if (tickRef.current) clearInterval(tickRef.current);
    };
  }, []);

  useEffect(() => {
    if (playing) {
      const start = startedAtMs ?? Date.now();
      setElapsed(Math.floor((Date.now() - start) / 1000));
      tickRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - start) / 1000));
      }, 1000);
    } else {
      if (tickRef.current) clearInterval(tickRef.current);
      setElapsed(0);
    }
    return () => { if (tickRef.current) clearInterval(tickRef.current); };
  }, [playing, startedAtMs]);

  useEffect(() => {
    if (!userId) {
      setUsageStats(null);
      return;
    }

    let canceled = false;
    setStatsLoading(true);
    getToolUsageStats(userId)
      .then((data) => {
        if (!canceled) {
          setUsageStats(data);
        }
      })
      .catch(() => {
        if (!canceled) {
          setUsageStats(null);
        }
      })
      .finally(() => {
        if (!canceled) {
          setStatsLoading(false);
        }
      });

    return () => {
      canceled = true;
    };
  }, [userId]);

  const handleToggle = useCallback((soundId: AmbientSoundId) => {
    toggleAmbientPlayback(soundId);
  }, []);

  const handleVolumeChange = useCallback((soundId: AmbientSoundId, volume: number) => {
    setAmbientPlaybackVolume(soundId, volume);
  }, []);

  const handleTimerChange = useCallback((min: number) => {
    setAmbientPlaybackTimer(min);
  }, []);

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const formatDuration = (seconds: number) => {
    const totalMinutes = Math.floor(seconds / 60);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    if (hours <= 0) {
      return `${totalMinutes} ${t('tools.minutes')}`;
    }
    return `${hours}${t('tools.stats_hour_short')} ${minutes}${t('tools.stats_min_short')}`;
  };

  const toolChips = [
    { key: 'audio', label: t('tools.audio_title') },
    { key: 'breathing', label: t('tools.breathing_title') },
    { key: 'meditation', label: t('tools.meditation_title') },
  ];

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-heading text-3xl font-bold">{t('tools.title')}</h1>
        <p className="text-muted mt-1 mb-8">{t('tools.subtitle')}</p>
      </motion.div>

      <Card className="mb-8 bg-gradient-to-r from-calm-soft/70 to-accent-soft/60">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="font-heading font-bold text-lg">{t('tools.stats_title')}</h3>
            <p className="text-muted text-sm mt-1">{t('tools.stats_subtitle')}</p>
          </div>
          <span className="text-2xl">📊</span>
        </div>

        <div className="grid grid-cols-2 gap-3 mt-5">
          <div className="rounded-xl bg-paper/80 border border-line p-4">
            <p className="text-muted text-xs uppercase tracking-wide">{t('tools.stats_week_usage')}</p>
            <p className="font-heading text-2xl font-bold mt-2">
              {statsLoading ? '--' : usageStats?.week_usage_count ?? 0}
              <span className="text-base font-medium ml-1">{t('tools.stats_sessions_unit')}</span>
            </p>
          </div>
          <div className="rounded-xl bg-paper/80 border border-line p-4">
            <p className="text-muted text-xs uppercase tracking-wide">{t('tools.stats_total_duration')}</p>
            <p className="font-heading text-2xl font-bold mt-2">
              {statsLoading ? '--' : formatDuration(usageStats?.total_duration_seconds ?? 0)}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mt-4">
          {toolChips.map((chip) => (
            <span
              key={chip.key}
              className="text-xs rounded-full px-3 py-1 bg-paper/80 border border-line text-muted"
            >
              {chip.label}: {usageStats?.by_tool?.[chip.key]?.week_usage_count ?? 0} {t('tools.stats_sessions_unit')}
            </span>
          ))}
        </div>
      </Card>

      {/* Ambient Sound Player */}
      <Card className="mb-8">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-calm-soft flex items-center justify-center text-xl">🎧</div>
          <div>
            <h3 className="font-heading font-bold text-lg">{t('tools.audio_title')}</h3>
            <p className="text-muted text-sm">{t('tools.audio_desc')}</p>
            <p className="text-xs text-accent mt-1">{t('tools.audio_mix_hint')}</p>
          </div>
        </div>

        {/* Sound grid */}
        <div className="grid grid-cols-5 gap-3 mb-6">
          {AMBIENT_SOUNDS.map((s) => {
            const isActive = activeSounds.includes(s.id);
            return (
              <button
                key={s.id}
                onClick={() => handleToggle(s.id)}
                className={`
                  relative flex flex-col items-center gap-2 py-4 rounded-2xl border-2 transition-all cursor-pointer
                  ${isActive
                    ? 'border-accent bg-accent-soft scale-105 shadow-md'
                    : `border-line ${s.color} hover:border-accent/30 hover:shadow-sm`
                  }
                `}
              >
                <span className="text-3xl">{s.emoji}</span>
                <span className="text-xs font-semibold">{t(s.nameKey)}</span>
                <AnimatePresence>
                  {isActive && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-accent rounded-full flex items-center justify-center"
                    >
                      <span className="text-white text-[10px]">▶</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </button>
            );
          })}
        </div>

        {/* Controls */}
        <AnimatePresence>
          {playing && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              {/* Elapsed */}
              <div className="text-center mb-4">
                <span className="font-mono text-2xl font-bold text-accent">{formatTime(elapsed)}</span>
                {timerMin > 0 && (
                  <span className="text-muted text-sm ml-2">/ {timerMin}:00</span>
                )}
              </div>

              {/* Volume */}
              <div className="space-y-3 mb-4">
                {activeSounds.map((soundId) => {
                  const sound = AMBIENT_SOUNDS.find((item) => item.id === soundId);
                  if (!sound) return null;

                  const volume = soundVolumes[soundId] ?? 0.7;

                  return (
                    <div key={soundId} className="flex items-center gap-3 rounded-xl bg-paper border border-line px-3 py-2">
                      <span className="text-base">{sound.emoji}</span>
                      <span className="text-xs text-muted min-w-[56px]">{t(sound.nameKey)}</span>
                      <span className="text-xs text-muted">🔈</span>
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.01}
                        value={volume}
                        onChange={(e) => handleVolumeChange(soundId, Number(e.target.value))}
                        aria-label={`${t(sound.nameKey)} volume`}
                        className="flex-1 accent-accent h-2"
                      />
                      <span className="text-xs text-muted">🔊</span>
                      <span className="text-xs font-medium text-muted w-10 text-right">
                        {Math.round(volume * 100)}%
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Timer */}
              <div className="flex items-center gap-2 mb-4">
                <span className="text-sm text-muted">⏱️</span>
                {TIMER_OPTIONS.map((min) => (
                  <button
                    key={min}
                    onClick={() => handleTimerChange(min)}
                    className={`
                      px-3 py-1 rounded-lg text-xs font-medium transition-colors
                      ${timerMin === min
                        ? 'bg-accent text-white'
                        : 'bg-cream text-muted hover:bg-accent-soft'
                      }
                    `}
                  >
                    {min === 0
                      ? t('tools.timer_unlimited')
                      : `${min} ${t('tools.minutes')}`
                    }
                  </button>
                ))}
              </div>

              {/* Stop */}
              <button
                onClick={() => { stopAllAmbientPlayback(); }}
                className="w-full py-2.5 rounded-xl bg-danger-soft text-danger font-semibold text-sm hover:bg-danger hover:text-white transition-colors"
              >
                {t('tools.stop')}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Other tools */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Sensory Relief */}
        <Card hoverable onClick={() => navigate('/relief/sensory')}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-calm-soft flex items-center justify-center text-3xl">🛡️</div>
            <div>
              <h3 className="font-heading font-bold text-lg">{t('tools.sensory_title')}</h3>
              <p className="text-muted text-sm mt-1">{t('tools.sensory_desc')}</p>
              <p className="text-accent font-semibold text-sm mt-2">{t('tools.start')} →</p>
            </div>
          </div>
        </Card>

        {/* Breathing */}
        <Card hoverable onClick={() => navigate('/relief/breathing')}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-safe-soft flex items-center justify-center text-3xl">🌬️</div>
            <div>
              <h3 className="font-heading font-bold text-lg">{t('tools.breathing_title')}</h3>
              <p className="text-muted text-sm mt-1">{t('tools.breathing_desc')}</p>
              <p className="text-accent font-semibold text-sm mt-2">{t('tools.start')} →</p>
            </div>
          </div>
        </Card>

        {/* Pomodoro */}
        <Card hoverable onClick={() => navigate('/tools/pomodoro')}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-warn-soft flex items-center justify-center text-3xl">🍅</div>
            <div>
              <h3 className="font-heading font-bold text-lg">{t('tools.pomo_title')}</h3>
              <p className="text-muted text-sm mt-1">{t('tools.pomo_desc')}</p>
              <p className="text-accent font-semibold text-sm mt-2">{t('tools.start')} →</p>
            </div>
          </div>
        </Card>

        {/* Meditation */}
        <Card hoverable onClick={() => navigate('/tools/meditation')}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-accent-soft flex items-center justify-center text-3xl">🧘</div>
            <div>
              <h3 className="font-heading font-bold text-lg">{t('tools.meditation_title')}</h3>
              <p className="text-muted text-sm mt-1">{t('tools.meditation_desc')}</p>
              <p className="text-accent font-semibold text-sm mt-2">{t('tools.start')} →</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
