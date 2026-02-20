import { useTranslation } from 'react-i18next';

export default function NeurodiversityBanner() {
  const { t } = useTranslation();

  return (
    <div className="bg-warn-soft border border-warn/30 rounded-xl px-4 py-3 mb-4 flex items-start gap-2.5">
      <span className="text-lg shrink-0 mt-0.5">⚠️</span>
      <div>
        <p className="text-sm font-semibold text-warn">{t('nd_disclaimer.banner_title')}</p>
        <p className="text-xs text-muted mt-0.5 leading-relaxed">{t('nd_disclaimer.banner_body')}</p>
        <p className="text-[11px] font-semibold text-warn mt-1">{t('nd_disclaimer.legal_review_badge')}</p>
      </div>
    </div>
  );
}
