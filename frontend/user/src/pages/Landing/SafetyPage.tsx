import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import SafetyDisclaimer from '../../components/SafetyDisclaimer/SafetyDisclaimer';

const HOTLINES = [
  { label: '中国心理援助热线', number: '400-161-9995', region: 'CN' },
  { label: '北京心理危机研究与干预中心', number: '800-810-1117', region: 'CN' },
  { label: 'US 988 Suicide & Crisis Lifeline', number: '988', region: 'US' },
  { label: '紧急服务 / Emergency', number: '120 / 911', region: 'ALL' },
];

export default function SafetyPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-6 py-4 flex items-center justify-between max-w-4xl mx-auto w-full">
        <Link to="/" className="font-heading text-xl font-bold text-accent">
          MindCoach AI
        </Link>
      </header>

      <main className="flex-1 max-w-2xl mx-auto px-6 py-12">
        <div className="text-center mb-10">
          <span className="text-5xl">🛡️</span>
          <h1 className="font-heading text-3xl font-bold mt-4">{t('safety.title')}</h1>
          <p className="text-muted mt-2">{t('safety.subtitle')}</p>
        </div>

        <div className="grid gap-4">
          {HOTLINES.map((h) => (
            <div
              key={h.number}
              className="bg-panel border border-line rounded-2xl p-5 flex items-center justify-between"
            >
              <div>
                <p className="font-semibold text-ink">{h.label}</p>
                <p className="text-muted text-sm">{h.region}</p>
              </div>
              <a
                href={`tel:${h.number.replace(/\s/g, '')}`}
                className="inline-flex items-center gap-2 bg-danger text-white font-semibold px-5 py-2.5 rounded-xl hover:bg-danger/90 transition-colors"
              >
                📞 {h.number}
              </a>
            </div>
          ))}
        </div>

        <div className="mt-10 bg-danger-soft border border-danger/20 rounded-2xl p-6 text-center">
          <p className="text-ink font-medium">{t('safety.crisis_message')}</p>
          <p className="text-muted text-sm mt-2">{t('app.boundary')}</p>
        </div>
      </main>

      <SafetyDisclaimer />
    </div>
  );
}
