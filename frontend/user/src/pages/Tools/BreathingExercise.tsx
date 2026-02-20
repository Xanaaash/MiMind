import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { completeBreathing } from '../../api/tools';
import { useAuthStore } from '../../stores/auth';
import Button from '../../components/Button/Button';

type Phase = 'idle' | 'inhale' | 'hold' | 'exhale' | 'done';

const INHALE_DURATION = 4;
const HOLD_DURATION = 7;
const EXHALE_DURATION = 8;

export default function BreathingExercise() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const userId = useAuthStore((s) => s.userId);

  const [phase, setPhase] = useState<Phase>('idle');
  const [totalCycles, setTotalCycles] = useState(4);
  const [currentCycle, setCurrentCycle] = useState(0);
  const [secondsInPhase, setSecondsInPhase] = useState(0);

  const phaseConfig: Record<string, { label: string; duration: number; scale: number }> = {
    inhale: { label: t('tools.inhale'), duration: INHALE_DURATION, scale: 1.4 },
    hold: { label: t('tools.hold'), duration: HOLD_DURATION, scale: 1.4 },
    exhale: { label: t('tools.exhale'), duration: EXHALE_DURATION, scale: 1.0 },
  };

  const startExercise = useCallback(() => {
    setPhase('inhale');
    setCurrentCycle(1);
    setSecondsInPhase(0);
  }, []);

  useEffect(() => {
    if (phase === 'idle' || phase === 'done') return;

    const config = phaseConfig[phase];
    if (!config) return;

    const timer = setInterval(() => {
      setSecondsInPhase((prev) => {
        const next = prev + 1;
        if (next >= config.duration) {
          if (phase === 'inhale') {
            setPhase('hold');
          } else if (phase === 'hold') {
            setPhase('exhale');
          } else if (phase === 'exhale') {
            if (currentCycle >= totalCycles) {
              setPhase('done');
              if (userId) {
                completeBreathing(userId, totalCycles).catch(() => {});
              }
            } else {
              setCurrentCycle((c) => c + 1);
              setPhase('inhale');
            }
          }
          return 0;
        }
        return next;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [phase, currentCycle, totalCycles, userId]);

  const currentConfig = phase !== 'idle' && phase !== 'done' ? phaseConfig[phase] : null;

  return (
    <div className="max-w-md mx-auto text-center py-8">
      <h1 className="font-heading text-2xl font-bold mb-2">{t('tools.breathing_title')}</h1>
      <p className="text-muted text-sm mb-8">4-7-8 {t('tools.breathing_desc')}</p>

      {/* Circle animation */}
      <div className="relative w-56 h-56 mx-auto mb-8">
        <motion.div
          className="absolute inset-0 rounded-full bg-safe-soft border-4 border-safe flex items-center justify-center"
          animate={{
            scale: currentConfig?.scale ?? 1.0,
          }}
          transition={{
            duration: currentConfig?.duration ?? 0.5,
            ease: 'easeInOut',
          }}
        >
          <div className="text-center">
            {phase === 'idle' && <span className="text-4xl">🌬️</span>}
            {phase === 'done' && <span className="text-4xl">✅</span>}
            {currentConfig && (
              <>
                <p className="font-heading font-bold text-xl text-safe">{currentConfig.label}</p>
                <p className="text-3xl font-bold text-ink mt-1">
                  {currentConfig.duration - secondsInPhase}
                </p>
              </>
            )}
          </div>
        </motion.div>
      </div>

      {phase === 'idle' && (
        <div className="space-y-4">
          <div className="flex items-center justify-center gap-3">
            <span className="text-sm text-muted">{t('tools.cycles')}:</span>
            <input
              type="range"
              min={1}
              max={10}
              value={totalCycles}
              onChange={(e) => setTotalCycles(Number(e.target.value))}
              className="w-32 accent-safe"
            />
            <span className="font-bold w-8">{totalCycles}</span>
          </div>
          <Button onClick={startExercise} size="lg">{t('tools.start')}</Button>
        </div>
      )}

      {(phase === 'inhale' || phase === 'hold' || phase === 'exhale') && (
        <p className="text-muted text-sm">
          {t('tools.cycles')} {currentCycle} / {totalCycles}
        </p>
      )}

      {phase === 'done' && (
        <div className="space-y-4">
          <p className="text-safe font-semibold text-lg">{t('tools.complete')} 🎉</p>
          <div className="flex gap-3 justify-center">
            <Button variant="ghost" onClick={() => setPhase('idle')}>{t('common.retry')}</Button>
            <Button onClick={() => navigate('/tools')}>{t('common.back')}</Button>
          </div>
        </div>
      )}
    </div>
  );
}
