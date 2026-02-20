import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { useCoachStore } from '../../stores/coach';
import * as coachApi from '../../api/coach';
import Button from '../../components/Button/Button';
import CrisisBanner from '../../components/CrisisBanner/CrisisBanner';
import AssessmentGate, { isAssessmentExpired } from '../../components/AssessmentGate/AssessmentGate';

const STYLES = [
  { id: 'warm_guide', nameKey: 'coach.style_warm', descKey: 'coach.style_warm_desc', icon: '🤗', color: 'bg-accent-soft' },
  { id: 'rational_analysis', nameKey: 'coach.style_rational', descKey: 'coach.style_rational_desc', icon: '🧠', color: 'bg-calm-soft' },
];

function useVisualViewportHeight() {
  const [height, setHeight] = useState<number | null>(null);

  useEffect(() => {
    const vv = window.visualViewport;
    if (!vv) return;

    const update = () => setHeight(vv.height);
    update();
    vv.addEventListener('resize', update);
    return () => vv.removeEventListener('resize', update);
  }, []);

  return height;
}

export default function CoachPage() {
  const { t } = useTranslation();
  const userId = useAuthStore((s) => s.userId);
  const channel = useAuthStore((s) => s.channel);
  const store = useCoachStore();
  const [input, setInput] = useState('');
  const [crisisMessage, setCrisisMessage] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const typingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const vpHeight = useVisualViewportHeight();

  const needsAssessment = !channel;
  const assessmentExpired = channel && isAssessmentExpired();
  const isRestricted = channel === 'YELLOW' || channel === 'RED';

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [store.messages, scrollToBottom]);

  useEffect(() => {
    if (vpHeight && containerRef.current) {
      scrollToBottom();
    }
  }, [vpHeight, scrollToBottom]);

  useEffect(() => {
    return () => {
      if (typingTimerRef.current) {
        clearInterval(typingTimerRef.current);
      }
    };
  }, []);

  const typeCoachMessage = (text: string) => {
    if (typingTimerRef.current) {
      clearInterval(typingTimerRef.current);
    }

    const targetIndex = store.addMessage('coach', '');
    const chunkSize = text.length > 180 ? 4 : text.length > 90 ? 2 : 1;
    let cursor = 0;

    typingTimerRef.current = setInterval(() => {
      cursor = Math.min(text.length, cursor + chunkSize);
      store.updateMessage(targetIndex, text.slice(0, cursor));
      if (cursor >= text.length && typingTimerRef.current) {
        clearInterval(typingTimerRef.current);
        typingTimerRef.current = null;
      }
    }, 18);
  };

  if (needsAssessment) {
    return <AssessmentGate reason="missing" />;
  }

  if (assessmentExpired) {
    return <AssessmentGate reason="expired" />;
  }

  const handleStart = async (styleId: string) => {
    if (!userId) return;
    store.setLoading(true);
    try {
      const data = await coachApi.startSession(userId, styleId, true);
      store.setSession(data.session.session_id, styleId);
      if (data.coach_message) {
        typeCoachMessage(data.coach_message);
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

    inputRef.current?.focus();

    try {
      const data = await coachApi.chat(store.sessionId, msg);
      if (data.coach_message) {
        typeCoachMessage(data.coach_message);
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
    if (typingTimerRef.current) {
      clearInterval(typingTimerRef.current);
      typingTimerRef.current = null;
    }
    await coachApi.endSession(store.sessionId);
    store.endSession();
  };

  if (isRestricted) {
    return (
      <div className="max-w-2xl mx-auto text-center py-10 sm:py-16 px-4">
        <span className="text-4xl sm:text-5xl">🛡️</span>
        <h1 className="font-heading text-xl sm:text-2xl font-bold mt-4">{t('coach.title')}</h1>
        <p className="text-muted mt-3 max-w-md mx-auto text-sm sm:text-base">{t('coach.restricted')}</p>
      </div>
    );
  }

  if (!store.isActive && !store.sessionId) {
    return (
      <div className="max-w-2xl mx-auto px-1 sm:px-0">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h1 className="font-heading text-2xl sm:text-3xl font-bold">{t('coach.title')}</h1>
          <p className="text-muted mt-1 mb-2 text-sm sm:text-base">{t('coach.subtitle')}</p>
          <p className="text-xs text-muted mb-6 sm:mb-8 bg-warn-soft rounded-xl px-3 sm:px-4 py-2">
            ⚠️ {t('coach.disclaimer')}
          </p>
        </motion.div>

        <div className="grid gap-3 sm:gap-4">
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
                className={`w-full text-left ${style.color} border border-line rounded-2xl p-4 sm:p-6 hover:shadow-md transition-all active:scale-[0.98]`}
              >
                <div className="flex items-center gap-3 sm:gap-4">
                  <span className="text-2xl sm:text-3xl">{style.icon}</span>
                  <div className="min-w-0">
                    <h3 className="font-heading font-bold text-base sm:text-lg">{t(style.nameKey)}</h3>
                    <p className="text-muted text-xs sm:text-sm mt-0.5 sm:mt-1">{t(style.descKey)}</p>
                  </div>
                </div>
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    );
  }

  const chatHeight = vpHeight
    ? `${vpHeight - 80}px`
    : 'calc(100dvh - 10rem)';

  return (
    <div
      ref={containerRef}
      className="max-w-2xl mx-auto flex flex-col"
      style={{ height: chatHeight }}
    >
      {/* Header — compact on mobile */}
      <div className="flex items-center justify-between mb-2 sm:mb-4 shrink-0">
        <div className="min-w-0 flex-1">
          <h2 className="font-heading font-bold text-base sm:text-lg truncate">{t('coach.title')}</h2>
          <p className="text-[10px] sm:text-xs text-muted truncate">{t('coach.disclaimer')}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={handleEnd} className="shrink-0 ml-2">
          {t('coach.end_session')}
        </Button>
      </div>

      <CrisisBanner visible={!!crisisMessage} message={crisisMessage} />

      {/* Messages — scrollable area takes remaining space */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 sm:space-y-4 pb-2 overscroll-contain">
        <AnimatePresence>
          {store.messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 sm:px-5 py-2.5 sm:py-3 ${
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
            <div className="bg-cream rounded-2xl px-4 sm:px-5 py-2.5 sm:py-3 rounded-bl-md">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input — sticky at bottom, adapts to keyboard via visualViewport */}
      {store.isActive && !store.halted && (
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex gap-2 sm:gap-3 pt-2 sm:pt-4 border-t border-line shrink-0 pb-[env(safe-area-inset-bottom,0px)]"
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('coach.placeholder')}
            className="flex-1 min-w-0 border border-line rounded-xl px-3 sm:px-4 py-2.5 sm:py-3 bg-white/90 focus:outline-none focus:ring-2 focus:ring-accent/30 text-base"
            disabled={store.isLoading}
            enterKeyHint="send"
            autoComplete="off"
          />
          <Button type="submit" disabled={!input.trim() || store.isLoading} className="shrink-0">
            {t('coach.send')}
          </Button>
        </form>
      )}

      {(store.halted || !store.isActive) && store.sessionId === null && (
        <p className="text-center text-muted py-3 sm:py-4 text-sm">{t('coach.session_ended')}</p>
      )}
    </div>
  );
}
