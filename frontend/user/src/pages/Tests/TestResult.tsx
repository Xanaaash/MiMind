import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts';
import Button from '../../components/Button/Button';
import { generateShareCard, downloadShareCard, canShare, shareImage } from '../../utils/shareCard';
import { getPairingReport } from '../../api/tests';
import type { PairingReport } from '../../types';
import { TEST_INTRO_KEYS, TEST_NAME_KEYS } from '../../utils/assessmentCopy';

function formatSummaryValue(value: unknown, t: (key: string, options?: Record<string, unknown>) => string): string {
  if (typeof value === 'string') {
    return t(`tests.value_label.${value}`, { defaultValue: value });
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((entry) => formatSummaryValue(entry, t)).join(', ');
  }
  if (value && typeof value === 'object') {
    return JSON.stringify(value);
  }
  return '';
}

export default function TestResult() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();

  const result = (location.state as { result?: Record<string, unknown> })?.result;

  if (!result) {
    return (
      <div className="text-center py-12">
        <p className="text-muted">{t('common.error')}</p>
        <Button variant="ghost" className="mt-4" onClick={() => navigate('/tests')}>
          {t('tests.back_to_list')}
        </Button>
      </div>
    );
  }

  const [sharePreview, setSharePreview] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const summary = result.summary as Record<string, unknown> | undefined;
  const resultId = (result.result_id as string | undefined) ?? '';
  const pairTargetResultId = searchParams.get('pair') ?? '';
  const [copyState, setCopyState] = useState<'idle' | 'copied'>('idle');
  const [pairingReport, setPairingReport] = useState<PairingReport | null>(null);
  const [pairingLoading, setPairingLoading] = useState(false);
  const [pairingError, setPairingError] = useState<string | null>(null);
  const localizedTestName = t(TEST_NAME_KEYS[testId ?? ''] ?? '', { defaultValue: testId ?? '' });
  const shareCardCopy = useMemo(() => ({
    genericSubtitle: t('tests.share_card.generic_subtitle'),
    footerLine1: t('tests.share_card.footer_line1'),
    footerLine2: t('tests.share_card.footer_line2'),
    mbtiSubtitle: t('tests.share_card.mbti_subtitle'),
    mbtiTypeLabel: t('tests.share_card.mbti_type_label'),
    big5Subtitle: t('tests.share_card.big5_subtitle'),
    big5DominantLabel: t('tests.share_card.big5_dominant_label'),
    big5Traits: {
      O: t('tests.share_card.trait_o'),
      C: t('tests.share_card.trait_c'),
      E: t('tests.share_card.trait_e'),
      A: t('tests.share_card.trait_a'),
      N: t('tests.share_card.trait_n'),
    },
  }), [t]);

  const inviteLink = useMemo(() => {
    if (!resultId || !testId) return '';
    const url = new URL(`/tests/${testId}`, window.location.origin);
    url.searchParams.set('pair', resultId);
    return url.toString();
  }, [resultId, testId]);

  useEffect(() => {
    if (!pairTargetResultId || !resultId || pairTargetResultId === resultId) return;

    setPairingLoading(true);
    getPairingReport(pairTargetResultId, resultId)
      .then((data) => {
        setPairingReport(data);
        setPairingError(null);
      })
      .catch((error: unknown) => {
        setPairingReport(null);
        setPairingError(error instanceof Error ? error.message : String(error));
      })
      .finally(() => {
        setPairingLoading(false);
      });
  }, [pairTargetResultId, resultId]);

  const chartData = summary
    ? Object.entries(summary)
        .filter(([, v]) => typeof v === 'number')
        .map(([key, value]) => ({
          dimension: t(`tests.summary_label.${key}`, { defaultValue: key }),
          value: value as number,
        }))
    : [];
  const summaryRows = useMemo(() => {
    if (!summary) return [] as Array<{ label: string; value: string }>;

    const rows: Array<{ label: string; value: string }> = [];
    Object.entries(summary).forEach(([key, value]) => {
      const label = t(`tests.summary_label.${key}`, { defaultValue: key });
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.entries(value as Record<string, unknown>).forEach(([subKey, subValue]) => {
          const subLabel = t(`tests.summary_label.${subKey}`, { defaultValue: subKey });
          rows.push({
            label: `${label} · ${subLabel}`,
            value: formatSummaryValue(subValue, t),
          });
        });
        return;
      }
      rows.push({ label, value: formatSummaryValue(value, t) });
    });
    return rows;
  }, [summary, t]);

  return (
    <motion.div
      className="max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h1 className="font-heading text-3xl font-bold mb-2">{t('tests.result_title')}</h1>
      <p className="text-muted">{localizedTestName}</p>
      <p className="text-xs text-muted leading-relaxed mb-8">
        {t(TEST_INTRO_KEYS[testId ?? ''] ?? 'tests.intro.generic')}
      </p>

      {chartData.length > 2 && (
        <div className="bg-panel border border-line rounded-2xl p-8 shadow-sm mb-6">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={chartData}>
                <PolarGrid stroke="rgba(103,71,63,0.15)" />
                <PolarAngleAxis dataKey="dimension" tick={{ fill: '#785c55', fontSize: 12 }} />
                <Radar
                  dataKey="value"
                  stroke="#c6674f"
                  fill="#c6674f"
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Summary details */}
      <div className="bg-panel border border-line rounded-2xl p-6 shadow-sm mb-6">
        <h3 className="font-heading font-bold mb-4">{t('tests.result_title')}</h3>
        {summaryRows.map((row, idx) => (
          <div key={`${row.label}-${idx}`} className="flex justify-between py-2 border-b border-line last:border-0 gap-4">
            <span className="text-muted text-sm">{row.label}</span>
            <span className="font-semibold text-sm text-right">{row.value}</span>
          </div>
        ))}
      </div>

      {/* Share card preview */}
      {sharePreview && (
        <div className="bg-panel border border-line rounded-2xl p-6 shadow-sm mb-6 text-center">
          <img src={sharePreview} alt="Share card" className="max-w-xs mx-auto rounded-xl shadow-md" />
          <div className="flex gap-3 justify-center mt-4">
            <Button size="sm" onClick={() => {
              if (canvasRef.current) downloadShareCard(canvasRef.current, `mimind-${testId}`);
            }}>
              {t('common.download_image')}
            </Button>
            {canShare() && (
              <Button size="sm" variant="secondary" onClick={() => {
                if (canvasRef.current) {
                  shareImage(canvasRef.current, localizedTestName || testId || 'result');
                }
              }}>
                {t('common.share')}
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Pair invite */}
      {inviteLink && (
        <div className="bg-panel border border-line rounded-2xl p-6 shadow-sm mb-6">
          <h3 className="font-heading font-bold mb-2">{t('tests.pair_invite_title')}</h3>
          <p className="text-sm text-muted mb-4">{t('tests.pair_invite_subtitle')}</p>
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              value={inviteLink}
              readOnly
              className="flex-1 border border-line rounded-xl px-3 py-2 bg-white/90 text-sm text-muted"
            />
            <Button
              size="sm"
              onClick={async () => {
                await navigator.clipboard.writeText(inviteLink).catch(() => {});
                setCopyState('copied');
                setTimeout(() => setCopyState('idle'), 2000);
              }}
            >
              {copyState === 'copied' ? t('tests.pair_copied') : t('tests.pair_copy')}
            </Button>
          </div>
        </div>
      )}

      {(pairTargetResultId || pairingReport || pairingLoading || pairingError) && (
        <div className="bg-panel border border-line rounded-2xl p-6 shadow-sm mb-6">
          <h3 className="font-heading font-bold mb-2">{t('tests.pair_result_title')}</h3>
          {pairingLoading && <p className="text-sm text-muted">{t('common.loading')}</p>}
          {!pairingLoading && pairingError && (
            <p className="text-sm text-danger">{pairingError}</p>
          )}
          {!pairingLoading && pairingReport && (
            <div>
              <p className="text-sm text-muted">
                {t('tests.pair_score')}: <span className="font-semibold text-ink">{pairingReport.compatibility_score}</span>
              </p>
              <p className="text-sm text-muted mt-1">
                {t('tests.pair_level')}:
                {' '}
                <span className="font-semibold text-ink">
                  {t(`tests.value_label.${pairingReport.compatibility_level}`, { defaultValue: pairingReport.compatibility_level })}
                </span>
              </p>
              <p className="text-sm text-muted mt-3">{pairingReport.notes}</p>
            </div>
          )}
          {!pairingLoading && !pairingReport && !pairingError && pairTargetResultId && (
            <p className="text-sm text-muted">{t('tests.pair_pending')}</p>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <Button variant="ghost" onClick={() => navigate('/tests')}>
          {t('tests.back_to_list')}
        </Button>
        <Button variant="secondary" onClick={() => {
          if (summary) {
            const canvas = generateShareCard(localizedTestName || testId || 'Test', summary, shareCardCopy);
            canvasRef.current = canvas;
            setSharePreview(canvas.toDataURL('image/png'));
          }
        }}>
          {t('tests.share')}
        </Button>
        <Button onClick={() => navigate('/home')}>
          {t('nav.home')}
        </Button>
      </div>
    </motion.div>
  );
}
