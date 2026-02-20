import { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Button from '../../components/Button/Button';

type Phase = 'idle' | 'work' | 'break';

const PRESETS = [
  { work: 25, break: 5, label: '25 / 5' },
  { work: 15, break: 3, label: '15 / 3' },
  { work: 50, break: 10, label: '50 / 10' },
];

const CIRCLE_R = 90;
const CIRCLE_C = 2 * Math.PI * CIRCLE_R;

function loadTodayCount(): number {
  const stored = localStorage.getItem('pomo_today');
  if (!stored) return 0;
  try {
    const { date, count } = JSON.parse(stored);
    if (date === new Date().toDateString()) return count;
  } catch { /* ignore */ }
  return 0;
}

function saveTodayCount(count: number) {
  localStorage.setItem('pomo_today', JSON.stringify({ date: new Date().toDateString(), count }));
}

export default function PomodoroTimer() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [workMin, setWorkMin] = useState(25);
  const [breakMin, setBreakMin] = useState(5);
  const [phase, setPhase] = useState<Phase>('idle');
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [todayCount, setTodayCount] = useState(loadTodayCount);
  const [showReward, setShowReward] = useState(false);
  const [tasks, setTasks] = useState<string[]>([]);
  const [taskInput, setTaskInput] = useState('');
  const [completedTasks, setCompletedTasks] = useState<Set<number>>(new Set());
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => { if (tickRef.current) clearInterval(tickRef.current); };
  }, []);

  useEffect(() => {
    if (phase === 'idle') {
      if (tickRef.current) clearInterval(tickRef.current);
      return;
    }

    tickRef.current = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          if (phase === 'work') {
            const next = todayCount + 1;
            setTodayCount(next);
            saveTodayCount(next);
            setShowReward(true);
            setTimeout(() => setShowReward(false), 3000);
            const breakSec = breakMin * 60;
            setTotalSeconds(breakSec);
            setPhase('break');
            return breakSec;
          } else {
            setPhase('idle');
            return 0;
          }
        }
        return prev - 1;
      });
    }, 1000);

    return () => { if (tickRef.current) clearInterval(tickRef.current); };
  }, [phase, breakMin, todayCount]);

  const startWork = useCallback(() => {
    const sec = workMin * 60;
    setTotalSeconds(sec);
    setSecondsLeft(sec);
    setPhase('work');
  }, [workMin]);

  const stop = useCallback(() => {
    setPhase('idle');
    setSecondsLeft(0);
  }, []);

  const addTask = () => {
    const trimmed = taskInput.trim();
    if (!trimmed) return;
    setTasks((prev) => [...prev, trimmed]);
    setTaskInput('');
  };

  const toggleTask = (idx: number) => {
    setCompletedTasks((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const removeTask = (idx: number) => {
    setTasks((prev) => prev.filter((_, i) => i !== idx));
    setCompletedTasks((prev) => {
      const next = new Set<number>();
      prev.forEach((v) => {
        if (v < idx) next.add(v);
        else if (v > idx) next.add(v - 1);
      });
      return next;
    });
  };

  const progress = totalSeconds > 0 ? 1 - secondsLeft / totalSeconds : 0;
  const dashOffset = CIRCLE_C * (1 - progress);
  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;

  const phaseColor = phase === 'work' ? '#e07a60' : phase === 'break' ? '#5cb87e' : '#a89890';

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate('/tools')}
          className="text-sm text-muted hover:text-ink transition-colors"
        >
          ← {t('pomo.back')}
        </button>
        <div className="flex items-center gap-2 bg-cream/60 rounded-xl px-3 py-1.5">
          <span className="text-lg">🍅</span>
          <span className="text-sm font-bold">{todayCount}</span>
          <span className="text-xs text-muted">{t('pomo.today')}</span>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6"
      >
        <h1 className="font-heading text-2xl font-bold">{t('pomo.title')}</h1>
        <p className="text-muted text-sm mt-1">{t('pomo.subtitle')}</p>
      </motion.div>

      {/* Timer Circle */}
      <div className="flex justify-center mb-6">
        <div className="relative w-52 h-52 sm:w-60 sm:h-60">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 200 200">
            <circle
              cx="100" cy="100" r={CIRCLE_R}
              fill="none"
              stroke="currentColor"
              strokeWidth="6"
              className="text-line"
            />
            <motion.circle
              cx="100" cy="100" r={CIRCLE_R}
              fill="none"
              stroke={phaseColor}
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={CIRCLE_C}
              animate={{ strokeDashoffset: dashOffset }}
              transition={{ duration: 0.5, ease: 'linear' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-mono text-4xl sm:text-5xl font-bold" style={{ color: phaseColor }}>
              {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
            </span>
            <span className="text-xs text-muted mt-1 uppercase tracking-wider">
              {phase === 'idle' ? t('pomo.ready') : t(`pomo.phase_${phase}`)}
            </span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-3 mb-6">
        {phase === 'idle' ? (
          <Button onClick={startWork} className="px-8">
            {t('pomo.start')}
          </Button>
        ) : (
          <Button variant="ghost" onClick={stop}>
            {t('pomo.stop')}
          </Button>
        )}
      </div>

      {/* Presets */}
      {phase === 'idle' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center gap-2 mb-8"
        >
          {PRESETS.map((p) => (
            <button
              key={p.label}
              onClick={() => { setWorkMin(p.work); setBreakMin(p.break); }}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                ${workMin === p.work && breakMin === p.break
                  ? 'bg-accent text-white'
                  : 'bg-cream text-muted hover:bg-accent-soft'
                }
              `}
            >
              {p.label}
            </button>
          ))}
        </motion.div>
      )}

      {/* Task Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-panel border border-line rounded-2xl p-4 sm:p-5"
      >
        <h3 className="font-heading font-bold text-sm mb-3">
          {t('pomo.tasks_title')}
        </h3>
        <p className="text-xs text-muted mb-3">{t('pomo.tasks_hint')}</p>

        <form
          onSubmit={(e) => { e.preventDefault(); addTask(); }}
          className="flex gap-2 mb-3"
        >
          <input
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            placeholder={t('pomo.task_placeholder')}
            className="flex-1 min-w-0 border border-line rounded-xl px-3 py-2 bg-paper/90 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30"
          />
          <Button type="submit" size="sm" disabled={!taskInput.trim()}>
            +
          </Button>
        </form>

        <AnimatePresence>
          {tasks.map((task, i) => {
            const done = completedTasks.has(i);
            return (
              <motion.div
                key={`${i}-${task}`}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="flex items-center gap-2 py-1.5 group">
                  <button
                    onClick={() => toggleTask(i)}
                    className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-colors shrink-0 ${
                      done ? 'bg-safe border-safe' : 'border-line hover:border-accent'
                    }`}
                  >
                    {done && <span className="text-white text-xs">✓</span>}
                  </button>
                  <span className={`flex-1 text-sm ${done ? 'line-through text-muted' : ''}`}>
                    {task}
                  </span>
                  <button
                    onClick={() => removeTask(i)}
                    className="text-muted hover:text-danger text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    ✕
                  </button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {tasks.length === 0 && (
          <p className="text-xs text-muted text-center py-3">{t('pomo.no_tasks')}</p>
        )}
      </motion.div>

      {/* Reward Animation */}
      <AnimatePresence>
        {showReward && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
          >
            <div className="bg-panel/95 backdrop-blur-md border border-safe/30 rounded-3xl px-10 py-8 shadow-lg text-center">
              <motion.span
                className="text-6xl block"
                animate={{ rotate: [0, -10, 10, -10, 0], scale: [1, 1.2, 1] }}
                transition={{ duration: 0.6 }}
              >
                🎉
              </motion.span>
              <p className="font-heading font-bold text-lg mt-3">{t('pomo.reward_title')}</p>
              <p className="text-muted text-sm mt-1">
                {t('pomo.reward_desc', { count: todayCount })}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
