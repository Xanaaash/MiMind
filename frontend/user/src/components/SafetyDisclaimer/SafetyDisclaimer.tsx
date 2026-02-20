import { useTranslation } from 'react-i18next';

interface SafetyDisclaimerProps {
  compact?: boolean;
}

export default function SafetyDisclaimer({ compact }: SafetyDisclaimerProps) {
  const { t } = useTranslation();

  if (compact) {
    return (
      <p className="text-xs text-muted text-center py-2 px-4">
        {t('app.boundary')}
      </p>
    );
  }

  return (
    <footer className="border-t border-line bg-panel/60 py-4 px-6 text-center">
      <p className="text-sm text-muted max-w-2xl mx-auto">
        {t('app.boundary')}
      </p>
      <p className="text-xs text-muted/70 mt-1">
        {t('app.crisis_note')}
      </p>
    </footer>
  );
}
