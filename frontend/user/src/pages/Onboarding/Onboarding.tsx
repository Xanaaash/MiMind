import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { getCatalog } from '../../api/scales';
import { submitAssessment } from '../../api/auth';
import { useAuthStore } from '../../stores/auth';
import { toast } from '../../stores/toast';
import { markAssessmentComplete } from '../../components/AssessmentGate/AssessmentGate';
import type { ScaleCatalogItem, ScaleQuestion, TriageChannel } from '../../types';
import Button from '../../components/Button/Button';
import Loading from '../../components/Loading/Loading';
import { SCALE_INTRO_KEYS, SCALE_NAME_KEYS } from '../../utils/assessmentCopy';

const REQUIRED_SCALES = ['phq9', 'gad7', 'pss10', 'cssrs'] as const;
type RequiredScaleId = (typeof REQUIRED_SCALES)[number];

type AssessmentDraft = {
  phq9: Array<number | null>;
  gad7: Array<number | null>;
  pss10: Array<number | null>;
  cssrs: Record<string, boolean | null>;
};

type Step = {
  scaleId: RequiredScaleId;
  questionIndex: number;
  question: ScaleQuestion;
};

function toChannel(value: unknown): TriageChannel | null {
  if (typeof value !== 'string') {
    return null;
  }
  const normalized = value.trim().toUpperCase();
  if (normalized === 'GREEN' || normalized === 'YELLOW' || normalized === 'RED') {
    return normalized as TriageChannel;
  }
  return null;
}

function buildInitialDraft(catalog: Record<string, ScaleCatalogItem>): AssessmentDraft {
  const createLikert = (scaleId: RequiredScaleId): Array<number | null> => {
    const count = catalog[scaleId].question_bank.questions.length;
    return Array.from({ length: count }, () => null);
  };

  const cssrsQuestions = catalog.cssrs.question_bank.questions;
  const cssrs: Record<string, boolean | null> = {};
  cssrsQuestions.forEach((question) => {
    cssrs[question.question_id] = null;
  });

  return {
    phq9: createLikert('phq9'),
    gad7: createLikert('gad7'),
    pss10: createLikert('pss10'),
    cssrs,
  };
}

function buildSteps(catalog: Record<string, ScaleCatalogItem>): Step[] {
  return REQUIRED_SCALES.flatMap((scaleId) =>
    catalog[scaleId].question_bank.questions.map((question, questionIndex) => ({
      scaleId,
      questionIndex,
      question,
    })),
  );
}

function getCurrentAnswer(draft: AssessmentDraft, step: Step): number | boolean | null {
  if (step.scaleId === 'cssrs') {
    return draft.cssrs[step.question.question_id] ?? null;
  }
  return draft[step.scaleId][step.questionIndex];
}

function isScaleCore(scaleId: RequiredScaleId): boolean {
  return scaleId === 'phq9' || scaleId === 'gad7';
}

