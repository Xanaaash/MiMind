import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { completeBreathing } from '../../api/tools';
import { useAuthStore } from '../../stores/auth';
import Button from '../../components/Button/Button';

type Phase = 'idle' | 'inhale' | 'hold' | 'exhale' | 'hold2' | 'done';

interface BreathingMode {
  id: string;
  nameKey: string;
  descKey: string;
  emoji: string;
  color: string;
  phases: Array<{ phase: Phase; duration: number; scale: number }>;
}

const MODES: BreathingMode[] = [
  {
    id: '478',
    nameKey: 'tools.mode_478',
    descKey: 'tools.mode_478_desc',
    emoji: '😴',
    color: 'bg-calm-soft',
    phases: [
      { phase: 'inhale', duration: 4, scale: 1.4 },
      { phase: 'hold', duration: 7, scale: 1.4 },
      { phase: 'exhale', duration: 8, scale: 1.0 },
    ],
  },
  {
    id: 'box',
    nameKey: 'tools.mode_box',
    descKey: 'tools.mode_box_desc',
    emoji: '🧠',
    color: 'bg-safe-soft',
    phases: [
      { phase: 'inhale', duration: 4, scale: 1.3 },
      { phase: 'hold', duration: 4, scale: 1.3 },
      { phase: 'exhale', duration: 4, scale: 1.0 },
      { phase: 'hold2', duration: 4, scale: 1.0 },
    ],
  },
  {
    id: 'relax',
    nameKey: 'tools.mode_relax',
    descKey: 'tools.mode_relax_desc',
    emoji: '🌿',
    color: 'bg-accent-soft',
    phases: [
      { phase: 'inhale', duration: 5, scale: 1.3 },
      { phase: 'exhale', duration: 5, scale: 1.0 },
    ],
  },
];

