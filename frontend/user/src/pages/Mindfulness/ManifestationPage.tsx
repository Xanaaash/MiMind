import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import { useToolStore } from '../../stores/useToolStore';
import { setAmbientPlaybackVolume, toggleAmbientPlayback } from '../../utils/ambientAudioService';

interface VisionCard {
  id: string;
  title: string;
  note: string;
}

const AFFIRMATIONS_KEY = 'mindfulness_affirmations_v1';
const VISION_CARDS_KEY = 'mindfulness_vision_cards_v1';

function loadList<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

export default function ManifestationPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const activeSounds = useToolStore((s) => s.ambient.activeSoundIds);
  const oceanActive = activeSounds.includes('ocean');

  const [affirmationInput, setAffirmationInput] = useState('');
  const [affirmations, setAffirmations] = useState<string[]>(() => loadList<string[]>(AFFIRMATIONS_KEY, []));
  const [visionTitle, setVisionTitle] = useState('');
  const [visionNote, setVisionNote] = useState('');
  const [visionCards, setVisionCards] = useState<VisionCard[]>(() => loadList<VisionCard[]>(VISION_CARDS_KEY, []));

  useEffect(() => {
    localStorage.setItem(AFFIRMATIONS_KEY, JSON.stringify(affirmations));
  }, [affirmations]);

  useEffect(() => {
    localStorage.setItem(VISION_CARDS_KEY, JSON.stringify(visionCards));
  }, [visionCards]);

  const addAffirmation = () => {
    const value = affirmationInput.trim();
    if (!value) return;
    setAffirmations((prev) => [value, ...prev].slice(0, 20));
    setAffirmationInput('');
  };

  const addVisionCard = () => {
    const title = visionTitle.trim();
    const note = visionNote.trim();
    if (!title || !note) return;
    setVisionCards((prev) => [
      { id: `${Date.now()}-${prev.length}`, title, note },
      ...prev,
    ].slice(0, 12));
    setVisionTitle('');
    setVisionNote('');
  };

  const toggleSoftAudio = () => {
    setAmbientPlaybackVolume('ocean', 0.35);
    toggleAmbientPlayback('ocean');
  };

  return (
    <div className="space-y-5 max-w-3xl mx-auto">
      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-line bg-panel px-5 py-6"
      >
        <button
          type="button"
          onClick={() => navigate('/mindfulness')}
          className="text-sm text-muted hover:text-accent transition-colors"
        >
          ← {t('mindfulness.back')}
        </button>
        <h1 className="mt-2 font-heading text-2xl font-bold">{t('mindfulness.manifestation_title')}</h1>
        <p className="mt-2 text-sm text-muted">{t('mindfulness.manifestation_desc')}</p>
        <div className="mt-4">
          <Button onClick={toggleSoftAudio}>
            {oceanActive ? t('mindfulness.manifestation_audio_stop') : t('mindfulness.manifestation_audio_start')}
          </Button>
        </div>
      </motion.section>

      <Card>
        <h2 className="font-heading text-lg font-bold">{t('mindfulness.manifestation_affirmation_title')}</h2>
        <p className="text-sm text-muted mt-1">{t('mindfulness.manifestation_affirmation_desc')}</p>
        <div className="mt-3 flex gap-2">
          <input
            value={affirmationInput}
            onChange={(e) => setAffirmationInput(e.target.value)}
            placeholder={t('mindfulness.manifestation_affirmation_placeholder')}
            className="flex-1 rounded-xl border border-line bg-paper px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
          />
          <Button onClick={addAffirmation} disabled={!affirmationInput.trim()}>
            {t('common.add')}
          </Button>
        </div>
        <div className="mt-4 space-y-2">
          {affirmations.length === 0 ? (
            <p className="text-sm text-muted">{t('mindfulness.manifestation_empty_affirmation')}</p>
          ) : (
            affirmations.map((item, idx) => (
              <div key={`${idx}-${item}`} className="rounded-xl border border-line bg-paper px-3 py-2 text-sm">
                {item}
              </div>
            ))
          )}
        </div>
      </Card>

      <Card>
        <h2 className="font-heading text-lg font-bold">{t('mindfulness.manifestation_vision_title')}</h2>
        <p className="text-sm text-muted mt-1">{t('mindfulness.manifestation_vision_desc')}</p>
        <div className="mt-3 grid gap-2">
          <input
            value={visionTitle}
            onChange={(e) => setVisionTitle(e.target.value)}
            placeholder={t('mindfulness.manifestation_vision_title_placeholder')}
            className="rounded-xl border border-line bg-paper px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
          />
          <textarea
            value={visionNote}
            onChange={(e) => setVisionNote(e.target.value)}
            placeholder={t('mindfulness.manifestation_vision_note_placeholder')}
            className="min-h-24 rounded-xl border border-line bg-paper px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
          />
          <Button onClick={addVisionCard} disabled={!visionTitle.trim() || !visionNote.trim()}>
            {t('common.save')}
          </Button>
        </div>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {visionCards.length === 0 ? (
            <p className="text-sm text-muted">{t('mindfulness.manifestation_empty_vision')}</p>
          ) : (
            visionCards.map((card) => (
              <div key={card.id} className="rounded-2xl border border-line bg-paper p-4">
                <p className="font-heading font-bold">{card.title}</p>
                <p className="text-sm text-muted mt-1 whitespace-pre-wrap">{card.note}</p>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
