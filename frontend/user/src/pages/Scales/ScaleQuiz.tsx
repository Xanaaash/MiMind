import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { getCatalog, scoreScale } from '../../api/scales';
import type { ScaleCatalogItem } from '../../types';
import Button from '../../components/Button/Button';
import Loading from '../../components/Loading/Loading';

export default function ScaleQuiz() {
  const { scaleId } = useParams<{ scaleId: string }>();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const [scale, setScale] = useState<ScaleCatalogItem | null>(null);
  const [answers, setAnswers] = useState<Record<string, number | boolean>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const lang = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';

  useEffect(() => {
    if (!scaleId) return;
    getCatalog().then((catalog) => {
      const item = catalog[scaleId];
      if (item) {
        setScale(item);
        const initial: Record<string, number | boolean> = {};
        item.question_bank.questions.forEach((q) => {
          initial[q.question_id] = scaleId === 'cssrs' ? false : 0;
        });
        setAnswers(initial);
      }
      setLoading(false);
    });
  }, [scaleId]);

  if (loading || !scale) return <Loading text={t('common.loading')} />;

  const questions = scale.question_bank.questions;
  const labels = scale.question_bank.answer_labels?.[lang]
    ?? scale.question_bank.answer_labels?.['zh-CN']
    ?? null;
  const total = questions.length;
  const question = questions[currentIndex];
  const isCssrs = scaleId === 'cssrs';
  const progress = ((currentIndex + 1) / total) * 100;

  const handleAnswer = (value: number | boolean) => {
    setAnswers((prev) => ({ ...prev, [question.question_id]: value }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      let payload: { scale_id: string; answers: unknown };
      if (isCssrs) {
        payload = { scale_id: scaleId!, answers };
      } else {
        const arr = questions.map((q) => Number(answers[q.question_id] ?? 0));
        payload = { scale_id: scaleId!, answers: arr };
      }
      const result = await scoreScale(payload.scale_id, payload.answers);
      navigate(`/scales/${scaleId}/result`, { state: { result } });
    } finally {
      setSubmitting(false);
    }
  };

  const isLast = currentIndex === total - 1;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-muted mb-2">
          <span>{scale.display_name}</span>
          <span>{t('scales.progress', { current: currentIndex + 1, total })}</span>
        </div>
        <div className="h-2 bg-cream rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-accent rounded-full"
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -40 }}
          transition={{ duration: 0.25 }}
          className="bg-panel border border-line rounded-2xl p-8 shadow-sm"
        >
          <h2 className="font-heading text-xl font-bold mb-6">
            {currentIndex + 1}. {question.text[lang] || question.text['zh-CN'] || question.text['en-US'] || question.question_id}
          </h2>

          {isCssrs ? (
            <div className="grid gap-3">
              {[false, true].map((val) => (
                <button
                  key={String(val)}
                  onClick={() => handleAnswer(val)}
                  className={`
                    text-left px-5 py-4 rounded-xl border-2 transition-all font-medium
                    ${answers[question.question_id] === val
                      ? 'border-accent bg-accent-soft text-accent'
                      : 'border-line bg-paper hover:border-accent/30'
                    }
                  `}
                >
                  {val ? '是 / Yes' : '否 / No'}
                </button>
              ))}
            </div>
          ) : labels ? (
            <div className="grid gap-3">
              {labels.map((label, value) => (
                <button
                  key={value}
                  onClick={() => handleAnswer(value)}
                  className={`
                    text-left px-5 py-4 rounded-xl border-2 transition-all font-medium
                    ${answers[question.question_id] === value
                      ? 'border-accent bg-accent-soft text-accent'
                      : 'border-line bg-paper hover:border-accent/30'
                    }
                  `}
                >
                  <span className="text-muted mr-2">{value}</span> {label}
                </button>
              ))}
            </div>
          ) : (
            <input
              type="range"
              min={0}
              max={4}
              value={Number(answers[question.question_id] ?? 0)}
              onChange={(e) => handleAnswer(Number(e.target.value))}
              className="w-full accent-accent"
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <Button
          variant="ghost"
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
        >
          {t('scales.prev')}
        </Button>

        {isLast ? (
          <Button onClick={handleSubmit} loading={submitting}>
            {t('scales.submit')}
          </Button>
        ) : (
          <Button onClick={() => setCurrentIndex((i) => i + 1)}>
            {t('scales.next')}
          </Button>
        )}
      </div>
    </div>
  );
}
