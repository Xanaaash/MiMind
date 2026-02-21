import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from 'recharts';
import { useAuthStore } from '../../stores/auth';
import { getEntitlements } from '../../api/billing';
import Button from '../../components/Button/Button';
import { SCALE_INTRO_KEYS, SCALE_NAME_KEYS } from '../../utils/assessmentCopy';

const SEVERITY_COLORS: Record<string, string> = {
  minimal: '#4a9d6e',
  none: '#4a9d6e',
  mild: '#d4a843',
  moderate: '#e78d73',
  'moderately severe': '#c6674f',
  severe: '#c0392b',
};

export default function ScaleResult() {
  const { scaleId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const userId = useAuthStore((state) => state.userId);
  const [reportsEnabled, setReportsEnabled] = useState(false);
  const [entitlementsReady, setEntitlementsReady] = useState(false);

  const result = (location.state as { result?: Record<string, unknown> })?.result;

  useEffect(() => {
    if (!userId) {
      setReportsEnabled(false);
      setEntitlementsReady(true);
      return;
    }

    getEntitlements(userId)
      .then((entitlements) => {
        setReportsEnabled(Boolean(entitlements.assessment_reports_enabled));
      })
      .catch(() => {
        setReportsEnabled(false);
      })
      .finally(() => {
        setEntitlementsReady(true);
      });
  }, [userId]);

  if (!result) {
    return (
      <div className="text-center py-12">
        <p className="text-muted">{t('common.error')}</p>
        <Button variant="ghost" className="mt-4" onClick={() => navigate('/scales')}>
          {t('scales.back_to_list')}
        </Button>
      </div>
    );
  }

  const score = result.score as number ?? result.total_score as number ?? 0;
  const severity = (result.severity as string) ?? 'unknown';
  const interpretation = result.interpretation as Record<string, string> | undefined;
  const lang = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';
  const color = SEVERITY_COLORS[severity.toLowerCase()] ?? '#785c55';
  const isPaywalled = entitlementsReady && !reportsEnabled;
  const localizedScaleName = t(SCALE_NAME_KEYS[scaleId ?? ''] ?? '', { defaultValue: scaleId?.toUpperCase() ?? '' });
  const severityLabel = t(`scales.severity_label.${severity.toLowerCase()}`, { defaultValue: severity });

  const chartData = [{ name: localizedScaleName, value: score }];

  return (
    <motion.div
      className="max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h1 className="font-heading text-3xl font-bold mb-2">{t('scales.result_title')}</h1>
      <p className="text-muted">{localizedScaleName}</p>
      <p className="text-xs text-muted leading-relaxed mb-8">
        {t(SCALE_INTRO_KEYS[scaleId ?? ''] ?? 'scales.intro.generic')}
      </p>

      <div className="bg-panel border border-line rounded-2xl p-8 shadow-sm mb-6 relative overflow-hidden">
        <div className={isPaywalled ? 'blur-[6px] select-none pointer-events-none' : ''}>
          <div className="flex items-center gap-8">
            <div className="text-center">
              <div className="text-5xl font-heading font-bold" style={{ color }}>
                {score}
              </div>
              <p className="text-sm text-muted mt-1">{t('scales.score')}</p>
            </div>
            <div className="flex-1">
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" tick={{ fill: '#785c55', fontSize: 12 }} />
                    <YAxis hide />
                    <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-line">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted">{t('scales.severity')}:</span>
              <span
                className="px-3 py-1 rounded-full text-sm font-semibold text-white"
                style={{ backgroundColor: color }}
              >
                {severityLabel}
              </span>
            </div>
            {interpretation && (
              <p className="text-muted text-sm mt-3">
                {interpretation[lang] || interpretation['zh-CN'] || interpretation['en-US'] || JSON.stringify(interpretation)}
              </p>
            )}
          </div>
        </div>

        {isPaywalled && (
          <div className="absolute inset-0 bg-panel/78 backdrop-blur-[1px] flex items-center justify-center p-6">
            <div className="text-center max-w-sm">
              <p className="font-heading text-xl font-bold">{t('scales.paywall_title')}</p>
              <p className="text-sm text-muted mt-2">{t('scales.paywall_subtitle')}</p>
              <Button className="mt-4" onClick={() => navigate('/billing')}>
                {t('scales.unlock_reports')}
              </Button>
            </div>
          </div>
        )}

        {!entitlementsReady && (
          <div className="absolute inset-0 bg-panel/65 backdrop-blur-[1px] flex items-center justify-center">
            <p className="text-sm text-muted">{t('common.loading')}</p>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <Button variant="ghost" onClick={() => navigate('/scales')}>
          {t('scales.back_to_list')}
        </Button>
        <Button onClick={() => navigate('/home')}>
          {t('nav.home')}
        </Button>
      </div>
    </motion.div>
  );
}
