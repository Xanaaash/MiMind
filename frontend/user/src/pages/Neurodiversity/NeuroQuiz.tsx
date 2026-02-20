import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Button from '../../components/Button/Button';
import NeurodiversityDisclaimer from '../../components/Neurodiversity/NeurodiversityDisclaimer';
import { getNeuroScale } from '../../data/neuroScales';

export default function NeuroQuiz() {
  const { scaleId } = useParams<{ scaleId: string }>();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const scale = getNeuroScale(scaleId ?? '');

  const [disclaimerPassed, setDisclaimerPassed] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});

  const handleAccept = useCallback(() => setDisclaimerPassed(true), []);
  const handleDecline = useCallback(() => navigate('/neurodiversity'), [navigate]);

  if (!scale) {
    return (
      <div className="text-center py-20">
        <p className="text-muted">{t('common.error')}</p>
        <Button variant="ghost" onClick={() => navigate('/neurodiversity')} className="mt-4">
          {t('common.back')}
        </Button>
      </div>
    );
  }

  if (!disclaimerPassed) {
    return (
      <NeurodiversityDisclaimer
        scaleId={scale.id}
        onAccept={handleAccept}
        onDecline={handleDecline}
      />
    );
  }

  const questions = scale.questions;
  const question = questions[currentIndex];
  const lang = i18n.language;
  const labels = scale.answerLabels[lang] ?? scale.answerLabels['zh-CN'];
  const answeredCount = Object.keys(answers).length;
  const progress = answeredCount / questions.length;

  const handleAnswer = (value: number) => {
    setAnswers((prev) => ({ ...prev, [question.id]: value }));
    if (currentIndex < questions.length - 1) {
      setTimeout(() => setCurrentIndex((i) => i + 1), 200);
    }
  };

  const handleSubmit = () => {
    const arr = questions.map((q) => answers[q.id] ?? 0);
    const result = scale.score(arr);
    navigate(`/neurodiversity/${scale.id}/result`, { state: { result, scaleId: scale.id } });
  };

  const canSubmit = answeredCount === questions.length;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => navigate('/neurodiversity')}
          className="text-sm text-muted hover:text-ink transition-colors"
        >
          ← {t('neuro.back')}
        </button>
        <span className="text-xs text-muted">{t(scale.nameKey)}</span>
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 bg-line rounded-full mb-6 overflow-hidden">
        <motion.div
          className="h-full bg-accent rounded-full"
          animate={{ width: `${progress * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      <p className="text-xs text-muted text-center mb-6">
        {t('scales.progress', { current: currentIndex + 1, total: questions.length })}
      </p>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={question.id}
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -30 }}
          transition={{ duration: 0.2 }}
          className="bg-panel border border-line rounded-2xl p-5 sm:p-6 mb-6"
        >
          <p className="font-heading font-bold text-base sm:text-lg leading-relaxed">
            {question.text[lang] ?? question.text['zh-CN']}
          </p>

          <div className="mt-5 space-y-2">
            {labels.map((label, idx) => {
              const selected = answers[question.id] === idx;
              return (
                <button
                  key={idx}
                  onClick={() => handleAnswer(idx)}
                  className={`
                    w-full text-left px-4 py-3 rounded-xl border-2 transition-all text-sm font-medium
                    ${selected
                      ? 'border-accent bg-accent-soft text-accent'
                      : 'border-line bg-paper hover:border-accent/30'
                    }
                  `}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="ghost"
          size="sm"
          disabled={currentIndex === 0}
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
        >
          {t('scales.prev')}
        </Button>

        {currentIndex < questions.length - 1 ? (
          <Button
            size="sm"
            disabled={answers[question.id] === undefined}
            onClick={() => setCurrentIndex((i) => i + 1)}
          >
            {t('scales.next')}
          </Button>
        ) : (
          <Button size="sm" disabled={!canSubmit} onClick={handleSubmit}>
            {t('scales.submit')}
          </Button>
        )}
      </div>
    </div>
  );
}
