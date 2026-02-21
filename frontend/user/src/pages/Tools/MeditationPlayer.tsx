import { useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Card from '../../components/Card/Card';
import Button from '../../components/Button/Button';
import { startMeditation } from '../../api/tools';
import { useAuthStore } from '../../stores/auth';
import { toast } from '../../stores/toast';
import { meditationPlaylist, type MeditationTrackConfig } from '../../config/meditationPlaylist';

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '00:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function MeditationPlayer() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { userId } = useAuthStore();
  const audioRefs = useRef<Record<string, HTMLAudioElement | null>>({});

  const [activeTrackId, setActiveTrackId] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loadingTrackId, setLoadingTrackId] = useState<string | null>(null);

  const activeTrack = useMemo(
    () => meditationPlaylist.find((item) => item.id === activeTrackId) ?? null,
    [activeTrackId],
  );

  const pauseOthers = (exceptId: string) => {
    Object.entries(audioRefs.current).forEach(([id, audio]) => {
      if (!audio || id === exceptId) return;
      audio.pause();
      audio.currentTime = 0;
    });
  };

  const handleToggleTrack = async (track: MeditationTrackConfig) => {
    const audio = audioRefs.current[track.id];
    if (!audio) return;

    if (activeTrackId === track.id && !audio.paused) {
      audio.pause();
      setPlaying(false);
      return;
    }

    pauseOthers(track.id);
    setLoadingTrackId(track.id);

    if (activeTrackId !== track.id) {
      setCurrentTime(0);
      setDuration(0);
    }

    setActiveTrackId(track.id);

    if (Number.isFinite(audio.duration) && audio.currentTime >= Math.max(0, audio.duration - 0.2)) {
      audio.currentTime = 0;
    }

    try {
      await audio.play();
      setPlaying(true);
      if (userId) {
        void startMeditation(userId, track.sessionId).catch(() => {
          toast.warning(t('tools.meditation_log_failed'));
        });
      }
    } catch {
      toast.error(t('tools.meditation_play_failed'));
    } finally {
      setLoadingTrackId(null);
    }
  };

  const handleSeek = (value: number) => {
    if (!activeTrackId) return;
    const audio = audioRefs.current[activeTrackId];
    if (!audio || !Number.isFinite(audio.duration)) return;
    audio.currentTime = value;
    setCurrentTime(value);
  };

  return (
    <div className="relative min-h-screen -mx-3 sm:-mx-4 -my-4 sm:-my-6 overflow-hidden bg-[#071826] px-3 sm:px-4 py-6 sm:py-8">
      <motion.div
        className="pointer-events-none absolute -top-24 -left-24 h-80 w-80 rounded-full bg-cyan-300/20 blur-3xl"
        animate={{ x: [0, 40, 0], y: [0, -30, 0] }}
        transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="pointer-events-none absolute -bottom-28 -right-20 h-96 w-96 rounded-full bg-indigo-300/20 blur-3xl"
        animate={{ x: [0, -32, 0], y: [0, 24, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />

      <div className="relative mx-auto max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <button
            type="button"
            onClick={() => navigate('/mindfulness')}
            className="text-sm text-cyan-100/80 hover:text-cyan-100 transition-colors mb-4"
          >
            ← {t('tools.mindfulness.back')}
          </button>
          <h1 className="font-heading text-3xl font-bold text-cyan-50">{t('tools.meditation_page_title')}</h1>
          <p className="text-cyan-100/70 mt-2">{t('tools.meditation_page_subtitle')}</p>
        </motion.div>

        <Card className="mb-6 bg-white/10 border-white/20 backdrop-blur-xl shadow-2xl">
          <p className="text-sm text-cyan-100/75">{t('tools.meditation_local_audio_note')}</p>
          {activeTrack ? (
            <div className="mt-4 rounded-2xl border border-white/20 bg-white/5 px-4 py-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 min-w-0">
                  <div
                    className="mt-0.5 h-12 w-12 shrink-0 rounded-xl border border-white/30"
                    style={{ background: activeTrack.coverGradient }}
                    aria-hidden
                  />
                  <div className="min-w-0">
                    <p className="text-xs text-cyan-100/70 uppercase tracking-wider">{t('tools.meditation_now_playing')}</p>
                    <p className="font-semibold text-cyan-50">{t(activeTrack.titleKey)}</p>
                    <p className="text-xs text-cyan-100/75 mt-0.5">{t(activeTrack.descKey)}</p>
                  </div>
                </div>
                <span className="text-sm text-cyan-100/75">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="rounded-full border border-cyan-200/30 bg-cyan-200/10 px-2 py-0.5 text-[11px] text-cyan-100/90">
                  {t(`tools.meditation_theme_${activeTrack.theme}`)}
                </span>
                {activeTrack.tagKeys.map((tagKey) => (
                  <span key={`${activeTrack.id}-${tagKey}`} className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-[11px] text-cyan-100/85">
                    {t(tagKey)}
                  </span>
                ))}
              </div>
              <div className="mt-3 space-y-1 text-xs text-cyan-100/75">
                <p>
                  {t('tools.meditation_source_label')}: {activeTrack.sourceName}{' '}
                  <a href={activeTrack.sourceUrl} target="_blank" rel="noreferrer" className="text-cyan-100 underline decoration-cyan-200/70 underline-offset-2">
                    {t('tools.meditation_open_source')}
                  </a>
                </p>
                <p>
                  {t('tools.meditation_license_label')}: {activeTrack.licenseType}
                </p>
                <p>
                  {t('tools.meditation_attribution_label')}: {t(activeTrack.attributionKey)}
                </p>
              </div>
              <input
                type="range"
                min={0}
                max={duration > 0 ? duration : 1}
                value={currentTime}
                onChange={(e) => handleSeek(Number(e.target.value))}
                className="w-full mt-3 accent-cyan-300"
              />
            </div>
          ) : null}
        </Card>

        <div className="grid gap-4">
          {meditationPlaylist.map((track, idx) => {
            const isActive = activeTrackId === track.id;
            const isLoading = loadingTrackId === track.id;

            return (
              <motion.div
                key={track.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Card className={`bg-white/10 border-white/20 backdrop-blur-xl shadow-xl ${isActive ? 'border-cyan-300/60' : ''}`}>
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex items-start gap-3">
                        <div
                          className="mt-0.5 h-12 w-12 shrink-0 rounded-xl border border-white/30"
                          style={{ background: track.coverGradient }}
                          aria-hidden
                        />
                        <div className="min-w-0">
                          <h2 className="font-heading text-lg font-bold text-cyan-50">{t(track.titleKey)}</h2>
                          <p className="text-sm text-cyan-100/75 mt-1">{t(track.descKey)}</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            <span className="rounded-full border border-cyan-200/30 bg-cyan-200/10 px-2 py-0.5 text-[11px] text-cyan-100/90">
                              {t(`tools.meditation_theme_${track.theme}`)}
                            </span>
                            {track.tagKeys.map((tagKey) => (
                              <span key={`${track.id}-${tagKey}`} className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-[11px] text-cyan-100/85">
                                {t(tagKey)}
                              </span>
                            ))}
                          </div>
                          <div className="mt-2 space-y-1 text-xs text-cyan-100/70">
                            <p>
                              {track.minutes} {t('tools.minutes')}
                            </p>
                            <p>
                              {t('tools.meditation_source_label')}: {track.sourceName}
                            </p>
                            <p>
                              {t('tools.meditation_license_label')}: {track.licenseType}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    <Button onClick={() => handleToggleTrack(track)} loading={isLoading}>
                      {isActive && playing ? t('tools.stop') : t('tools.start')}
                    </Button>
                  </div>
                  <audio
                    ref={(node) => {
                      audioRefs.current[track.id] = node;
                    }}
                    preload="metadata"
                    src={track.src}
                    onPlay={() => {
                      if (activeTrackId === track.id) {
                        setPlaying(true);
                      }
                    }}
                    onPause={() => {
                      if (activeTrackId === track.id) {
                        setPlaying(false);
                      }
                    }}
                    onEnded={() => {
                      if (activeTrackId === track.id) {
                        setPlaying(false);
                        setCurrentTime(0);
                      }
                    }}
                    onLoadedMetadata={(e) => {
                      if (activeTrackId === track.id) {
                        setDuration(e.currentTarget.duration || 0);
                      }
                    }}
                    onTimeUpdate={(e) => {
                      if (activeTrackId === track.id) {
                        setCurrentTime(e.currentTarget.currentTime);
                        setDuration(e.currentTarget.duration || 0);
                      }
                    }}
                  />
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
