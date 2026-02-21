import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { getCatalog, scoreScale } from '../../api/scales';
import type { ScaleCatalogItem } from '../../types';
import Button from '../../components/Button/Button';
import Loading from '../../components/Loading/Loading';
import { useAuthStore } from '../../stores/auth';
import { toast } from '../../stores/toast';
import { SCALE_INTRO_KEYS, SCALE_NAME_KEYS } from '../../utils/assessmentCopy';

type ScaleAnswer = number | boolean | null;

type Scl90DraftPayload = {
  version: 1;
  currentPage: number;
  answers: Record<string, ScaleAnswer>;
};

type Scl90Group = {
  key: string;
  title: string;
  start: number;
  end: number;
  questions: Array<{ index: number; questionId: string }>;
};

const SCL90_DIMENSION_LABEL_KEYS: Record<string, string> = {
  somatization: 'scales.dim_somatization',
  obsessive_compulsive: 'scales.dim_obsessive_compulsive',
  interpersonal_sensitivity: 'scales.dim_interpersonal_sensitivity',
  depression: 'scales.dim_depression',
  anxiety: 'scales.dim_anxiety',
  hostility: 'scales.dim_hostility',
  phobic_anxiety: 'scales.dim_phobic_anxiety',
  paranoid_ideation: 'scales.dim_paranoid_ideation',
  psychoticism: 'scales.dim_psychoticism',
};

const SCL90_DIMENSION_ORDER = [
  'somatization',
  'obsessive_compulsive',
  'interpersonal_sensitivity',
  'depression',
  'anxiety',
  'hostility',
  'phobic_anxiety',
  'paranoid_ideation',
  'psychoticism',
];

const EMPTY_QUESTIONS: ScaleCatalogItem['question_bank']['questions'] = [];

function buildInitialAnswers(scaleId: string, scale: ScaleCatalogItem): Record<string, ScaleAnswer> {
  const initial: Record<string, ScaleAnswer> = {};
  scale.question_bank.questions.forEach((question) => {
    if (scaleId === 'cssrs') {
      initial[question.question_id] = false;
      return;
    }
    initial[question.question_id] = scaleId === 'scl90' ? null : 0;
  });
  return initial;
}

function getScl90DraftKey(userId: string | null, scaleId: string): string {
  return `mc_scale_draft_${userId ?? 'guest'}_${scaleId}`;
}

function getQuestionDimension(question: ScaleCatalogItem['question_bank']['questions'][number]): string {
  const withDimension = question as typeof question & { dimension?: string };
  return question.dimension_key ?? withDimension.dimension ?? 'general';
}

function isValidScl90Answer(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 4;
}