export default function BreathingExercise() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const userId = useAuthStore((s) => s.userId);

  const [selectedMode, setSelectedMode] = useState<BreathingMode>(MODES[0]);
  const [phase, setPhase] = useState<Phase>('idle');
  const [totalCycles, setTotalCycles] = useState(4);
  const [currentCycle, setCurrentCycle] = useState(0);
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [secondsInPhase, setSecondsInPhase] = useState(0);

  const currentPhaseConfig = phase !== 'idle' && phase !== 'done'
    ? selectedMode.phases[phaseIndex]
    : null;

  const phaseLabel = (p: Phase): string => {
    if (p === 'hold2') return t('tools.hold');
    return t(`tools.${p}`);
  };

  const startExercise = useCallback(() => {
    setPhaseIndex(0);
    setPhase(selectedMode.phases[0].phase);
    setCurrentCycle(1);
    setSecondsInPhase(0);
  }, [selectedMode]);

  useEffect(() => {
    if (phase === 'idle' || phase === 'done') return;

    const config = selectedMode.phases[phaseIndex];
    if (!config) return;

    const timer = setInterval(() => {
      setSecondsInPhase((prev) => {
        const next = prev + 1;
        if (next >= config.duration) {
          const nextIdx = phaseIndex + 1;
          if (nextIdx < selectedMode.phases.length) {
            setPhaseIndex(nextIdx);
            setPhase(selectedMode.phases[nextIdx].phase);
          } else {
            if (currentCycle >= totalCycles) {
              setPhase('done');
              if (userId) {
                completeBreathing(userId, totalCycles).catch(() => {});
              }
            } else {
              setCurrentCycle((c) => c + 1);
              setPhaseIndex(0);
              setPhase(selectedMode.phases[0].phase);
            }
          }
          return 0;
        }
        return next;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [phase, phaseIndex, currentCycle, totalCycles, userId, selectedMode]);

  const circleColor: Record<string, string> = {
    inhale: 'border-safe bg-safe-soft',
    hold: 'border-calm bg-calm-soft',
    hold2: 'border-calm bg-calm-soft',
    exhale: 'border-accent bg-accent-soft',
  };

  return (
    <div className="max-w-lg mx-auto text-center py-8">
      <h1 className="font-heading text-2xl font-bold mb-2">{t('tools.breathing_title')}</h1>
      <p className="text-muted text-sm mb-8">{t('tools.breathing_desc')}</p>

      {/* Mode selector */}
      <AnimatePresence mode="wait">
        {phase === 'idle' && (
          <motion.div
            key="mode-select"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="grid gap-3 mb-8">
              {MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setSelectedMode(mode)}
                  className={`
                    w-full text-left rounded-2xl border-2 p-4 transition-all cursor-pointer
                    ${selectedMode.id === mode.id
                      ? 'border-accent bg-accent-soft shadow-md scale-[1.02]'
                      : `border-line ${mode.color} hover:border-accent/30`
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{mode.emoji}</span>
                    <div>
                      <p className="font-heading font-bold">{t(mode.nameKey)}</p>
                      <p className="text-muted text-sm">{t(mode.descKey)}</p>
                    </div>
                  </div>
                  <div className="flex gap-1.5 mt-2 ml-10">
                    {mode.phases.map((p, i) => (
                      <span key={i} className="text-xs bg-white/60 px-2 py-0.5 rounded-full text-muted font-medium">
                        {phaseLabel(p.phase)} {p.duration}s
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>

            <div className="flex items-center justify-center gap-3 mb-6">
              <span className="text-sm text-muted">{t('tools.cycles')}:</span>
              <input
                type="range"
                min={1}
                max={10}
                value={totalCycles}
                onChange={(e) => setTotalCycles(Number(e.target.value))}
                className="w-32 accent-accent"
              />
              <span className="font-bold text-lg w-8">{totalCycles}</span>
            </div>
            <Button onClick={startExercise} size="lg">{t('tools.start')}</Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active breathing animation */}
      {(phase !== 'idle' && phase !== 'done') && currentPhaseConfig && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="relative w-56 h-56 mx-auto mb-8">
            <motion.div
              className={`absolute inset-0 rounded-full border-4 flex items-center justify-center ${circleColor[phase] ?? 'border-safe bg-safe-soft'}`}
              animate={{ scale: currentPhaseConfig.scale }}
              transition={{
                duration: currentPhaseConfig.duration,
                ease: 'easeInOut',
              }}
            >
              <div className="text-center">
                <p className="font-heading font-bold text-xl text-ink">{phaseLabel(phase)}</p>
                <p className="text-3xl font-bold text-accent mt-1">
                  {currentPhaseConfig.duration - secondsInPhase}
                </p>
              </div>
            </motion.div>
          </div>

          {/* Phase indicators */}
          <div className="flex justify-center gap-2 mb-4">
            {selectedMode.phases.map((_, i) => (
              <div
                key={i}
                className={`
                  w-3 h-3 rounded-full transition-colors
                  ${i === phaseIndex ? 'bg-accent scale-125' : 'bg-line'}
                `}
              />
            ))}
          </div>

          <p className="text-muted text-sm mb-4">
            {t('tools.cycles')} {currentCycle} / {totalCycles}
          </p>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => { setPhase('idle'); setPhaseIndex(0); setSecondsInPhase(0); }}
          >
            {t('tools.stop')}
          </Button>
        </motion.div>
      )}

      {/* Done */}
      {phase === 'done' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="w-24 h-24 mx-auto rounded-full bg-safe-soft border-4 border-safe flex items-center justify-center">
            <span className="text-4xl">✅</span>
          </div>
          <p className="text-safe font-heading font-bold text-xl">{t('tools.complete')}</p>
          <p className="text-muted text-sm">
            {totalCycles} {t('tools.cycles')} · {selectedMode.phases.map(p => `${p.duration}s`).join('-')}
          </p>
          <div className="flex gap-3 justify-center mt-6">
            <Button variant="ghost" onClick={() => { setPhase('idle'); setPhaseIndex(0); }}>
              {t('common.retry')}
            </Button>
            <Button onClick={() => navigate('/tools')}>{t('common.back')}</Button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
