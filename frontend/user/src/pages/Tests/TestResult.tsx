import { useState, useRef } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts';
import Button from '../../components/Button/Button';
import { generateShareCard, downloadShareCard, canShare, shareImage } from '../../utils/shareCard';

export default function TestResult() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
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

  const chartData = summary
    ? Object.entries(summary)
        .filter(([, v]) => typeof v === 'number')
        .map(([key, value]) => ({ dimension: key, value: value as number }))
    : [];

  return (
    <motion.div
      className="max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h1 className="font-heading text-3xl font-bold mb-2">{t('tests.result_title')}</h1>
      <p className="text-muted mb-8">{testId}</p>

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
        {summary && Object.entries(summary).map(([key, value]) => (
          <div key={key} className="flex justify-between py-2 border-b border-line last:border-0">
            <span className="text-muted text-sm">{key}</span>
            <span className="font-semibold text-sm">{String(value)}</span>
          </div>
        ))}
      </div>

      {/* Share card preview */}
      {sharePreview && (
        <div className="bg-panel border border-line rounded-2xl p-6 shadow-sm mb-6 text-center">
          <img src={sharePreview} alt="Share card" className="max-w-xs mx-auto rounded-xl shadow-md" />
          <div className="flex gap-3 justify-center mt-4">
            <Button size="sm" onClick={() => {
              if (canvasRef.current) downloadShareCard(canvasRef.current, `mindcoach-${testId}`);
            }}>
              下载图片
            </Button>
            {canShare() && (
              <Button size="sm" variant="secondary" onClick={() => {
                if (canvasRef.current) shareImage(canvasRef.current, testId ?? 'result');
              }}>
                分享
              </Button>
            )}
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <Button variant="ghost" onClick={() => navigate('/tests')}>
          {t('tests.back_to_list')}
        </Button>
        <Button variant="secondary" onClick={() => {
          if (summary) {
            const canvas = generateShareCard(testId ?? 'Test', summary);
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
