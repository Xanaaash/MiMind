import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { getPlans, startTrial, getSubscription } from '../../api/billing';
import { useAuthStore } from '../../stores/auth';
import { toast } from '../../stores/toast';
import type { BillingPlan, SubscriptionRecord } from '../../types';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Skeleton from '../../components/Skeleton/Skeleton';

const PLAN_STYLES: Record<string, { icon: string; color: string; popular?: boolean }> = {
  free: { icon: '🆓', color: 'bg-cream' },
  basic: { icon: '⭐', color: 'bg-calm-soft' },
  coach: { icon: '💎', color: 'bg-accent-soft', popular: true },
};

export default function BillingPage() {
  const { t, i18n } = useTranslation();
  const userId = useAuthStore((s) => s.userId);
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [subscription, setSubscription] = useState<SubscriptionRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');

  useEffect(() => {
    Promise.all([
      getPlans().catch(() => []),
      userId ? getSubscription(userId).catch(() => null) : null,
    ]).then(([p, s]) => {
      if (Array.isArray(p)) setPlans(p);
      if (s) setSubscription(s);
      setLoading(false);
    });
  }, [userId]);

  const formatDate = (value: string) => {
    const locale = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';
    return new Date(value).toLocaleDateString(locale);
  };

  const handleTrial = async () => {
    if (!userId) return;
    setActionLoading('trial');
    try {
      const sub = await startTrial(userId);
      setSubscription(sub);
      toast.success(t('billing.trial_activated'));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.error'));
    } finally { setActionLoading(''); }
  };

  if (loading) {
    return (
      <div aria-busy className="space-y-8">
        <div>
          <Skeleton className="h-10 w-52 mb-3" />
          <Skeleton className="h-5 w-72" />
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, idx) => (
            <Card key={idx}>
              <Skeleton className="w-12 h-12 mb-4" />
              <Skeleton className="h-7 w-28 mb-4" />
              <Skeleton className="h-4 w-44 mb-2" />
              <Skeleton className="h-4 w-40 mb-2" />
              <Skeleton className="h-4 w-36 mb-6" />
              <Skeleton className="h-10 w-full" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-heading text-3xl font-bold">{t('billing.title')}</h1>
        <p className="text-muted mt-1 mb-8">{t('billing.subtitle')}</p>
      </motion.div>

      {subscription && (
        <Card className="mb-8 border-accent">
          <div className="flex items-center gap-3">
            <span className="text-2xl">✅</span>
            <div>
              <p className="font-semibold">{t('billing.current_plan')}: {subscription.plan_id}</p>
              <p className="text-sm text-muted">
                {subscription.trial ? t('billing.trial') : subscription.status}
                {subscription.ends_at && ` · ${t('billing.ends_at')}: ${formatDate(subscription.ends_at)}`}
              </p>
            </div>
          </div>
        </Card>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        {plans.length > 0 ? plans.map((plan, i) => {
          const style = PLAN_STYLES[plan.plan_id] ?? PLAN_STYLES.basic;
          return (
            <motion.div
              key={plan.plan_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className={`relative ${style.popular ? 'border-accent border-2' : ''}`}>
                {style.popular && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white text-xs font-bold px-3 py-1 rounded-full">
                    {t('billing.recommended')}
                  </span>
                )}
                <div className={`w-12 h-12 rounded-xl ${style.color} flex items-center justify-center text-2xl mb-4`}>
                  {style.icon}
                </div>
                <h3 className="font-heading font-bold text-xl">{plan.display_name}</h3>
                <div className="mt-4 space-y-2 text-sm text-muted">
                  <p>📊 {plan.reports_enabled ? t('billing.feature_reports_full') : t('billing.feature_reports_basic')}</p>
                  <p>🌿 {plan.tools_enabled ? t('billing.feature_tools_full') : t('billing.feature_tools_basic')}</p>
                  <p>💬 {t('billing.feature_ai_prefix')} {plan.ai_sessions_per_month > 0 ? t('billing.feature_ai_sessions', { count: plan.ai_sessions_per_month }) : t('billing.feature_ai_none')}</p>
                  {plan.trial_days > 0 && <p>🎁 {t('billing.feature_trial_days', { days: plan.trial_days })}</p>}
                </div>
                <Button
                  className="w-full mt-6"
                  variant={style.popular ? 'primary' : 'secondary'}
                  onClick={plan.trial_days > 0 ? handleTrial : undefined}
                  loading={actionLoading === 'trial'}
                >
                  {plan.trial_days > 0 ? t('billing.trial') : t('billing.subscribe')}
                </Button>
              </Card>
            </motion.div>
          );
        }) : (
          /* Fallback display when API returns empty */
          ['free', 'basic', 'coach'].map((planId, i) => {
            const style = PLAN_STYLES[planId];
            const names: Record<string, string> = { free: t('billing.free'), basic: t('billing.basic'), coach: t('billing.premium') };
            return (
              <motion.div
                key={planId}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <Card className={`relative ${style.popular ? 'border-accent border-2' : ''}`}>
                  {style.popular && (
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white text-xs font-bold px-3 py-1 rounded-full">
                      {t('billing.recommended')}
                    </span>
                  )}
                  <div className={`w-12 h-12 rounded-xl ${style.color} flex items-center justify-center text-2xl mb-4`}>
                    {style.icon}
                  </div>
                  <h3 className="font-heading font-bold text-xl">{names[planId]}</h3>
                  <div className="mt-4 space-y-2 text-sm text-muted">
                    <p>📊 {planId !== 'free' ? t('billing.feature_reports_full') : t('billing.feature_reports_basic')}</p>
                    <p>🌿 {planId !== 'free' ? t('billing.feature_tools_full') : t('billing.feature_tools_basic')}</p>
                    <p>💬 {t('billing.feature_ai_prefix')} {planId === 'coach' ? t('billing.feature_ai_unlimited') : t('billing.feature_ai_none')}</p>
                    {planId === 'basic' && <p>🎁 {t('billing.feature_trial_days', { days: 7 })}</p>}
                  </div>
                  <Button
                    className="w-full mt-6"
                    variant={style.popular ? 'primary' : 'secondary'}
                    onClick={planId === 'basic' ? handleTrial : undefined}
                    loading={actionLoading === 'trial' && planId === 'basic'}
                  >
                    {planId === 'free' ? t('billing.free') : planId === 'basic' ? t('billing.trial') : t('billing.subscribe')}
                  </Button>
                </Card>
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
}
