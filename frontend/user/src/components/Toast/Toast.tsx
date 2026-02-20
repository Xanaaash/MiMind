import { AnimatePresence, motion } from 'framer-motion';
import { useToastStore, type ToastItem } from '../../stores/toast';

const icons: Record<ToastItem['type'], string> = {
  success: '✓',
  error: '✕',
  warning: '!',
};

const styles: Record<ToastItem['type'], string> = {
  success: 'bg-safe-soft border-safe text-safe',
  error: 'bg-danger-soft border-danger text-danger',
  warning: 'bg-warn-soft border-warn text-ink',
};

const iconBg: Record<ToastItem['type'], string> = {
  success: 'bg-safe text-white',
  error: 'bg-danger text-white',
  warning: 'bg-warn text-white',
};

export default function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts);
  const dismiss = useToastStore((s) => s.dismiss);

  return (
    <div className="fixed top-5 right-5 z-[9999] flex flex-col gap-3 pointer-events-none max-w-sm w-full">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, x: 80, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 80, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className={`
              pointer-events-auto flex items-start gap-3 px-4 py-3
              rounded-xl border shadow-md backdrop-blur-sm
              ${styles[t.type]}
            `}
          >
            <span
              className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${iconBg[t.type]}`}
            >
              {icons[t.type]}
            </span>

            <p className="flex-1 text-sm font-medium leading-snug pt-0.5">{t.message}</p>

            <button
              onClick={() => dismiss(t.id)}
              className="flex-shrink-0 opacity-50 hover:opacity-100 transition-opacity text-current"
              aria-label="Close"
            >
              ✕
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
