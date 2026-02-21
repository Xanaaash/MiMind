import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  SENSORY_SOUNDS,
  playAmbient,
  stopAmbient,
  setVolume,
  isPlaying,
  getCurrentSound,
  type AmbientSoundId,
} from '../../utils/ambientAudio';

const BREATH_PHASES = [
  { key: 'inhale', duration: 5, scale: 1.35 },
  { key: 'hold', duration: 3, scale: 1.35 },
  { key: 'exhale', duration: 7, scale: 1 },
  { key: 'rest', duration: 2, scale: 1 },
];

const GROUNDING_STEPS = [
  { sense: 'see', count: 5, emoji: '👁️' },
  { sense: 'touch', count: 4, emoji: '✋' },
  { sense: 'hear', count: 3, emoji: '👂' },
  { sense: 'smell', count: 2, emoji: '👃' },
  { sense: 'taste', count: 1, emoji: '👅' },
];

export default function SensoryRelief() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [activeSound, setActiveSound] = useState<AmbientSoundId | null>(null);
  const [volume, setVolumeState] = useState(0.6);
  const [breathActive, setBreathActive] = useState(false);
  const [phaseIdx, setPhaseIdx] = useState(0);
  const [phaseTime, setPhaseTime] = useState(0);
  const [groundingStep, setGroundingStep] = useState(-1);
  const breathTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      stopAmbient();
      if (breathTimerRef.current) clearInterval(breathTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!breathActive) {
      if (breathTimerRef.current) clearInterval(breathTimerRef.current);
      return;
    }

    setPhaseIdx(0);
    setPhaseTime(0);

    return () => {
      if (breathTimerRef.current) clearInterval(breathTimerRef.current);
    };
  }, [breathActive]);

  useEffect(() => {
    if (!breathActive) return;
    if (breathTimerRef.current) clearInterval(breathTimerRef.current);

    breathTimerRef.current = setInterval(() => {
      setPhaseTime((prev) => prev + 1);
    }, 1000);

    return () => {
      if (breathTimerRef.current) clearInterval(breathTimerRef.current);
    };
  }, [breathActive, phaseIdx]);

  useEffect(() => {
    if (!breathActive) return;
    const currentPhase = BREATH_PHASES[phaseIdx];
    if (phaseTime >= currentPhase.duration) {
      setPhaseTime(0);
      setPhaseIdx((pi) => (pi + 1) % BREATH_PHASES.length);
    }
  }, [phaseTime, phaseIdx, breathActive]);

  const handleToggleNoise = useCallback((soundId: AmbientSoundId) => {
    if (isPlaying() && getCurrentSound() === soundId) {
      stopAmbient();
      setActiveSound(null);
    } else {
      playAmbient(soundId, volume);
      setActiveSound(soundId);
    }
  }, [volume]);

  const handleVolumeChange = useCallback((v: number) => {
    setVolumeState(v);
    setVolume(v);
  }, []);

  const phase = BREATH_PHASES[phaseIdx];

  return (
    <div className="min-h-screen bg-[#0d0a09] text-[#e8ddd6] -mx-3 sm:-mx-4 -my-4 sm:-my-6 px-4 sm:px-6 py-6 sm:py-8">
      {/* Header */}
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6 sm:mb-8">
          <button
            onClick={() => navigate('/relief')}
            className="text-sm text-[#a89890] hover:text-[#e8ddd6] transition-colors"
          >
            ← {t('sensory.back')}
          </button>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8 sm:mb-10"
        >
          <span className="text-4xl sm:text-5xl">🛡️</span>
          <h1 className="font-heading text-xl sm:text-2xl font-bold mt-3">
            {t('sensory.title')}
          </h1>
          <p className="text-[#a89890] mt-2 text-sm sm:text-base max-w-md mx-auto">
            {t('sensory.subtitle')}
          </p>
        </motion.div>

        {/* Noise Selection */}
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 sm:mb-10"
        >
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#a89890] mb-3">
            {t('sensory.noise_title')}
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {SENSORY_SOUNDS.map((s) => {
              const isActive = activeSound === s.id;
              return (
                <button
                  key={s.id}
                  onClick={() => handleToggleNoise(s.id)}
                  className={`
                    flex flex-col items-center gap-2 py-5 rounded-2xl border-2 transition-all
                    ${isActive
                      ? 'border-[#e07a60] bg-[#e07a60]/10 scale-[1.02] shadow-lg shadow-[#e07a60]/10'
                      : 'border-[#3d2a26]/40 bg-[#1a1210] hover:border-[#e07a60]/30'
                    }
                  `}
                >
                  <span className="text-3xl">{s.emoji}</span>
                  <span className="text-sm font-semibold">{t(s.nameKey)}</span>
                  {isActive && (
                    <span className="text-xs text-[#e07a60]">{t('sensory.playing')}</span>
                  )}
                </button>
              );
            })}
          </div>

          <AnimatePresence>
            {activeSound && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 overflow-hidden"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs text-[#a89890]">🔈</span>
                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.01}
                    value={volume}
                    onChange={(e) => handleVolumeChange(Number(e.target.value))}
                    className="flex-1 accent-[#e07a60] h-1.5"
                  />
                  <span className="text-xs text-[#a89890]">🔊</span>
                  <span className="text-xs text-[#a89890] w-8 text-right">
                    {Math.round(volume * 100)}%
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.section>

        {/* Dark Breathing Animation */}
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8 sm:mb-10"
        >
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#a89890] mb-4">
            {t('sensory.breath_title')}
          </h2>

          <div className="flex flex-col items-center">
            {/* Circle */}
            <div className="relative w-48 h-48 sm:w-56 sm:h-56 flex items-center justify-center mb-6">
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-[#e07a60]/30"
                animate={{
                  scale: breathActive ? phase.scale : 1,
                  borderColor: breathActive
                    ? phase.key === 'inhale' ? 'rgba(224,122,96,0.6)' : 'rgba(224,122,96,0.2)'
                    : 'rgba(224,122,96,0.3)',
                }}
                transition={{ duration: phase.duration, ease: 'easeInOut' }}
              />
              <motion.div
                className="absolute inset-4 rounded-full bg-[#e07a60]/5"
                animate={{
                  scale: breathActive ? phase.scale : 1,
                  backgroundColor: breathActive
                    ? phase.key === 'inhale' ? 'rgba(224,122,96,0.12)' : 'rgba(224,122,96,0.04)'
                    : 'rgba(224,122,96,0.05)',
                }}
                transition={{ duration: phase.duration, ease: 'easeInOut' }}
              />
              <div className="text-center z-10">
                {breathActive ? (
                  <>
                    <p className="text-lg font-heading font-bold text-[#e07a60]">
                      {t(`sensory.breath_${phase.key}`)}
                    </p>
                    <p className="text-3xl font-mono font-bold mt-1">
                      {phase.duration - phaseTime}
                    </p>
                  </>
                ) : (
                  <p className="text-sm text-[#a89890]">{t('sensory.breath_ready')}</p>
                )}
              </div>
            </div>

            {/* Progress dots */}
            {breathActive && (
              <div className="flex gap-2 mb-4">
                {BREATH_PHASES.map((p, i) => (
                  <div
                    key={p.key}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      i === phaseIdx ? 'bg-[#e07a60]' : 'bg-[#3d2a26]'
                    }`}
                  />
                ))}
              </div>
            )}

            <button
              onClick={() => {
                setBreathActive(!breathActive);
                if (breathActive) {
                  setPhaseIdx(0);
                  setPhaseTime(0);
                }
              }}
              className={`
                px-6 py-2.5 rounded-xl text-sm font-semibold transition-all
                ${breathActive
                  ? 'bg-[#3d2a26] text-[#e07a60] hover:bg-[#4d3a36]'
                  : 'bg-[#e07a60] text-white hover:bg-[#f08a70]'
                }
              `}
            >
              {breathActive ? t('sensory.breath_stop') : t('sensory.breath_start')}
            </button>
          </div>
        </motion.section>

        {/* 5-4-3-2-1 Grounding */}
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8 sm:mb-10"
        >
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#a89890] mb-2">
            {t('sensory.grounding_title')}
          </h2>
          <p className="text-xs text-[#a89890] mb-4">
            {t('sensory.grounding_desc')}
          </p>

          <div className="space-y-3">
            {GROUNDING_STEPS.map((step, i) => {
              const isCurrentStep = groundingStep === i;
              const isDone = groundingStep > i;
              return (
                <motion.button
                  key={step.sense}
                  onClick={() => setGroundingStep(isDone ? -1 : i === groundingStep ? i + 1 : i)}
                  className={`
                    w-full text-left flex items-center gap-4 px-4 py-3.5 rounded-xl border transition-all
                    ${isDone
                      ? 'border-[#5cb87e]/40 bg-[#5cb87e]/10'
                      : isCurrentStep
                        ? 'border-[#e07a60]/50 bg-[#e07a60]/10 scale-[1.01]'
                        : 'border-[#3d2a26]/30 bg-[#1a1210] hover:border-[#3d2a26]/60'
                    }
                  `}
                  animate={{ opacity: isDone ? 0.6 : 1 }}
                >
                  <span className="text-2xl">{step.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-semibold ${isDone ? 'line-through text-[#a89890]' : ''}`}>
                      {step.count} {t(`sensory.ground_${step.sense}`)}
                    </p>
                    <p className="text-xs text-[#a89890] mt-0.5">
                      {t(`sensory.ground_${step.sense}_hint`)}
                    </p>
                  </div>
                  {isDone && <span className="text-[#5cb87e] text-lg">✓</span>}
                  {isCurrentStep && (
                    <span className="text-xs text-[#e07a60] font-medium">{t('sensory.tap_done')}</span>
                  )}
                </motion.button>
              );
            })}
          </div>

          {groundingStep >= GROUNDING_STEPS.length && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mt-6"
            >
              <p className="text-[#5cb87e] font-semibold">{t('sensory.grounding_done')}</p>
              <button
                onClick={() => setGroundingStep(-1)}
                className="text-xs text-[#a89890] mt-2 hover:text-[#e8ddd6] transition-colors"
              >
                {t('sensory.grounding_reset')}
              </button>
            </motion.div>
          )}
        </motion.section>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-center text-xs text-[#a89890]/60 pb-8"
        >
          <p>{t('sensory.disclaimer')}</p>
        </motion.div>
      </div>
    </div>
  );
}
