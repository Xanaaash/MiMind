import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../../components/Button/Button';
import SafetyDisclaimer from '../../components/SafetyDisclaimer/SafetyDisclaimer';

const FEATURES = [
  { key: 'scales', icon: '📋', color: 'bg-calm-soft' },
  { key: 'tests', icon: '🧩', color: 'bg-warn-soft' },
  { key: 'coach', icon: '💬', color: 'bg-safe-soft' },
  { key: 'tools', icon: '🌿', color: 'bg-accent-soft' },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5 },
  }),
};

export default function Landing() {
  const { t, i18n } = useTranslation();

  const toggleLang = () => {
    const next = i18n.language === 'zh-CN' ? 'en-US' : 'zh-CN';
    i18n.changeLanguage(next);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between max-w-6xl mx-auto w-full">
        <div className="flex items-center gap-2">
          <span className="font-heading text-2xl font-bold text-accent">MindCoach</span>
          <span className="text-xs bg-accent-soft text-accent px-2 py-0.5 rounded-full font-semibold">AI</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleLang}
            className="text-sm text-muted hover:text-ink px-3 py-1.5 rounded-lg hover:bg-cream/50 transition-colors"
          >
            {i18n.language === 'zh-CN' ? 'EN' : '中文'}
          </button>
          <Link to="/auth">
            <Button size="sm">{t('auth.login')}</Button>
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="flex-1 flex items-center justify-center px-6 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h1
            className="font-heading text-4xl md:text-6xl font-bold text-ink leading-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {t('landing.hero_title')}
          </motion.h1>
          <motion.p
            className="mt-6 text-lg md:text-xl text-muted max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15, duration: 0.6 }}
          >
            {t('landing.hero_subtitle')}
          </motion.p>
          <motion.div
            className="mt-10 flex flex-wrap justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <Link to="/auth">
              <Button size="lg">{t('landing.cta_start')}</Button>
            </Link>
            <a href="#features">
              <Button variant="ghost" size="lg">{t('landing.cta_learn')}</Button>
            </a>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="px-6 py-20 max-w-6xl mx-auto w-full">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.key}
              custom={i}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeUp}
              className="bg-panel border border-line rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center text-2xl mb-4`}>
                {f.icon}
              </div>
              <h3 className="font-heading font-bold text-lg">
                {t(`landing.feature_${f.key}`)}
              </h3>
              <p className="text-muted text-sm mt-2">
                {t(`landing.feature_${f.key}_desc`)}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Safety promise */}
      <section className="px-6 py-12 text-center">
        <div className="max-w-2xl mx-auto bg-safe-soft/50 border border-safe/20 rounded-2xl p-8">
          <span className="text-3xl">🛡️</span>
          <h3 className="font-heading font-bold text-lg mt-3">{t('safety.title')}</h3>
          <p className="text-muted text-sm mt-2">{t('app.boundary')}</p>
          <p className="text-muted text-xs mt-1">{t('app.crisis_note')}</p>
        </div>
      </section>

      <SafetyDisclaimer />
    </div>
  );
}
