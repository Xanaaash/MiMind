import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/Card/Card';

export default function MindfulnessHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="space-y-5">
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-line bg-panel px-5 py-6 sm:px-6 sm:py-7"
      >
        <div className="text-xs uppercase tracking-[0.2em] text-accent font-semibold">
          {t('nav.mindfulness')}
        </div>
        <h1 className="mt-2 font-heading text-2xl sm:text-3xl font-bold text-ink">
          {t('tools.mindfulness.title')}
        </h1>
        <p className="mt-2 text-sm text-muted max-w-2xl">
          {t('tools.mindfulness.subtitle')}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="rounded-full border border-line bg-paper px-3 py-1 text-xs text-muted">
            {t('tools.mindfulness.quick_title')}
          </span>
          <span className="rounded-full border border-line bg-paper px-3 py-1 text-xs text-muted">
            {t('tools.mindfulness.deep_title')}
          </span>
        </div>
      </motion.section>

      <section className="rounded-3xl border border-line bg-panel p-4 sm:p-5">
        <h2 className="font-heading text-xl font-bold">{t('tools.mindfulness.quick_title')}</h2>
        <p className="text-sm text-muted mt-1">{t('tools.mindfulness.quick_desc')}</p>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card
            hoverable
            onClick={() => navigate('/mindfulness/meditation')}
            data-testid="mindfulness-entry-meditation-quick"
          >
            <div className="text-sm text-muted">{t('tools.mindfulness.quick_badge')}</div>
            <div className="mt-1 text-xl font-heading font-bold">{t('tools.mindfulness.meditation_title')}</div>
            <p className="mt-1 text-sm text-muted">{t('tools.mindfulness.meditation_desc')}</p>
          </Card>

          <Card
            hoverable
            onClick={() => navigate('/mindfulness/manifestation?mode=quick')}
            data-testid="mindfulness-entry-manifestation-quick"
          >
            <div className="text-sm text-muted">{t('tools.mindfulness.quick_badge')}</div>
            <div className="mt-1 text-xl font-heading font-bold">{t('tools.manifestation.title')}</div>
            <p className="mt-1 text-sm text-muted">{t('tools.mindfulness.manifestation_quick_desc')}</p>
          </Card>
        </div>
      </section>

      <section className="rounded-3xl border border-line bg-panel p-4 sm:p-5">
        <h2 className="font-heading text-xl font-bold">{t('tools.mindfulness.deep_title')}</h2>
        <p className="text-sm text-muted mt-1">{t('tools.mindfulness.deep_desc')}</p>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card hoverable onClick={() => navigate('/mindfulness/meditation')} data-testid="mindfulness-entry-meditation-deep">
            <div className="text-sm text-muted">{t('tools.mindfulness.deep_badge')}</div>
            <div className="mt-1 text-xl font-heading font-bold">{t('tools.mindfulness.meditation_title')}</div>
            <p className="mt-1 text-sm text-muted">{t('tools.mindfulness.meditation_deep_desc')}</p>
          </Card>

          <Card hoverable onClick={() => navigate('/mindfulness/manifestation?mode=deep')} data-testid="mindfulness-entry-manifestation-deep">
            <div className="text-sm text-muted">{t('tools.mindfulness.deep_badge')}</div>
            <div className="mt-1 text-xl font-heading font-bold">{t('tools.manifestation.title')}</div>
            <p className="mt-1 text-sm text-muted">{t('tools.manifestation.desc')}</p>
          </Card>
        </div>

        <div className="mt-5 rounded-2xl border border-line bg-paper p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">{t('tools.mindfulness.flow_title')}</p>
          <ol className="mt-2 text-sm text-muted space-y-1 list-decimal pl-5">
            <li>{t('tools.mindfulness.flow_step_1')}</li>
            <li>{t('tools.mindfulness.flow_step_2')}</li>
            <li>{t('tools.mindfulness.flow_step_3')}</li>
          </ol>
        </div>
      </section>
    </div>
  );
}
