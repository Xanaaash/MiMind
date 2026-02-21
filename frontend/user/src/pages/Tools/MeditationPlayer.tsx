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
        void startMeditation(userId, track.id).catch(() => {
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
    <div className="max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <button
          type="button"
          onClick={() => navigate('/mindfulness')}
          className="text-sm text-muted hover:text-accent transition-colors mb-4"
        >
          ← {t('mindfulness.back')}
        </button>
        <h1 className="font-heading text-3xl font-bold">{t('tools.meditation_page_title')}</h1>
        <p className="text-muted mt-2">{t('tools.meditation_page_subtitle')}</p>
      </motion.div>

      <Card className="mb-6">
        <p className="text-sm text-muted">{t('tools.meditation_local_audio_note')}</p>
        {activeTrack ? (
          <div className="mt-4 rounded-2xl border border-line bg-paper px-4 py-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs text-muted uppercase tracking-wider">{t('tools.meditation_now_playing')}</p>
                <p className="font-semibold">{t(activeTrack.titleKey)}</p>
              </div>
              <span className="text-sm text-muted">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={duration > 0 ? duration : 1}
              value={currentTime}
              onChange={(e) => handleSeek(Number(e.target.value))}
              className="w-full mt-3 accent-accent"
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
              <Card className={isActive ? 'border-accent/40' : ''}>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="min-w-0">
                    <h2 className="font-heading text-lg font-bold">{t(track.titleKey)}</h2>
                    <p className="text-sm text-muted mt-1">{t(track.descKey)}</p>
                    <p className="text-xs text-muted mt-2">
                      {track.minutes} {t('tools.minutes')}
                    </p>
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
  );
}
