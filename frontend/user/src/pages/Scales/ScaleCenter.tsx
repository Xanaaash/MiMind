import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getCatalog, getProfessionalLibrary } from '../../api/scales';
import type { ProfessionalScaleLibraryItem, ScaleCatalogItem } from '../../types';
import Card from '../../components/Card/Card';
import Skeleton from '../../components/Skeleton/Skeleton';
import { SCALE_INTRO_KEYS, SCALE_NAME_KEYS, SCALE_PURPOSE_KEYS } from '../../utils/assessmentCopy';

const SCALE_ICONS: Record<string, string> = {
  phq9: '🧠',
  gad7: '😰',
  pss10: '📊',
  cssrs: '🛡️',
  scl90: '📋',
  who5: '🌤️',
  isi7: '🌙',
  swls5: '😊',
  ucla3: '🤝',
  cdrisc10: '🧗',
  phq15: '🩺',
};

export default function ScaleCenter() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [catalog, setCatalog] = useState<Record<string, ScaleCatalogItem> | null>(null);
  const [professionalLibrary, setProfessionalLibrary] = useState<Record<string, ProfessionalScaleLibraryItem> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([getCatalog(), getProfessionalLibrary()])
      .then(([catalogResult, libraryResult]) => {
        if (catalogResult.status === 'fulfilled') {
          setCatalog(catalogResult.value);
        }
        if (libraryResult.status === 'fulfilled') {
          setProfessionalLibrary(libraryResult.value);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const localeKey = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';

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
              <p className="text-xs text-muted mt-2 leading-relaxed">
                <span className="font-semibold text-ink">{t('scales.purpose_label')}: </span>
                {t(SCALE_PURPOSE_KEYS[scaleId] ?? 'scales.purpose.generic')}
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

      {professionalLibrary ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-10">
          <h2 className="font-heading text-2xl font-bold">{t('scales.professional_library_title')}</h2>
          <p className="text-muted mt-1 mb-5">{t('scales.professional_library_subtitle')}</p>
          <div className="grid md:grid-cols-2 gap-5">
            {Object.entries(professionalLibrary).map(([scaleId, item], i) => {
              const name = item.names[localeKey] ?? item.names['en-US'] ?? scaleId.toUpperCase();
              const useCase = item.use_cases[localeKey] ?? item.use_cases['en-US'] ?? '';
              const scoring = item.scoring_logic[localeKey] ?? item.scoring_logic['en-US'] ?? '';
              const disclaimer = item.disclaimer[localeKey] ?? item.disclaimer['en-US'] ?? '';
              const firstRef = item.references?.[0];
              const canOpen = item.interactive_available && Boolean(catalog?.[scaleId]);
              return (
                <motion.div
                  key={scaleId}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                >
                  <Card hoverable={canOpen} onClick={canOpen ? () => navigate(`/scales/${scaleId}`) : undefined}>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-heading font-bold text-lg">{name}</h3>
                        <p className="text-xs text-muted mt-1 uppercase tracking-wide">{scaleId}</p>
                      </div>
                      <span className="text-xs rounded-full bg-calm-soft px-2 py-1">{item.item_count} {t('scales.items')}</span>
                    </div>
                    <p className="text-sm text-muted mt-3">
                      <span className="font-semibold text-ink">{t('scales.use_case_label')}: </span>
                      {useCase}
                    </p>
                    <p className="text-sm text-muted mt-2">
                      <span className="font-semibold text-ink">{t('scales.scoring_label')}: </span>
                      {scoring}
                    </p>
                    <p className="text-sm text-muted mt-2">
                      <span className="font-semibold text-ink">{t('scales.disclaimer_label')}: </span>
                      {disclaimer}
                    </p>
                    {firstRef ? (
                      <a
                        href={firstRef.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex mt-3 text-sm text-accent font-semibold hover:underline"
                      >
                        {t('scales.reference_label')}
                      </a>
                    ) : null}
                    {canOpen ? (
                      <button className="mt-3 text-accent font-semibold text-sm hover:underline">
                        {t('scales.start')} →
                      </button>
                    ) : null}
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      ) : null}
    </div>
  );
}
