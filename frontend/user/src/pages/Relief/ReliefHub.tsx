import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useToolStore } from '../../stores/useToolStore';
import { setAmbientPlaybackVolume, stopAllAmbientPlayback, toggleAmbientPlayback } from '../../utils/ambientAudioService';

export default function ReliefHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const activeSoundIds = useToolStore((s) => s.ambient.activeSoundIds);
  const pinkNoiseActive = activeSoundIds.includes('pink_noise');

  const startPinkNoise = () => {
    setAmbientPlaybackVolume('pink_noise', 0.45);
    if (!pinkNoiseActive) {
      toggleAmbientPlayback('pink_noise');
    }
    navigate('/relief/sensory');
  };

  return (
    <div className="min-h-screen bg-[#090706] text-[#efe4dc] -mx-3 sm:-mx-4 -my-4 sm:-my-6 px-4 sm:px-6 py-6 sm:py-8">
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-3xl rounded-3xl border border-[#3a2a25] bg-[#120e0c] px-5 py-6 sm:px-6 sm:py-7"
      >
        <div className="text-xs uppercase tracking-[0.24em] text-[#d8a38d] font-semibold">
          {t('nav.rescue')}
        </div>
        <h1 className="mt-2 font-heading text-2xl sm:text-3xl font-bold">
          {t('relief.title')}
        </h1>
        <p className="mt-2 text-sm text-[#b9a7a0] max-w-2xl">
          {t('relief.minimal_hint')}
        </p>

        <button
          type="button"
          onClick={startPinkNoise}
          className="mt-5 w-full rounded-2xl border border-[#e07a60]/60 bg-[#241814] px-5 py-5 text-left transition-colors hover:bg-[#2f1f1a]"
        >
          <div className="text-xs uppercase tracking-wider text-[#c8aea3]">
            {t('relief.quick_pink_caption')}
          </div>
          <div className="mt-1 font-heading text-2xl font-bold">
            {pinkNoiseActive ? t('relief.quick_pink_running') : t('relief.quick_pink_start')}
          </div>
        </button>
      </motion.section>

      <section className="mx-auto mt-4 grid max-w-3xl grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => navigate('/relief/sensory')}
          className="rounded-2xl border border-[#3a2a25] bg-[#120e0c] px-5 py-6 text-left transition-colors hover:bg-[#1d1613]"
        >
          <div className="text-xs uppercase tracking-wider text-[#c8aea3]">{t('tools.sensory_title')}</div>
          <div className="mt-1 font-heading text-xl font-bold">{t('relief.quick_sensory_title')}</div>
        </button>

        <button
          type="button"
          onClick={() => navigate('/relief/breathing')}
          className="rounded-2xl border border-[#3a2a25] bg-[#120e0c] px-5 py-6 text-left transition-colors hover:bg-[#1d1613]"
        >
          <div className="text-xs uppercase tracking-wider text-[#c8aea3]">{t('tools.breathing_title')}</div>
          <div className="mt-1 font-heading text-xl font-bold">{t('relief.quick_breath_title')}</div>
        </button>

        {activeSoundIds.length > 0 && (
          <button
            type="button"
            onClick={stopAllAmbientPlayback}
            className="sm:col-span-2 rounded-2xl border border-[#5b2e28] bg-[#2a1614] px-5 py-4 text-sm font-semibold text-[#efb2a0] transition-colors hover:bg-[#3a1e1b]"
          >
            {t('relief.stop_all_audio')}
          </button>
        )}
      </section>
    </div>
  );
}