export default function Onboarding() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get('returnTo');
  const { userId, channel, setChannel } = useAuthStore();

  const [catalog, setCatalog] = useState<Record<string, ScaleCatalogItem> | null>(null);
  const [draft, setDraft] = useState<AssessmentDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  const lang = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';

  useEffect(() => {
    if (!userId) {
      navigate('/auth');
      return;
    }
    if (channel && !returnTo) {
      navigate('/home');
    }
  }, [userId, channel, returnTo, navigate]);

  useEffect(() => {
    getCatalog()
      .then((data) => {
        const missing = REQUIRED_SCALES.filter((scaleId) => !data[scaleId]);
        if (missing.length > 0) {
          throw new Error(`Missing required scales: ${missing.join(', ')}`);
        }

        setCatalog(data);
        setDraft(buildInitialDraft(data));
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : String(error);
        toast.error(message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const steps = useMemo(() => {
    if (!catalog) return [];
    return buildSteps(catalog);
  }, [catalog]);

  if (loading || !catalog || !draft || steps.length === 0) {
    return <Loading fullScreen text={t('common.loading')} />;
  }

  const step = steps[currentStepIndex];
  const scale = catalog[step.scaleId];
  const labels = scale.question_bank.answer_labels?.[lang]
    ?? scale.question_bank.answer_labels?.['zh-CN']
    ?? null;
  const answer = getCurrentAnswer(draft, step);
  const isAnswered = answer !== null;
  const isFirst = currentStepIndex === 0;
  const isLast = currentStepIndex === steps.length - 1;
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const setLikertAnswer = (value: number) => {
    setDraft((prev) => {
      if (!prev) return prev;
      if (step.scaleId === 'cssrs') return prev;
      const scaleId = step.scaleId;
      const next = [...prev[scaleId]];
      next[step.questionIndex] = value;
      return {
        ...prev,
        [scaleId]: next,
      };
    });
  };

  const setCssrsAnswer = (value: boolean) => {
    setDraft((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        cssrs: {
          ...prev.cssrs,
          [step.question.question_id]: value,
        },
      };
    });
  };

  const goNext = () => {
    if (!isAnswered || isLast) return;
    setCurrentStepIndex((prev) => prev + 1);
  };

  const goPrev = () => {
    if (isFirst) return;
    setCurrentStepIndex((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    if (!userId || submitting) return;
    setSubmitting(true);

    try {
      const numericScale = (scaleId: 'phq9' | 'gad7' | 'pss10') => {
        const values = draft[scaleId];
        if (values.some((value) => value === null)) {
          throw new Error(t('onboarding.errors.incomplete'));
        }
        return values as number[];
      };

      const cssrsEntries = Object.entries(draft.cssrs);
      const hasNull = cssrsEntries.some(([, value]) => value === null);
      if (hasNull) {
        throw new Error(t('onboarding.errors.incomplete'));
      }

      const responses = {
        phq9: numericScale('phq9'),
        gad7: numericScale('gad7'),
        pss10: numericScale('pss10'),
        cssrs: Object.fromEntries(
          cssrsEntries.map(([key, value]) => [key, Boolean(value)]),
        ),
      };

      const result = await submitAssessment(userId, responses);
      const triage = result.triage as { channel?: unknown } | undefined;
      const nextChannel = toChannel(triage?.channel);
      if (!nextChannel) {
        throw new Error(t('onboarding.errors.no_channel'));
      }

      setChannel(nextChannel);
      markAssessmentComplete();
      toast.success(t('onboarding.submit_success'));
      navigate(returnTo || '/home');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-3xl bg-panel border border-line rounded-3xl p-8 shadow-lg"
      >
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold">{t('onboarding.title')}</h1>
          <p className="text-muted text-sm mt-1">{t('onboarding.subtitle')}</p>
          <p className="text-xs mt-2 text-muted">{t('onboarding.note')}</p>
        </div>

        <div className="mb-7">
          <div className="flex justify-between text-xs text-muted mb-2">
            <span>
              {isScaleCore(step.scaleId) ? t('onboarding.core_scale') : t('onboarding.safety_scale')}
            </span>
            <span>{t('scales.progress', { current: currentStepIndex + 1, total: steps.length })}</span>
          </div>
          <div className="h-2 bg-cream rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-accent rounded-full"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.2 }}
            />
          </div>
        </div>

        <div className="bg-paper rounded-2xl border border-line p-6">
          <p className="text-xs font-semibold text-accent uppercase tracking-wider mb-2">
            {t(SCALE_NAME_KEYS[step.scaleId] ?? '', { defaultValue: step.scaleId.toUpperCase() })}
          </p>
          <p className="text-xs text-muted mb-3 leading-relaxed">
            {t(SCALE_INTRO_KEYS[step.scaleId] ?? 'scales.intro.generic')}
          </p>
          <h2 className="font-heading text-xl font-bold mb-5">
            {step.question.text[lang] ?? step.question.text['zh-CN'] ?? step.question.text['en-US'] ?? step.question.question_id}
          </h2>

          {step.scaleId === 'cssrs' ? (
            <div className="grid gap-3">
              {[false, true].map((value) => (
                <button
                  key={String(value)}
                  type="button"
                  onClick={() => setCssrsAnswer(value)}
                  aria-pressed={answer === value}
                  className={`text-left px-4 py-3 rounded-xl border-2 transition-all ${
                    answer === value ? 'border-accent bg-accent-soft text-accent' : 'border-line hover:border-accent/30'
                  }`}
                >
                  {value ? t('onboarding.yes') : t('onboarding.no')}
                </button>
              ))}
            </div>
          ) : (
            <div className="grid gap-3">
              {(labels ?? []).map((label, value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setLikertAnswer(value)}
                  aria-pressed={answer === value}
                  className={`text-left px-4 py-3 rounded-xl border-2 transition-all ${
                    answer === value ? 'border-accent bg-accent-soft text-accent' : 'border-line hover:border-accent/30'
                  }`}
                >
                  <span className="text-muted mr-2">{value}</span>
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-between mt-6">
          <Button variant="ghost" onClick={goPrev} disabled={isFirst || submitting}>
            {t('scales.prev')}
          </Button>

          {isLast ? (
            <Button onClick={handleSubmit} loading={submitting} disabled={!isAnswered}>
              {t('onboarding.submit')}
            </Button>
          ) : (
            <Button onClick={goNext} disabled={!isAnswered || submitting}>
              {t('scales.next')}
            </Button>
          )}
        </div>
      </motion.div>
    </div>
  );
}
