import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { useCoachStore } from '../../stores/coach';
import * as coachApi from '../../api/coach';
import { submitAssessment } from '../../api/auth';
import Button from '../../components/Button/Button';
import CrisisBanner from '../../components/CrisisBanner/CrisisBanner';

const STYLES = [
  { id: 'warm_guide', nameKey: 'coach.style_warm', descKey: 'coach.style_warm_desc', icon: '🤗', color: 'bg-accent-soft' },
  { id: 'rational_analysis', nameKey: 'coach.style_rational', descKey: 'coach.style_rational_desc', icon: '🧠', color: 'bg-calm-soft' },
];

const BASELINE_RESPONSES = {
  phq9: Array(9).fill(0),
  gad7: Array(7).fill(0),
  pss10: Array(10).fill(0),
  cssrs: { q1: false, q2: false, q3: false, q4: false, q5: false, q6: false },
};

export default function CoachPage() {
  const { t } = useTranslation();
  const userId = useAuthStore((s) => s.userId);
  const channel = useAuthStore((s) => s.channel);
  const store = useCoachStore();
  const [input, setInput] = useState('');
  const [crisisMessage, setCrisisMessage] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const isRestricted = channel === 'YELLOW' || channel === 'RED';

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [store.messages]);

  const handleStart = async (styleId: string) => {
    if (!userId) return;
    store.setLoading(true);
    try {
      await submitAssessment(userId, { responses: BASELINE_RESPONSES }).catch(() => {});
      const data = await coachApi.startSession(userId, styleId, true);
      store.setSession(data.session.session_id, styleId);
      if (data.coach_message) {
        store.addMessage('coach', data.coach_message);
      }
    } finally {
      store.setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!store.sessionId || !input.trim()) return;
    const msg = input.trim();
    setInput('');
    store.addMessage('user', msg);
    store.setLoading(true);

    try {
      const data = await coachApi.chat(store.sessionId, msg);
      if (data.coach_message) {
        store.addMessage('coach', data.coach_message);
      }
      if (data.halted) {
        store.setHalted(true);
        setCrisisMessage(data.safety?.action?.message ?? t('coach.safety_pause'));
      }
      if (data.mode === 'crisis' || data.mode === 'safety_pause') {
        setCrisisMessage(data.safety?.action?.message ?? t('coach.safety_pause'));
      }
    } finally {
      store.setLoading(false);
    }
  };

  const handleEnd = async () => {
    if (!store.sessionId) return;
    await coachApi.endSession(store.sessionId);
    store.endSession();
  };

  if (isRestricted) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <span className="text-5xl">🛡️</span>
        <h1 className="font-heading text-2xl font-bold mt-4">{t('coach.title')}</h1>
        <p className="text-muted mt-3 max-w-md mx-auto">{t('coach.restricted')}</p>
      </div>
    );
  }

  // Style selection (no active session)
  if (!store.isActive && !store.sessionId) {
    return (
      <div className="max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h1 className="font-heading text-3xl font-bold">{t('coach.title')}</h1>
          <p className="text-muted mt-1 mb-2">{t('coach.subtitle')}</p>
          <p className="text-xs text-muted mb-8 bg-warn-soft rounded-xl px-4 py-2">
            ⚠️ {t('coach.disclaimer')}
          </p>
        </motion.div>

        <div className="grid gap-4">
          {STYLES.map((style, i) => (
            <motion.div
              key={style.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <button
                onClick={() => handleStart(style.id)}
                disabled={store.isLoading}
                className={`w-full text-left ${style.color} border border-line rounded-2xl p-6 hover:shadow-md transition-all`}
              >
                <div className="flex items-center gap-4">
                  <span className="text-3xl">{style.icon}</span>
                  <div>
                    <h3 className="font-heading font-bold text-lg">{t(style.nameKey)}</h3>
                    <p className="text-muted text-sm mt-1">{t(style.descKey)}</p>
                  </div>
                </div>
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    );
  }

  // Chat interface
  return (
    <div className="max-w-2xl mx-auto flex flex-col h-[calc(100vh-12rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="font-heading font-bold text-lg">{t('coach.title')}</h2>
          <p className="text-xs text-muted">{t('coach.disclaimer')}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={handleEnd}>
          {t('coach.end_session')}
        </Button>
      </div>

      <CrisisBanner visible={!!crisisMessage} message={crisisMessage} />

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pb-4">
        <AnimatePresence>
          {store.messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                  msg.role === 'user'
                    ? 'bg-accent text-white rounded-br-md'
                    : 'bg-cream text-ink rounded-bl-md'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {store.isLoading && (
          <div className="flex justify-start">
            <div className="bg-cream rounded-2xl px-5 py-3 rounded-bl-md">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      {store.isActive && !store.halted && (
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex gap-3 pt-4 border-t border-line"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('coach.placeholder')}
            className="flex-1 border border-line rounded-xl px-4 py-3 bg-white/90 focus:outline-none focus:ring-2 focus:ring-accent/30"
            disabled={store.isLoading}
          />
          <Button type="submit" disabled={!input.trim() || store.isLoading}>
            {t('coach.send')}
          </Button>
        </form>
      )}

      {(store.halted || !store.isActive) && store.sessionId === null && (
        <p className="text-center text-muted py-4">{t('coach.session_ended')}</p>
      )}
    </div>
  );
}
