import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../Button/Button';

const ASSESSMENT_VALIDITY_DAYS = 30;

const MANDATORY_SCALES = [
  { id: 'phq9', icon: '🧠', items: 9 },
  { id: 'gad7', icon: '💭', items: 7 },
  { id: 'cssrs', icon: '🛡️', items: 6 },
];

const OPTIONAL_SCALES = [
  { id: 'pss10', icon: '📊', items: 10 },
];

export function isAssessmentExpired(): boolean {
  const ts = localStorage.getItem('mc_assessment_ts');
  if (!ts) return true;
  const elapsed = Date.now() - Number(ts);
  return elapsed > ASSESSMENT_VALIDITY_DAYS * 24 * 60 * 60 * 1000;
}

export function markAssessmentComplete(): void {
  localStorage.setItem('mc_assessment_ts', String(Date.now()));
}

interface Props {
  reason: 'missing' | 'expired';
}

export default function AssessmentGate({ reason }: Props) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleStart = () => {
    navigate('/onboarding?returnTo=/coach');
  };

  return (
    <div className="max-w-2xl mx-auto py-8">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <span className="text-5xl">📋</span>
        <h1 className="font-heading text-2xl font-bold mt-4">
          {t('coach_gate.title')}
        </h1>
        <p className="text-muted mt-2 max-w-lg mx-auto">
          {reason === 'expired'
            ? t('coach_gate.expired_desc')
            : t('coach_gate.missing_desc')}
        </p>
      </motion.div>

      {/* Mandatory */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6"
      >
        <h2 className="text-sm font-semibold text-accent uppercase tracking-wider mb-3">
          {t('coach_gate.mandatory')}
        </h2>
        <div className="grid gap-3">
          {MANDATORY_SCALES.map((s) => (
            <div
              key={s.id}
              className="flex items-center gap-4 bg-accent-soft/50 border border-accent/20 rounded-2xl px-5 py-4"
            >
              <span className="text-2xl">{s.icon}</span>
              <div className="flex-1">
                <p className="font-semibold text-sm">{t(`coach_gate.scale_${s.id}`)}</p>
                <p className="text-xs text-muted">{t(`coach_gate.scale_${s.id}_desc`)}</p>
              </div>
              <span className="text-xs text-muted bg-white/80 px-2 py-1 rounded-lg">
                {s.items} {t('scales.items')}
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Optional */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <h2 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
          {t('coach_gate.optional')}
        </h2>
        <div className="grid gap-3">
          {OPTIONAL_SCALES.map((s) => (
            <div
              key={s.id}
              className="flex items-center gap-4 bg-cream/50 border border-line rounded-2xl px-5 py-4"
            >
              <span className="text-2xl">{s.icon}</span>
              <div className="flex-1">
                <p className="font-semibold text-sm">{t(`coach_gate.scale_${s.id}`)}</p>
                <p className="text-xs text-muted">{t(`coach_gate.scale_${s.id}_desc`)}</p>
              </div>
              <span className="text-xs text-muted bg-white/80 px-2 py-1 rounded-lg">
                {s.items} {t('scales.items')}
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-center"
      >
        <Button onClick={handleStart} className="px-8">
          {t('coach_gate.start_assessment')}
        </Button>
        <p className="text-xs text-muted mt-3">
          {t('coach_gate.time_estimate')}
        </p>
      </motion.div>
    </div>
  );
}
