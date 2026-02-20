import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import Card from '../../components/Card/Card';
import { loadCoachHistory } from '../../utils/coachHistory';

const STYLE_KEY_MAP: Record<string, string> = {
  warm_guide: 'coach.style_warm',
  rational_analysis: 'coach.style_rational',
  deep_exploration: 'coach.style_deep',
  mindfulness_guide: 'coach.style_mindful',
  action_coach: 'coach.style_action',
};

export default function CoachHistoryPage() {
  const { t } = useTranslation();
  const userId = useAuthStore((state) => state.userId);

  const items = useMemo(() => {
    if (!userId) return [];
    return loadCoachHistory(userId);
  }, [userId]);

  return (
    <div className="max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
        <h1 className="font-heading text-3xl font-bold">{t('coach.history_title')}</h1>
        <p className="text-muted mt-1">{t('coach.history_subtitle')}</p>
      </motion.div>

      {items.length === 0 ? (
        <Card className="text-center py-10">
          <p className="text-muted">{t('coach.history_empty')}</p>
          <Link to="/coach" className="inline-block mt-4 text-accent font-semibold hover:underline">
            {t('coach.back_to_chat')}
          </Link>
        </Card>
      ) : (
        <div className="space-y-4">
          {items.map((item, index) => (
            <motion.div
              key={item.session_id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04 }}
            >
              <Card>
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-accent">
                    {t(STYLE_KEY_MAP[item.style_id] ?? 'coach.title')}
                  </p>
                  <p className="text-xs text-muted">{new Date(item.ended_at).toLocaleString()}</p>
                </div>
                <p className="text-sm text-ink mt-3 leading-relaxed">{item.summary}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
