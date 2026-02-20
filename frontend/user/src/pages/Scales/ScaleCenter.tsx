import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getCatalog } from '../../api/scales';
import type { ScaleCatalogItem } from '../../types';
import Card from '../../components/Card/Card';
import Loading from '../../components/Loading/Loading';

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

  if (loading) return <Loading text={t('common.loading')} />;

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
              <h3 className="font-heading font-bold text-lg uppercase">{scaleId}</h3>
              <p className="text-muted text-sm mt-1">{item.display_name}</p>
              <p className="text-xs text-muted mt-2">
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
