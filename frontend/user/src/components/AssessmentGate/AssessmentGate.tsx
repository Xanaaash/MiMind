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
    <div className="max-w-2xl mx-auto py-4 sm:py-8 px-1 sm:px-0">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6 sm:mb-8"
      >
        <span className="text-4xl sm:text-5xl">📋</span>
        <h1 className="font-heading text-xl sm:text-2xl font-bold mt-3 sm:mt-4 px-2">
          {t('coach_gate.title')}
        </h1>
        <p className="text-muted mt-2 max-w-lg mx-auto text-sm sm:text-base px-2">
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
        className="mb-5 sm:mb-6"
      >
        <h2 className="text-xs sm:text-sm font-semibold text-accent uppercase tracking-wider mb-2 sm:mb-3">
          {t('coach_gate.mandatory')}
        </h2>
        <div className="grid gap-2 sm:gap-3">
          {MANDATORY_SCALES.map((s) => (
            <div
              key={s.id}
              className="flex items-center gap-3 sm:gap-4 bg-accent-soft/50 border border-accent/20 rounded-xl sm:rounded-2xl px-3 sm:px-5 py-3 sm:py-4"
            >
              <span className="text-xl sm:text-2xl">{s.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm">{t(`coach_gate.scale_${s.id}`)}</p>
                <p className="text-xs text-muted truncate sm:whitespace-normal">{t(`coach_gate.scale_${s.id}_desc`)}</p>
              </div>
              <span className="text-xs text-muted bg-white/80 px-2 py-1 rounded-lg shrink-0">
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
        className="mb-6 sm:mb-8"
      >
        <h2 className="text-xs sm:text-sm font-semibold text-muted uppercase tracking-wider mb-2 sm:mb-3">
          {t('coach_gate.optional')}
        </h2>
        <div className="grid gap-2 sm:gap-3">
          {OPTIONAL_SCALES.map((s) => (
            <div
              key={s.id}
              className="flex items-center gap-3 sm:gap-4 bg-cream/50 border border-line rounded-xl sm:rounded-2xl px-3 sm:px-5 py-3 sm:py-4"
            >
              <span className="text-xl sm:text-2xl">{s.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm">{t(`coach_gate.scale_${s.id}`)}</p>
                <p className="text-xs text-muted truncate sm:whitespace-normal">{t(`coach_gate.scale_${s.id}_desc`)}</p>
              </div>
              <span className="text-xs text-muted bg-white/80 px-2 py-1 rounded-lg shrink-0">
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
        <Button onClick={handleStart} className="px-6 sm:px-8 w-full sm:w-auto">
          {t('coach_gate.start_assessment')}
        </Button>
        <p className="text-xs text-muted mt-3">
          {t('coach_gate.time_estimate')}
        </p>
      </motion.div>
    </div>
  );
}
