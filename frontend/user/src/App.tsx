import { Suspense, useEffect } from 'react';
import { useLocation, useRoutes } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AnimatePresence, motion } from 'framer-motion';
import { routes } from './router';
import Loading from './components/Loading/Loading';
import ToastContainer from './components/Toast/Toast';
import GlobalErrorBoundary from './components/ErrorBoundary/GlobalErrorBoundary';

const LANG_MAP: Record<string, string> = {
  'zh-CN': 'zh-Hans',
  'en-US': 'en',
};

export default function App() {
  const location = useLocation();
  const element = useRoutes(routes, location);
  const { t, i18n } = useTranslation();

  useEffect(() => {
    const lang = i18n.language;
    document.documentElement.lang = LANG_MAP[lang] ?? lang;
    document.title = `${t('app.name')} — ${t('app.tagline')}`;
  }, [i18n.language, t]);

  return (
    <>
      <GlobalErrorBoundary>
        <Suspense fallback={<Loading fullScreen />}>
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
            >
              {element}
            </motion.div>
          </AnimatePresence>
        </Suspense>
      </GlobalErrorBoundary>
      <ToastContainer />
    </>
  );
}
