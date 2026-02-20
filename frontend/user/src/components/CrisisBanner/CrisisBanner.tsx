import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import Button from '../Button/Button';

interface CrisisBannerProps {
  visible: boolean;
  message?: string;
}

const HOTLINES = [
  { label: '中国心理援助热线', number: '400-161-9995' },
  { label: 'US 988 Lifeline', number: '988' },
];

export default function CrisisBanner({ visible, message }: CrisisBannerProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  if (!visible) return null;

  return (
    <div className="bg-danger-soft border-2 border-danger rounded-2xl p-6 my-4" role="alert">
      <div className="flex items-start gap-3">
        <span className="text-2xl">🚨</span>
        <div className="flex-1">
          <h3 className="font-heading font-bold text-danger text-lg">
            {t('safety.title')}
          </h3>
          {message && <p className="text-ink mt-1">{message}</p>}
          <p className="text-muted mt-2">{t('safety.crisis_message')}</p>
          <div className="flex flex-wrap gap-3 mt-4">
            {HOTLINES.map((h) => (
              <a
                key={h.number}
                href={`tel:${h.number}`}
                className="inline-flex items-center gap-2 bg-danger text-white font-semibold px-4 py-2 rounded-xl hover:bg-danger/90 transition-colors"
              >
                📞 {h.label}: {h.number}
              </a>
            ))}
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="mt-3"
            onClick={() => navigate('/safety')}
          >
            {t('safety.subtitle')}
          </Button>
        </div>
      </div>
    </div>
  );
}
