import { Suspense } from 'react';
import { useLocation, useRoutes } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { routes } from './router';
import Loading from './components/Loading/Loading';
import ToastContainer from './components/Toast/Toast';
import GlobalErrorBoundary from './components/ErrorBoundary/GlobalErrorBoundary';

export default function App() {
  const location = useLocation();
  const element = useRoutes(routes, location);

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
