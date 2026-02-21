import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
type PracticeMode = 'quick' | 'deep';
type QuickFocus = 'stability' | 'confidence' | 'calm';

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
  const [searchParams] = useSearchParams();
  const activeSounds = useToolStore((s) => s.ambient.activeSoundIds);
  const oceanActive = activeSounds.includes('ocean');

  const modeParam = searchParams.get('mode');
  const initialMode: PracticeMode = modeParam === 'deep' ? 'deep' : 'quick';
  const [practiceMode, setPracticeMode] = useState<PracticeMode>(initialMode);
  const [quickFocus, setQuickFocus] = useState<QuickFocus>('stability');
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

  const ensureSoftAudio = () => {
    setAmbientPlaybackVolume('ocean', 0.35);
    if (!oceanActive) {
      toggleAmbientPlayback('ocean');
    }
  };

  const addQuickAffirmation = () => {
    const template = t(`tools.manifestation.quick_template_${quickFocus}`);
    setAffirmations((prev) => [template, ...prev].slice(0, 20));
    ensureSoftAudio();
  };

  const toggleSoftAudio = () => {
    if (oceanActive) {
      toggleAmbientPlayback('ocean');
      return;
    }
    ensureSoftAudio();
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
          ← {t('tools.mindfulness.back')}
        </button>
        <h1 className="mt-2 font-heading text-2xl font-bold">{t('tools.manifestation.title')}</h1>
        <p className="mt-2 text-sm text-muted">{t('tools.manifestation.desc')}</p>
        <div className="mt-4">
          <Button onClick={toggleSoftAudio}>
            {oceanActive ? t('tools.manifestation.audio_stop') : t('tools.manifestation.audio_start')}
          </Button>
        </div>
      </motion.section>

      <div className="rounded-2xl border border-line bg-panel p-3 sm:p-4">
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setPracticeMode('quick')}
            data-testid="manifestation-mode-quick"
            className={`rounded-xl px-3 py-2 text-sm font-semibold transition-colors ${
              practiceMode === 'quick' ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
            }`}
          >
            {t('tools.manifestation.mode_quick')}
          </button>
          <button
            type="button"
            onClick={() => setPracticeMode('deep')}
            data-testid="manifestation-mode-deep"
            className={`rounded-xl px-3 py-2 text-sm font-semibold transition-colors ${
              practiceMode === 'deep' ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
            }`}
          >
            {t('tools.manifestation.mode_deep')}
          </button>
        </div>
      </div>

      {practiceMode === 'quick' ? (
        <Card>
          <h2 className="font-heading text-lg font-bold">{t('tools.manifestation.quick_title')}</h2>
          <p className="text-sm text-muted mt-1">{t('tools.manifestation.quick_desc')}</p>

          <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-accent">
            {t('tools.manifestation.quick_focus_label')}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {(['stability', 'confidence', 'calm'] as QuickFocus[]).map((focus) => {
              const active = quickFocus === focus;
              return (
                <button
                  key={focus}
                  type="button"
                  onClick={() => setQuickFocus(focus)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                    active ? 'bg-accent text-white' : 'bg-paper text-muted hover:text-ink'
                  }`}
                >
                  {t(`tools.manifestation.quick_focus_${focus}`)}
                </button>
              );
            })}
          </div>

          <div className="mt-4 rounded-xl border border-line bg-paper p-3">
            <p className="text-xs text-muted">{t('tools.manifestation.quick_preview_label')}</p>
            <p className="text-sm mt-1">{t(`tools.manifestation.quick_template_${quickFocus}`)}</p>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <Button onClick={addQuickAffirmation} data-testid="manifestation-quick-generate">
              {t('tools.manifestation.quick_apply')}
            </Button>
            <Button variant="ghost" onClick={() => setPracticeMode('deep')}>
              {t('tools.manifestation.mode_deep')}
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <Card>
            <h2 className="font-heading text-lg font-bold">{t('tools.manifestation.deep_title')}</h2>
            <p className="text-sm text-muted mt-1">{t('tools.manifestation.deep_desc')}</p>
          </Card>

          <Card>
            <h2 className="font-heading text-lg font-bold">{t('tools.manifestation.affirmation_title')}</h2>
            <p className="text-sm text-muted mt-1">{t('tools.manifestation.affirmation_desc')}</p>
            <div className="mt-3 flex gap-2">
              <input
                data-testid="manifestation-affirmation-input"
                value={affirmationInput}
                onChange={(e) => setAffirmationInput(e.target.value)}
                placeholder={t('tools.manifestation.affirmation_placeholder')}
                className="flex-1 rounded-xl border border-line bg-paper px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
              />
              <Button onClick={addAffirmation} disabled={!affirmationInput.trim()} data-testid="manifestation-add-affirmation">
                {t('common.add')}
              </Button>
            </div>
            <div className="mt-4 space-y-2">
              {affirmations.length === 0 ? (
                <p className="text-sm text-muted">{t('tools.manifestation.empty_affirmation')}</p>
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
            <h2 className="font-heading text-lg font-bold">{t('tools.manifestation.vision_title')}</h2>
            <p className="text-sm text-muted mt-1">{t('tools.manifestation.vision_desc')}</p>
            <div className="mt-3 grid gap-2">
              <input
                data-testid="manifestation-vision-title"
                value={visionTitle}
                onChange={(e) => setVisionTitle(e.target.value)}
                placeholder={t('tools.manifestation.vision_title_placeholder')}
                className="rounded-xl border border-line bg-paper px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
              />
              <textarea
                data-testid="manifestation-vision-note"
                value={visionNote}
                onChange={(e) => setVisionNote(e.target.value)}
                placeholder={t('tools.manifestation.vision_note_placeholder')}
                className="min-h-24 rounded-xl border border-line bg-paper px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
              />
              <Button onClick={addVisionCard} disabled={!visionTitle.trim() || !visionNote.trim()} data-testid="manifestation-save-vision">
                {t('common.save')}
              </Button>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {visionCards.length === 0 ? (
                <p className="text-sm text-muted">{t('tools.manifestation.empty_vision')}</p>
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
        </>
      )}
    </div>
  );
}
