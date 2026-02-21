import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

type Section = {
  heading: string;
  body: string;
};

export default function TermsPage() {
  const { t } = useTranslation();
  const sections = t('legal.terms.sections', { returnObjects: true }) as Section[];

  return (
    <div className="min-h-screen px-4 py-12">
      <motion.div
        className="max-w-3xl mx-auto bg-panel border border-line rounded-3xl p-8 shadow-sm"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mb-6">
          <h1 className="font-heading text-3xl font-bold">{t('legal.terms.title')}</h1>
          <p className="text-muted mt-1">{t('legal.terms.subtitle')}</p>
          <p className="text-xs text-muted mt-2">{t('legal.terms.updated_at')}</p>
        </div>

        <div className="space-y-5">
          {sections.map((section) => (
            <section key={section.heading}>
              <h2 className="font-heading font-bold text-lg">{section.heading}</h2>
              <p className="text-muted text-sm mt-1 leading-relaxed">{section.body}</p>
            </section>
          ))}
        </div>

        <div className="mt-8">
          <Link to="/" className="text-sm font-semibold text-accent hover:underline">
            {t('legal.back_home')}
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
