import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { createJournalEntry, getJournalTrend } from '../../api/tools';
import { useAuthStore } from '../../stores/auth';
import { toast } from '../../stores/toast';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import FieldError from '../../components/Form/FieldError';
import { maxLength, required, runValidators } from '../../utils/validators';

const MOODS = [
  { value: 'happy', emoji: '😊', color: 'bg-safe-soft' },
  { value: 'calm', emoji: '😌', color: 'bg-calm-soft' },
  { value: 'hopeful', emoji: '🌟', color: 'bg-warn-soft' },
  { value: 'tired', emoji: '😴', color: 'bg-cream' },
  { value: 'anxious', emoji: '😰', color: 'bg-warn-soft' },
  { value: 'sad', emoji: '😢', color: 'bg-calm-soft' },
  { value: 'angry', emoji: '😤', color: 'bg-danger-soft' },
];

export default function JournalPage() {
  const { t } = useTranslation();
  const userId = useAuthStore((s) => s.userId);

  const [mood, setMood] = useState('calm');
  const [energy, setEnergy] = useState(5);
  const [note, setNote] = useState('');
  const [noteError, setNoteError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [trendData, setTrendData] = useState<Array<{ date: string; energy: number }>>([]);

  useEffect(() => {
    if (!userId) return;
    getJournalTrend(userId, 7)
      .then((data) => {
        if (data.entries) {
          setTrendData(data.entries.map((e) => ({
            date: new Date(e.created_at).toLocaleDateString(),
            energy: e.energy,
          })));
        }
      })
      .catch(() => {});
  }, [userId]);

  const validateNote = (value: string): string | null => {
    return runValidators(value, [
      required(t('validation.required', { field: t('fields.note') })),
      maxLength(500, t('validation.max_length', { field: t('fields.note'), count: 500 })),
    ]);
  };

  const handleSave = async () => {
    if (!userId) return;
    const nextError = validateNote(note);
    setNoteError(nextError);
    if (nextError) {
      toast.error(nextError);
      return;
    }
    setSaving(true);
    try {
      await createJournalEntry(userId, mood, energy, note);
      setNote('');
      setNoteError(null);
      toast.success(t('journal.saved'));
      const data = await getJournalTrend(userId, 7);
      if (data.entries) {
        setTrendData(data.entries.map((e) => ({
          date: new Date(e.created_at).toLocaleDateString(),
          energy: e.energy,
        })));
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-heading text-3xl font-bold">{t('journal.title')}</h1>
        <p className="text-muted mt-1 mb-8">{t('journal.subtitle')}</p>
      </motion.div>

      {/* Mood selector */}
      <Card className="mb-6">
        <h3 className="font-heading font-bold mb-4">{t('journal.mood_label')}</h3>
        <div className="flex flex-wrap gap-3">
          {MOODS.map((m) => (
            <button
              key={m.value}
              onClick={() => setMood(m.value)}
              className={`
                flex flex-col items-center gap-1 px-4 py-3 rounded-xl border-2 transition-all
                ${mood === m.value
                  ? 'border-accent bg-accent-soft scale-105'
                  : `border-line ${m.color} hover:border-accent/30`
                }
              `}
            >
              <span className="text-2xl">{m.emoji}</span>
              <span className="text-xs font-medium">{t(`journal.moods.${m.value}`)}</span>
            </button>
          ))}
        </div>
      </Card>

      {/* Energy slider */}
      <Card className="mb-6">
        <h3 className="font-heading font-bold mb-4">{t('journal.energy_label')}</h3>
        <div className="flex items-center gap-4">
          <span className="text-muted text-sm">0</span>
          <input
            type="range"
            min={0}
            max={10}
            value={energy}
            onChange={(e) => setEnergy(Number(e.target.value))}
            aria-label={t('journal.energy_label')}
            className="flex-1 accent-accent h-2"
          />
          <span className="text-muted text-sm">10</span>
          <span className="text-2xl font-bold text-accent w-10 text-center">{energy}</span>
        </div>
      </Card>

      {/* Note */}
      <Card className="mb-6">
        <h3 className="font-heading font-bold mb-3">{t('journal.note_label')}</h3>
        <textarea
          value={note}
          onChange={(e) => {
            const value = e.target.value;
            setNote(value);
            if (noteError) {
              setNoteError(validateNote(value));
            }
          }}
          onBlur={() => setNoteError(validateNote(note))}
          placeholder={t('journal.note_placeholder')}
          rows={4}
          className={`w-full border rounded-xl px-4 py-3 bg-paper/90 focus:outline-none focus:ring-2 resize-none ${
            noteError ? 'border-danger focus:ring-danger/30' : 'border-line focus:ring-accent/30'
          }`}
        />
        <div className="flex items-center justify-between mt-2">
          <FieldError message={noteError} />
          <p className={`text-xs ${note.length > 500 ? 'text-danger' : 'text-muted'}`}>{note.length}/500</p>
        </div>
        <Button
          className="mt-3 w-full"
          onClick={handleSave}
          loading={saving}
        >
          {t('journal.save')}
        </Button>
      </Card>

      {/* Trend chart */}
      {trendData.length > 0 && (
        <Card>
          <h3 className="font-heading font-bold mb-4">{t('journal.trend_title')}</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <XAxis dataKey="date" tick={{ fill: '#785c55', fontSize: 11 }} />
                <YAxis domain={[0, 10]} tick={{ fill: '#785c55', fontSize: 11 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="energy"
                  stroke="#c6674f"
                  strokeWidth={2.5}
                  dot={{ fill: '#c6674f', strokeWidth: 0, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}
    </div>
  );
}
