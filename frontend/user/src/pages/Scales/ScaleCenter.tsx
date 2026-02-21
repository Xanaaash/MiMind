import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getCatalog } from '../../api/scales';
import type { ScaleCatalogItem } from '../../types';
import Card from '../../components/Card/Card';
import Skeleton from '../../components/Skeleton/Skeleton';
import { SCALE_INTRO_KEYS, SCALE_NAME_KEYS } from '../../utils/assessmentCopy';

const SCALE_ICONS: Record<string, string> = {
  phq9: '🧠',
  gad7: '😰',
  pss10: '📊',
  cssrs: '🛡️',
  scl90: '📋',
};

export default function ScaleCenter() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [catalog, setCatalog] = useState<Record<string, ScaleCatalogItem> | null>(null);
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
          <Skeleton className="h-5 w-80" />
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, idx) => (
            <Card key={idx}>
              <Skeleton className="w-12 h-12 mb-3" />
              <Skeleton className="h-6 w-24 mb-2" />
              <Skeleton className="h-4 w-44 mb-2" />
              <Skeleton className="h-4 w-20 mb-4" />
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
        <h1 className="font-heading text-3xl font-bold">{t('scales.title')}</h1>
        <p className="text-muted mt-1 mb-8">{t('scales.subtitle')}</p>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {catalog && Object.entries(catalog).map(([scaleId, item], i) => (
          <motion.div
            key={scaleId}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card hoverable onClick={() => navigate(`/scales/${scaleId}`)}>
              <div className="w-12 h-12 rounded-xl bg-calm-soft flex items-center justify-center text-2xl mb-3">
                {SCALE_ICONS[scaleId] ?? '📋'}
              </div>
              <h3 className="font-heading font-bold text-lg">
                {t(SCALE_NAME_KEYS[scaleId] ?? '', { defaultValue: item.display_name || scaleId.toUpperCase() })}
              </h3>
              <p className="text-muted text-xs mt-1 uppercase tracking-wide">{scaleId}</p>
              <p className="text-xs text-muted mt-2 leading-relaxed">
                {t(SCALE_INTRO_KEYS[scaleId] ?? 'scales.intro.generic')}
              </p>
              <p className="text-xs text-muted mt-3">
                {item.item_count} {t('scales.items')}
              </p>
              <button className="mt-4 text-accent font-semibold text-sm hover:underline">
                {t('scales.start')} →
              </button>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
