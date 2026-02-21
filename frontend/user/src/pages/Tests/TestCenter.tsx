import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getCatalog } from '../../api/tests';
import type { TestCatalogItem } from '../../types';
import Card from '../../components/Card/Card';
import Skeleton from '../../components/Skeleton/Skeleton';
import { TEST_INTRO_KEYS, TEST_NAME_KEYS } from '../../utils/assessmentCopy';

const TEST_ICONS: Record<string, string> = {
  mbti: '🎭',
  '16p': '🧭',
  big5: '⭐',
  attachment: '💕',
  love_language: '❤️',
  stress_coping: '🧘',
  eq: '🧠',
  inner_child: '🧸',
  boundary: '🚧',
  psych_age: '🎂',
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

  if (loading) {
    return (
      <div aria-busy className="space-y-8">
        <div>
          <Skeleton className="h-10 w-56 mb-3" />
          <Skeleton className="h-5 w-72" />
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, idx) => (
            <Card key={idx}>
              <Skeleton className="w-12 h-12 mb-3" />
              <Skeleton className="h-6 w-40 mb-3" />
              <Skeleton className="h-4 w-24 mb-4" />
              <Skeleton className="h-4 w-28" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

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
              <h3 className="font-heading font-bold text-lg">
                {t(TEST_NAME_KEYS[testId] ?? '', { defaultValue: item.display_name || testId })}
              </h3>
              <p className="text-xs text-muted mt-2 leading-relaxed">
                {t(TEST_INTRO_KEYS[testId] ?? 'tests.intro.generic')}
              </p>
              <p className="text-xs text-muted mt-3">
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
