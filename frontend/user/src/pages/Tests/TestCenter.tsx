import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getCatalog } from '../../api/tests';
import type { TestCatalogItem } from '../../types';
import Card from '../../components/Card/Card';
import Loading from '../../components/Loading/Loading';

const TEST_ICONS: Record<string, string> = {
  mbti: '🎭',
  big5: '⭐',
  attachment: '💕',
  love_language: '❤️',
  eq: '🧠',
  inner_child: '🧸',
  boundary: '🚧',
  mental_age: '🎂',
};

export default function TestCenter() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [catalog, setCatalog] = useState<Record<string, TestCatalogItem> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCatalog()
      .then(setCatalog)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading text={t('common.loading')} />;

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-heading text-3xl font-bold">{t('tests.title')}</h1>
        <p className="text-muted mt-1 mb-8">{t('tests.subtitle')}</p>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {catalog && Object.entries(catalog).map(([testId, item], i) => (
          <motion.div
            key={testId}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card hoverable onClick={() => navigate(`/tests/${testId}`)}>
              <div className="w-12 h-12 rounded-xl bg-warn-soft flex items-center justify-center text-2xl mb-3">
                {TEST_ICONS[testId] ?? '🧩'}
              </div>
              <h3 className="font-heading font-bold text-lg">{item.display_name}</h3>
              <p className="text-xs text-muted mt-2">
                {item.input_dimension_count} {t('tests.dimensions')}
              </p>
              <button className="mt-4 text-accent font-semibold text-sm hover:underline">
                {t('tests.start')} →
              </button>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
