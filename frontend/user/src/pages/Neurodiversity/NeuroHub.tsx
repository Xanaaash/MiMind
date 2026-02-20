import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Card from '../../components/Card/Card';
import { NEURO_SCALES } from '../../data/neuroScales';

export default function NeuroHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-heading text-3xl font-bold">{t('neuro.title')}</h1>
        <p className="text-muted mt-1 mb-2">{t('neuro.subtitle')}</p>
        <p className="text-xs text-muted mb-8 leading-relaxed">{t('neuro.intro')}</p>
      </motion.div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {NEURO_SCALES.map((scale, i) => (
          <motion.div
            key={scale.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <Card hoverable onClick={() => navigate(`/neurodiversity/${scale.id}`)}>
              <div className="flex items-start gap-4">
                <div className={`w-14 h-14 rounded-xl ${scale.color} flex items-center justify-center text-3xl shrink-0`}>
                  {scale.emoji}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-heading font-bold text-lg">{t(scale.nameKey)}</h3>
                  <p className="text-muted text-sm mt-1 line-clamp-2">{t(scale.descKey)}</p>
                  <div className="flex items-center gap-3 mt-3">
                    <span className="text-xs bg-cream px-2 py-0.5 rounded-md font-medium">
                      {scale.itemCount} {t('scales.items')}
                    </span>
                    <span className="text-accent font-semibold text-sm">{t('neuro.start')} →</span>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Info Section */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-10 bg-panel border border-line rounded-2xl p-5"
      >
        <h3 className="font-heading font-bold text-sm mb-2">🧠 {t('neuro.what_is_title')}</h3>
        <p className="text-xs text-muted leading-relaxed">{t('neuro.what_is_body')}</p>
      </motion.div>
    </div>
  );
}
