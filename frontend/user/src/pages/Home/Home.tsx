import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import Card from '../../components/Card/Card';

const MODULES = [
  { path: '/scales', labelKey: 'nav.scales', icon: '📋', descKey: 'landing.feature_scales_desc', color: 'bg-calm-soft' },
  { path: '/tests', labelKey: 'nav.tests', icon: '🧩', descKey: 'landing.feature_tests_desc', color: 'bg-warn-soft' },
  { path: '/coach', labelKey: 'nav.coach', icon: '💬', descKey: 'landing.feature_coach_desc', color: 'bg-safe-soft' },
  { path: '/tools', labelKey: 'nav.tools', icon: '🌿', descKey: 'landing.feature_tools_desc', color: 'bg-accent-soft' },
  { path: '/journal', labelKey: 'nav.journal', icon: '📝', descKey: 'journal.subtitle', color: 'bg-cream' },
  { path: '/billing', labelKey: 'nav.billing', icon: '💎', descKey: 'billing.subtitle', color: 'bg-calm-soft' },
];

const CHANNEL_CONFIG: Record<string, { label: string; color: string; bg: string; icon: string }> = {
  GREEN: { label: '全功能开放', color: 'text-safe', bg: 'bg-safe-soft', icon: '🟢' },
  YELLOW: { label: '部分功能受限 · 建议咨询专业人士', color: 'text-warn', bg: 'bg-warn-soft', icon: '🟡' },
  RED: { label: '请优先联系专业心理健康服务', color: 'text-danger', bg: 'bg-danger-soft', icon: '🔴' },
};

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { channel, email } = useAuthStore();

  const channelInfo = channel ? CHANNEL_CONFIG[channel] : null;

  return (
    <div>
      {/* Welcome */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-heading text-3xl font-bold">
          {t('landing.hero_title')} ✨
        </h1>
        <p className="text-muted mt-1">
          {email ? `${email}` : t('app.tagline')}
        </p>
      </motion.div>

      {/* Triage channel banner */}
      {channelInfo && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`${channelInfo.bg} border border-line rounded-2xl p-5 mb-8 flex items-center gap-3`}
        >
          <span className="text-2xl">{channelInfo.icon}</span>
          <div>
            <p className={`font-semibold ${channelInfo.color}`}>{channelInfo.label}</p>
            {channel === 'YELLOW' && (
              <p className="text-sm text-muted mt-0.5">AI 教练功能暂不可用，其他功能正常使用</p>
            )}
            {channel === 'RED' && (
              <p className="text-sm text-danger mt-0.5">
                请立即联系专业心理健康服务。
                <button
                  onClick={() => navigate('/safety')}
                  className="underline ml-1"
                >
                  查看安全资源
                </button>
              </p>
            )}
          </div>
        </motion.div>
      )}

      {/* Module grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {MODULES.map((mod, i) => {
          const isCoachDisabled = mod.path === '/coach' && (channel === 'YELLOW' || channel === 'RED');

          return (
            <motion.div
              key={mod.path}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card
                hoverable={!isCoachDisabled}
                onClick={() => !isCoachDisabled && navigate(mod.path)}
                className={isCoachDisabled ? 'opacity-50 cursor-not-allowed' : ''}
              >
                <div className={`w-12 h-12 rounded-xl ${mod.color} flex items-center justify-center text-2xl mb-3`}>
                  {mod.icon}
                </div>
                <h3 className="font-heading font-bold text-lg">{t(mod.labelKey)}</h3>
                <p className="text-muted text-sm mt-1">{t(mod.descKey)}</p>
                {isCoachDisabled && (
                  <p className="text-xs text-warn mt-2 font-medium">
                    {t('coach.restricted')}
                  </p>
                )}
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
