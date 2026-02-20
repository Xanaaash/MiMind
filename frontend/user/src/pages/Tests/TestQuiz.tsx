import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { getTestDetail, submitTest } from '../../api/tests';
import { useAuthStore } from '../../stores/auth';
import type { TestCatalogItem } from '../../types';
import Button from '../../components/Button/Button';
import Loading from '../../components/Loading/Loading';

function inferRange(answerRange: string) {
  const text = answerRange.toLowerCase();
  if (text.includes('-100 to 100')) return { min: -100, max: 100 };
  if (text.includes('13 to 90')) return { min: 13, max: 90 };
  return { min: 0, max: 100 };
}

export default function TestQuiz() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const userId = useAuthStore((s) => s.userId);
  const lang = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';

  const [test, setTest] = useState<TestCatalogItem | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!testId) return;
    getTestDetail(testId).then((data) => {
      setTest(data);
      const initial: Record<string, number> = {};
      const range = inferRange(data.answer_range);
      data.question_bank.questions.forEach((q) => {
        initial[q.question_id] = q.dimension_key === 'chronological_age' ? 25 : Math.round((range.min + range.max) / 2);
      });
      setAnswers(initial);
      setLoading(false);
    });
  }, [testId]);

  if (loading || !test) return <Loading text={t('common.loading')} />;

  const questions = test.question_bank.questions;
  const total = questions.length;
  const question = questions[currentIndex];
  const range = inferRange(test.answer_range);
  const progress = ((currentIndex + 1) / total) * 100;

  const handleSubmit = async () => {
    if (!userId || !testId) return;
    setSubmitting(true);
    try {
      const sums: Record<string, number> = {};
      const counts: Record<string, number> = {};
      questions.forEach((q) => {
        const val = answers[q.question_id] ?? 0;
        sums[q.dimension_key] = (sums[q.dimension_key] ?? 0) + val;
        counts[q.dimension_key] = (counts[q.dimension_key] ?? 0) + 1;
      });
      const aggregated: Record<string, number> = {};
      test.required_answer_keys.forEach((key) => {
        aggregated[key] = counts[key] ? Math.round(sums[key] / counts[key]) : 0;
      });
      const result = await submitTest(userId, testId, aggregated);
      navigate(`/tests/${testId}/result${location.search}`, { state: { result } });
    } finally {
      setSubmitting(false);
    }
  };

  const isLast = currentIndex === total - 1;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-muted mb-2">
          <span>{test.display_name}</span>
          <span>{t('scales.progress', { current: currentIndex + 1, total })}</span>
        </div>
        <div className="h-2 bg-cream rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-warn rounded-full"
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

          <div className="space-y-3">
            <input
              type="range"
              min={range.min}
              max={range.max}
              value={answers[question.question_id] ?? 0}
              onChange={(e) => setAnswers((prev) => ({ ...prev, [question.question_id]: Number(e.target.value) }))}
              aria-label={question.text[lang] || question.text['zh-CN'] || question.text['en-US'] || question.question_id}
              className="w-full accent-warn h-2"
            />
            <div className="flex justify-between text-sm text-muted">
              <span>{range.min}</span>
              <span className="text-lg font-bold text-ink">{answers[question.question_id]}</span>
              <span>{range.max}</span>
            </div>
          </div>
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
            {t('tests.submit')}
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
