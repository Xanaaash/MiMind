import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import Button from '../Button/Button';

interface Props {
  scaleId: string;
  onAccept: () => void;
  onDecline?: () => void;
}

const NEURO_SCALES = new Set(['asrs', 'aq10', 'hsp', 'catq']);
const ACCEPTED_KEY = 'nd_disclaimer_accepted';

function wasAcceptedRecently(scaleId: string): boolean {
  try {
    const stored = JSON.parse(localStorage.getItem(ACCEPTED_KEY) ?? '{}');
    const ts = stored[scaleId];
    if (!ts) return false;
    return Date.now() - ts < 24 * 3600 * 1000;
  } catch { return false; }
}

function markAccepted(scaleId: string) {
  try {
    const stored = JSON.parse(localStorage.getItem(ACCEPTED_KEY) ?? '{}');
    stored[scaleId] = Date.now();
    localStorage.setItem(ACCEPTED_KEY, JSON.stringify(stored));
  } catch { /* ignore */ }
}

export function isNeurodiversityScale(scaleId: string): boolean {
  return NEURO_SCALES.has(scaleId.toLowerCase());
}

export default function NeurodiversityDisclaimer({ scaleId, onAccept, onDecline }: Props) {
  const { t } = useTranslation();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (isNeurodiversityScale(scaleId) && !wasAcceptedRecently(scaleId)) {
      setVisible(true);
    } else {
      onAccept();
    }
  }, [scaleId, onAccept]);

  const handleAccept = () => {
    markAccepted(scaleId);
    setVisible(false);
    onAccept();
  };

  const handleDecline = () => {
    setVisible(false);
    onDecline?.();
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        >
          <motion.div
            initial={{ scale: 0.92, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.92, opacity: 0 }}
            className="bg-panel border border-line rounded-2xl shadow-lg max-w-md w-full p-6 sm:p-8"
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🧠</span>
              <div>
                <h2 className="font-heading font-bold text-lg">{t('nd_disclaimer.title')}</h2>
                <p className="text-[11px] font-semibold uppercase tracking-wide text-warn mt-1">
                  {t('nd_disclaimer.legal_review_badge')}
                </p>
              </div>
            </div>

            <div className="space-y-3 text-sm text-muted leading-relaxed">
              <p>{t('nd_disclaimer.p1')}</p>
              <p>{t('nd_disclaimer.p2')}</p>
              <p className="font-semibold text-ink">{t('nd_disclaimer.p3')}</p>
            </div>

            <div className="mt-6 bg-warn-soft border border-warn/30 rounded-xl p-3">
              <p className="text-xs text-warn leading-relaxed">{t('nd_disclaimer.seek_help')}</p>
            </div>

            <p className="text-[11px] text-muted mt-3 leading-relaxed">
              {t('nd_disclaimer.legal_review_note')}
            </p>

            <div className="flex gap-3 mt-6">
              <Button onClick={handleAccept} className="flex-1">
                {t('nd_disclaimer.accept')}
              </Button>
              <Button variant="ghost" onClick={handleDecline} className="flex-1">
                {t('nd_disclaimer.decline')}
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