export default function ScaleQuiz() {
  const { scaleId } = useParams<{ scaleId: string }>();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const { userId } = useAuthStore();

  const [scale, setScale] = useState<ScaleCatalogItem | null>(null);
  const [answers, setAnswers] = useState<Record<string, ScaleAnswer>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [restored, setRestored] = useState(false);

  const lang = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';

  useEffect(() => {
    if (!scaleId) return;
    getCatalog()
      .then((catalog) => {
        const item = catalog[scaleId];
        if (item) {
          setScale(item);
          const initial = buildInitialAnswers(scaleId, item);
          let restoredPage = 0;
          let isRestored = false;

          if (scaleId === 'scl90') {
            const raw = localStorage.getItem(getScl90DraftKey(userId, scaleId));
            if (raw) {
              try {
                const draft = JSON.parse(raw) as Scl90DraftPayload;
                if (
                  draft.version === 1
                  && typeof draft.currentPage === 'number'
                  && Number.isFinite(draft.currentPage)
                  && draft.answers
                  && typeof draft.answers === 'object'
                ) {
                  item.question_bank.questions.forEach((question) => {
                    const value = draft.answers[question.question_id];
                    if (isValidScl90Answer(value)) {
                      initial[question.question_id] = value;
                    }
                  });
                  restoredPage = Math.max(0, Math.floor(draft.currentPage));
                  isRestored = true;
                }
              } catch {
                localStorage.removeItem(getScl90DraftKey(userId, scaleId));
              }
            }
          }

          setAnswers(initial);
          setCurrentIndex(0);
          setCurrentPage(restoredPage);
          setRestored(isRestored);
          return;
        }
        setRestored(false);
      })
      .finally(() => setLoading(false));
  }, [scaleId, userId]);

  const questions = scale?.question_bank.questions ?? EMPTY_QUESTIONS;
  const labels = scale?.question_bank.answer_labels?.[lang]
    ?? scale?.question_bank.answer_labels?.['zh-CN']
    ?? null;
  const total = questions.length;
  const question = questions[currentIndex];
  const isCssrs = scaleId === 'cssrs';
  const isScl90 = scaleId === 'scl90';

  const scl90Groups = useMemo<Scl90Group[]>(() => {
    if (!isScl90) return [];

    const grouped = new Map<string, Array<{ index: number; questionId: string }>>();
    questions.forEach((item, index) => {
      const dimension = getQuestionDimension(item);
      const list = grouped.get(dimension) ?? [];
      list.push({ index, questionId: item.question_id });
      grouped.set(dimension, list);
    });

    const orderedKeys = Array.from(grouped.keys()).sort((a, b) => {
      const aOrder = SCL90_DIMENSION_ORDER.indexOf(a);
      const bOrder = SCL90_DIMENSION_ORDER.indexOf(b);
      if (aOrder < 0 && bOrder < 0) return a.localeCompare(b);
      if (aOrder < 0) return 1;
      if (bOrder < 0) return -1;
      return aOrder - bOrder;
    });

    return orderedKeys.map((key) => {
      const groupedQuestions = grouped.get(key) ?? [];
      const indexes = groupedQuestions.map((item) => item.index);
      const first = Math.min(...indexes);
      const last = Math.max(...indexes);
      return {
        key,
        title: t(SCL90_DIMENSION_LABEL_KEYS[key] ?? '', { defaultValue: key }),
        start: first + 1,
        end: last + 1,
        questions: groupedQuestions,
      };
    });
  }, [isScl90, questions, t]);

  useEffect(() => {
    if (!isScl90 || scl90Groups.length === 0) return;
    setCurrentPage((prev) => Math.min(Math.max(prev, 0), scl90Groups.length - 1));
  }, [isScl90, scl90Groups.length]);

  useEffect(() => {
    if (!isScl90 || !scaleId || loading || !scale || scl90Groups.length === 0) return;
    const payload: Scl90DraftPayload = {
      version: 1,
      currentPage,
      answers,
    };
    localStorage.setItem(getScl90DraftKey(userId, scaleId), JSON.stringify(payload));
  }, [answers, currentPage, isScl90, loading, scale, scaleId, scl90Groups.length, userId]);

  const currentGroup = isScl90 ? scl90Groups[currentPage] : null;
  const totalPages = isScl90 ? scl90Groups.length : total;
  const currentStep = isScl90 ? currentPage + 1 : currentIndex + 1;
  const progress = totalPages > 0 ? (currentStep / totalPages) * 100 : 0;
  const answeredInGroup = currentGroup
    ? currentGroup.questions.filter((entry) => isValidScl90Answer(answers[entry.questionId])).length
    : 0;
  const answeredTotal = isScl90
    ? questions.filter((entry) => isValidScl90Answer(answers[entry.question_id])).length
    : 0;
  const isCurrentGroupComplete = currentGroup
    ? currentGroup.questions.every((entry) => isValidScl90Answer(answers[entry.questionId]))
    : true;

  const setAnswer = (questionId: string, value: number | boolean) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleSubmit = async () => {
    if (!scaleId || !scale) return;
    if (isScl90 && !isCurrentGroupComplete) {
      toast.warning(t('scales.errors.complete_section'));
      return;
    }
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
      if (isScl90 && scaleId) {
        localStorage.removeItem(getScl90DraftKey(userId, scaleId));
      }
      navigate(`/scales/${scaleId}/result`, { state: { result } });
    } finally {
      setSubmitting(false);
    }
  };

  const goNext = () => {
    if (isScl90) {
      if (!isCurrentGroupComplete) {
        toast.warning(t('scales.errors.complete_section'));
        return;
      }
      setCurrentPage((prev) => Math.min(prev + 1, totalPages - 1));
      return;
    }
    setCurrentIndex((prev) => Math.min(prev + 1, total - 1));
  };

  const goPrev = () => {
    if (isScl90) {
      setCurrentPage((prev) => Math.max(0, prev - 1));
      return;
    }
    setCurrentIndex((prev) => Math.max(0, prev - 1));
  };

  const clearScl90Draft = () => {
    if (!isScl90 || !scaleId || !scale) return;
    localStorage.removeItem(getScl90DraftKey(userId, scaleId));
    setAnswers(buildInitialAnswers(scaleId, scale));
    setCurrentPage(0);
    setRestored(false);
  };

  const isLast = currentStep === totalPages;

  if (loading || !scale || (!isScl90 && !question)) {
    return <Loading text={t('common.loading')} />;
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-muted mb-2">
          <span>
            {t(SCALE_NAME_KEYS[scaleId ?? ''] ?? '', {
              defaultValue: scale.display_name || (scaleId ?? '').toUpperCase(),
            })}
          </span>
          <span>
            {isScl90
              ? t('scales.section_progress', { current: currentStep, total: totalPages })
              : t('scales.progress', { current: currentStep, total })}
          </span>
        </div>
        <div className="h-2 bg-cream rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-accent rounded-full"
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        <p className="mt-3 text-xs text-muted leading-relaxed">
          {t(SCALE_INTRO_KEYS[scaleId ?? ''] ?? 'scales.intro.generic')}
        </p>
        {isScl90 ? (
          <div className="mt-2 text-xs text-muted space-y-1">
            <p>{t('scales.answered_progress', { answered: answeredTotal, total })}</p>
            <p>{t('scales.resume_hint')}</p>
            {restored ? <p className="text-accent">{t('scales.draft_restored')}</p> : null}
          </div>
        ) : null}
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={isScl90 ? `group-${currentPage}` : `question-${currentIndex}`}
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -40 }}
          transition={{ duration: 0.25 }}
          className="bg-panel border border-line rounded-2xl p-8 shadow-sm"
        >
          {isScl90 && currentGroup ? (
            <div className="space-y-5">
              <div className="rounded-xl border border-line bg-cream/60 px-4 py-3">
                <p className="text-xs font-semibold tracking-wide text-accent uppercase">
                  {t('scales.group_range', { start: currentGroup.start, end: currentGroup.end })}
                </p>
                <h2 className="font-heading text-xl font-bold mt-1">{currentGroup.title}</h2>
                <p className="text-xs text-muted mt-1">
                  {t('scales.group_answered', { answered: answeredInGroup, total: currentGroup.questions.length })}
                </p>
              </div>

              {currentGroup.questions.map(({ index, questionId }) => {
                const item = questions[index];
                const prompt = item.text[lang] || item.text['zh-CN'] || item.text['en-US'] || questionId;
                return (
                  <div key={questionId} className="border border-line rounded-xl bg-paper p-4">
                    <h3 className="font-semibold mb-3">
                      {index + 1}. {prompt}
                    </h3>
                    {labels ? (
                      <div className="grid gap-2">
                        {labels.map((label, value) => (
                          <button
                            key={value}
                            type="button"
                            onClick={() => setAnswer(questionId, value)}
                            aria-pressed={answers[questionId] === value}
                            className={`
                              text-left px-4 py-3 rounded-xl border-2 transition-all font-medium
                              ${answers[questionId] === value
                                ? 'border-accent bg-accent-soft text-accent'
                                : 'border-line bg-paper hover:border-accent/30'
                              }
                            `}
                          >
                            <span className="text-muted mr-2">{value}</span> {label}
                          </button>
                        ))}
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          ) : (
            <>
              <h2 className="font-heading text-xl font-bold mb-6">
                {currentIndex + 1}. {question.text[lang] || question.text['zh-CN'] || question.text['en-US'] || question.question_id}
              </h2>

              {isCssrs ? (
                <div className="grid gap-3">
                  {[false, true].map((val) => (
                    <button
                      key={String(val)}
                      type="button"
                      onClick={() => setAnswer(question.question_id, val)}
                      aria-pressed={answers[question.question_id] === val}
                      className={`
                        text-left px-5 py-4 rounded-xl border-2 transition-all font-medium
                        ${answers[question.question_id] === val
                          ? 'border-accent bg-accent-soft text-accent'
                          : 'border-line bg-white hover:border-accent/30'
                        }
                      `}
                    >
                      {val ? t('onboarding.yes') : t('onboarding.no')}
                    </button>
                  ))}
                </div>
              ) : labels ? (
                <div className="grid gap-3">
                  {labels.map((label, value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setAnswer(question.question_id, value)}
                      aria-pressed={answers[question.question_id] === value}
                      className={`
                        text-left px-5 py-4 rounded-xl border-2 transition-all font-medium
                        ${answers[question.question_id] === value
                          ? 'border-accent bg-accent-soft text-accent'
                          : 'border-line bg-white hover:border-accent/30'
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
                  onChange={(e) => setAnswer(question.question_id, Number(e.target.value))}
                  aria-label={question.text[lang] || question.text['zh-CN'] || question.text['en-US'] || question.question_id}
                  className="w-full accent-accent"
                />
              )}
            </>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <Button
          variant="ghost"
          onClick={goPrev}
          disabled={(isScl90 ? currentPage : currentIndex) === 0}
        >
          {t('scales.prev')}
        </Button>

        <div className="flex items-center gap-3">
          {isScl90 ? (
            <Button variant="ghost" onClick={clearScl90Draft} disabled={submitting}>
              {t('scales.clear_progress')}
            </Button>
          ) : null}
          {isLast ? (
            <Button onClick={handleSubmit} loading={submitting} disabled={isScl90 && !isCurrentGroupComplete}>
              {t('scales.submit')}
            </Button>
          ) : (
            <Button onClick={goNext} disabled={isScl90 && !isCurrentGroupComplete}>
              {t('scales.next')}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
