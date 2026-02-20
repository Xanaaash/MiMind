import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts';
import Button from '../../components/Button/Button';
import NeurodiversityBanner from '../../components/Neurodiversity/NeurodiversityBanner';
import type { NeuroScoreResult } from '../../data/neuroScales';
import { canShare, downloadShareCard, shareImage } from '../../utils/shareCard';
import { buildNeuroArchetype, generateNeuroShareCard, type NeuroSharePreset } from '../../utils/neuroShareCard';

const LEVEL_COLORS: Record<string, string> = {
  low: '#4a9d6e',
  moderate: '#d4a843',
  high: '#e07a60',
};

export default function NeuroResult() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { scaleId } = useParams<{ scaleId: string }>();
  const result = (location.state as { result?: NeuroScoreResult })?.result;
  const [sharePreset, setSharePreset] = useState<NeuroSharePreset>('xiaohongshu');

  if (!result) {
    return (
      <div className="text-center py-20">
        <p className="text-muted">{t('common.error')}</p>
        <Button variant="ghost" onClick={() => navigate('/neurodiversity')} className="mt-4">
          {t('common.back')}
        </Button>
      </div>
    );
  }

  const levelColor = LEVEL_COLORS[result.level] ?? '#a89890';
  const archetype = buildNeuroArchetype(scaleId ?? '', result.level);

  const radarData = result.dimensions.map((d) => ({
    subject: t(d.nameKey),
    value: d.max > 0 ? (d.score / d.max) * 100 : 0,
    fullMark: 100,
  }));

  const sharePayload = {
    scaleId: scaleId ?? 'neuro',
    levelLabel: t(result.levelKey),
    summary: t(result.summaryKey),
    total: result.total,
    maxTotal: result.maxTotal,
    dimensions: result.dimensions.map((dimension) => ({
      label: t(dimension.nameKey),
      score: dimension.score,
      max: dimension.max,
      color: dimension.color,
    })),
    archetypeTitle: archetype.title,
    archetypeTags: archetype.tags,
  };

  const handleDownload = () => {
    const canvas = generateNeuroShareCard(sharePayload, sharePreset);
    downloadShareCard(canvas, `mimind-neuro-${scaleId ?? 'profile'}-${sharePreset}`);
  };

  const handleNativeShare = async () => {
    if (!canShare()) {
      return;
    }
    const canvas = generateNeuroShareCard(sharePayload, sharePreset);
    try {
      await shareImage(canvas, `neuro-${scaleId ?? 'profile'}`);
    } catch {
      // User cancellation or unsupported file sharing is non-fatal here.
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => navigate('/neurodiversity')}
          className="text-sm text-muted hover:text-ink transition-colors"
        >
          ← {t('neuro.back')}
        </button>
      </div>

      <NeurodiversityBanner />

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6"
      >
        <h1 className="font-heading text-2xl font-bold">{t('neuro.result_title')}</h1>
        <div className="mt-4">
          <span
            className="inline-block text-5xl font-mono font-bold"
            style={{ color: levelColor }}
          >
            {result.total}
          </span>
          <span className="text-muted text-lg ml-1">/ {result.maxTotal}</span>
        </div>
        <div
          className="inline-block mt-2 px-3 py-1 rounded-full text-sm font-semibold text-white"
          style={{ backgroundColor: levelColor }}
        >
          {t(result.levelKey)}
        </div>
      </motion.div>

      {/* Radar Chart */}
      {result.dimensions.length >= 3 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="bg-panel border border-line rounded-2xl p-4 mb-6"
        >
          <h3 className="font-heading font-bold text-sm text-center mb-2">{t('neuro.dimension_chart')}</h3>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="var(--color-line)" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: 'var(--color-muted)' }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                dataKey="value"
                stroke={levelColor}
                fill={levelColor}
                fillOpacity={0.25}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {/* Dimension Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="bg-panel border border-line rounded-2xl p-5 mb-6"
      >
        <h3 className="font-heading font-bold text-sm mb-4">{t('neuro.dimension_detail')}</h3>
        <div className="space-y-3">
          {result.dimensions.map((d) => {
            const pct = d.max > 0 ? (d.score / d.max) * 100 : 0;
            return (
              <div key={d.key}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium">{t(d.nameKey)}</span>
                  <span className="text-muted">{d.score} / {d.max}</span>
                </div>
                <div className="h-2 bg-line rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ backgroundColor: d.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="bg-panel border border-line rounded-2xl p-5 mb-6"
      >
        <h3 className="font-heading font-bold text-sm mb-2">💡 {t('neuro.interpretation')}</h3>
        <p className="text-sm text-muted leading-relaxed">{t(result.summaryKey)}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.45 }}
        className="bg-panel border border-line rounded-2xl p-5 mb-6"
      >
        <h3 className="font-heading font-bold text-sm mb-2">{t('neuro.share_title')}</h3>
        <p className="text-xs text-muted mb-4">{t('neuro.share_subtitle')}</p>

        <div className="grid grid-cols-3 gap-2 mb-4">
          {([
            ['xiaohongshu', t('neuro.share_preset_xiaohongshu')],
            ['instagram', t('neuro.share_preset_instagram')],
            ['tiktok', t('neuro.share_preset_tiktok')],
          ] as Array<[NeuroSharePreset, string]>).map(([preset, label]) => (
            <button
              key={preset}
              type="button"
              onClick={() => setSharePreset(preset)}
              className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-colors ${
                sharePreset === preset
                  ? 'bg-accent text-white border-accent'
                  : 'bg-paper text-muted border-line hover:border-accent/30'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <Button onClick={handleDownload} className="flex-1">
            {t('neuro.share_download')}
          </Button>
          {canShare() ? (
            <Button variant="ghost" onClick={handleNativeShare} className="flex-1">
              {t('neuro.share_native')}
            </Button>
          ) : null}
        </div>
      </motion.div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button onClick={() => navigate('/neurodiversity')} className="flex-1">
          {t('neuro.back_to_hub')}
        </Button>
        <Button
          variant="ghost"
          onClick={() => navigate(`/neurodiversity/${scaleId}`)}
          className="flex-1"
        >
          {t('neuro.retake')}
        </Button>
      </div>
    </div>
  );
}
