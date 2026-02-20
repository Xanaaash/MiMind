import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getAudioLibrary, getMeditationLibrary, startAudio, startMeditation } from '../../api/tools';
import { useAuthStore } from '../../stores/auth';
import Card from '../../components/Card/Card';
import Button from '../../components/Button/Button';
import Loading from '../../components/Loading/Loading';

export default function ToolsHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const userId = useAuthStore((s) => s.userId);

  const [audioTracks, setAudioTracks] = useState<Array<{ id: string; name: string }>>([]);
  const [meditations, setMeditations] = useState<Array<{ id: string; name: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAudio, setSelectedAudio] = useState('');
  const [audioMinutes, setAudioMinutes] = useState(10);
  const [selectedMeditation, setSelectedMeditation] = useState('');
  const [actionLoading, setActionLoading] = useState('');

  useEffect(() => {
    Promise.all([getAudioLibrary(), getMeditationLibrary()])
      .then(([audio, med]) => {
        const tracks = Object.entries(audio).map(([id, v]) => ({ id, name: v.name }));
        const meds = Object.entries(med).map(([id, v]) => ({ id, name: v.name }));
        setAudioTracks(tracks);
        setMeditations(meds);
        if (tracks.length) setSelectedAudio(tracks[0].id);
        if (meds.length) setSelectedMeditation(meds[0].id);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleStartAudio = async () => {
    if (!userId || !selectedAudio) return;
    setActionLoading('audio');
    try {
      await startAudio(userId, selectedAudio, audioMinutes);
    } finally {
      setActionLoading('');
    }
  };

  const handleStartMeditation = async () => {
    if (!userId || !selectedMeditation) return;
    setActionLoading('meditation');
    try {
      await startMeditation(userId, selectedMeditation);
    } finally {
      setActionLoading('');
    }
  };

  if (loading) return <Loading text={t('common.loading')} />;

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-heading text-3xl font-bold">{t('tools.title')}</h1>
        <p className="text-muted mt-1 mb-8">{t('tools.subtitle')}</p>
      </motion.div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* White Noise */}
        <Card>
          <div className="w-12 h-12 rounded-xl bg-calm-soft flex items-center justify-center text-2xl mb-4">🎧</div>
          <h3 className="font-heading font-bold text-lg mb-1">{t('tools.audio_title')}</h3>
          <p className="text-muted text-sm mb-4">{t('tools.audio_desc')}</p>
          <select
            value={selectedAudio}
            onChange={(e) => setSelectedAudio(e.target.value)}
            className="w-full border border-line rounded-xl px-3 py-2 mb-3 bg-white/90"
          >
            {audioTracks.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          <div className="flex items-center gap-2 mb-4">
            <input
              type="range"
              min={1}
              max={120}
              value={audioMinutes}
              onChange={(e) => setAudioMinutes(Number(e.target.value))}
              className="flex-1 accent-calm"
            />
            <span className="text-sm text-muted w-16 text-right">{audioMinutes} {t('tools.minutes')}</span>
          </div>
          <Button
            size="sm"
            className="w-full"
            onClick={handleStartAudio}
            loading={actionLoading === 'audio'}
          >
            {t('tools.start')}
          </Button>
        </Card>

        {/* Breathing */}
        <Card hoverable onClick={() => navigate('/tools/breathing')}>
          <div className="w-12 h-12 rounded-xl bg-safe-soft flex items-center justify-center text-2xl mb-4">🌬️</div>
          <h3 className="font-heading font-bold text-lg mb-1">{t('tools.breathing_title')}</h3>
          <p className="text-muted text-sm mb-4">{t('tools.breathing_desc')}</p>
          <p className="text-accent font-semibold text-sm">{t('tools.start')} →</p>
        </Card>

        {/* Meditation */}
        <Card>
          <div className="w-12 h-12 rounded-xl bg-accent-soft flex items-center justify-center text-2xl mb-4">🧘</div>
          <h3 className="font-heading font-bold text-lg mb-1">{t('tools.meditation_title')}</h3>
          <p className="text-muted text-sm mb-4">{t('tools.meditation_desc')}</p>
          <select
            value={selectedMeditation}
            onChange={(e) => setSelectedMeditation(e.target.value)}
            className="w-full border border-line rounded-xl px-3 py-2 mb-4 bg-white/90"
          >
            {meditations.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
          <Button
            size="sm"
            className="w-full"
            onClick={handleStartMeditation}
            loading={actionLoading === 'meditation'}
          >
            {t('tools.start')}
          </Button>
        </Card>
      </div>
    </div>
  );
}
