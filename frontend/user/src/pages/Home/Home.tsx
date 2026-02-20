import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { getReassessmentSchedule } from '../../api/auth';
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

const SCALE_LABELS: Record<string, string> = {
  phq9: 'PHQ-9',
  gad7: 'GAD-7',
  pss10: 'PSS-10',
  cssrs: 'C-SSRS',
  scl90: 'SCL-90',
};

type ReminderState = {
  kind: 'overdue' | 'upcoming';
  scaleIds: string[];
  minDays: number;
} | null;

const REMINDER_WINDOW_DAYS = 3;

function daysUntil(dateText: string): number {
  const target = new Date(`${dateText}T00:00:00`);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.floor((target.getTime() - today.getTime()) / 86_400_000);
}

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { userId, channel, email } = useAuthStore();
  const [reminder, setReminder] = useState<ReminderState>(null);

  const channelInfo = channel ? CHANNEL_CONFIG[channel] : null;
  const reminderScaleText = useMemo(() => {
    if (!reminder) return '';
    return reminder.scaleIds.map((scaleId) => SCALE_LABELS[scaleId] ?? scaleId.toUpperCase()).join(', ');
  }, [reminder]);

  useEffect(() => {
    if (!userId) {
      setReminder(null);
      return;
    }

    getReassessmentSchedule(userId)
      .then((payload) => {
        const entries = Object.entries(payload.due_dates).map(([scaleId, dueDate]) => ({
          scaleId,
          diffDays: daysUntil(dueDate),
        }));

        const overdue = entries
          .filter((entry) => entry.diffDays <= 0)
          .sort((a, b) => a.diffDays - b.diffDays);
        if (overdue.length > 0) {
          setReminder({
            kind: 'overdue',
            scaleIds: overdue.slice(0, 2).map((entry) => entry.scaleId),
            minDays: overdue[0].diffDays,
          });
          return;
        }

        const upcoming = entries
          .filter((entry) => entry.diffDays > 0 && entry.diffDays <= REMINDER_WINDOW_DAYS)
          .sort((a, b) => a.diffDays - b.diffDays);
        if (upcoming.length > 0) {
          setReminder({
            kind: 'upcoming',
            scaleIds: upcoming.slice(0, 2).map((entry) => entry.scaleId),
            minDays: upcoming[0].diffDays,
          });
          return;
        }

        setReminder(null);
      })
      .catch(() => {
        setReminder(null);
      });
  }, [userId]);

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

      {reminder && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`border border-line rounded-2xl p-5 mb-8 flex items-start gap-3 ${
            reminder.kind === 'overdue' ? 'bg-danger-soft' : 'bg-warn-soft'
          }`}
        >
          <span className="text-2xl">{reminder.kind === 'overdue' ? '⏰' : '📅'}</span>
          <div className="flex-1">
            <p className="font-semibold">
              {reminder.kind === 'overdue' ? t('home.reassessment_overdue_title') : t('home.reassessment_upcoming_title')}
            </p>
            <p className="text-sm text-muted mt-1">
              {reminder.kind === 'overdue'
                ? t('home.reassessment_overdue_body', {
                    scales: reminderScaleText,
                    days: Math.abs(reminder.minDays),
                  })
                : t('home.reassessment_upcoming_body', {
                    scales: reminderScaleText,
                    days: reminder.minDays,
                  })}
            </p>
          </div>
          <button
            onClick={() => navigate('/scales')}
            className="text-sm font-semibold text-accent hover:underline shrink-0"
          >
            {t('home.reassessment_cta')}
          </button>
        </motion.div>
      )}

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
