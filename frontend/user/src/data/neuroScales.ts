export interface NeuroScale {
  id: string;
  nameKey: string;
  descKey: string;
  emoji: string;
  color: string;
  itemCount: number;
  dimensions: NeuroDimension[];
  questions: NeuroQuestion[];
  answerLabels: Record<string, string[]>;
  score: (answers: number[]) => NeuroScoreResult;
}

export interface NeuroDimension {
  key: string;
  nameKey: string;
  color: string;
}

export interface NeuroQuestion {
  id: string;
  text: Record<string, string>;
  dimension: string;
  reverseScored?: boolean;
}

export interface NeuroScoreResult {
  total: number;
  maxTotal: number;
  level: 'low' | 'moderate' | 'high';
  levelKey: string;
  dimensions: { key: string; nameKey: string; score: number; max: number; color: string }[];
  summaryKey: string;
}

// ─── ASRS v1.1 Screener (6 items) ──────────────────────────
const ASRS_QUESTIONS: NeuroQuestion[] = [
  { id: 'asrs-1', dimension: 'inattention', text: { 'zh-CN': '当一项任务中最困难的部分完成后，你是否经常难以完成收尾工作？', 'en-US': 'How often do you have difficulty finishing the final details of a project once the challenging parts are done?' } },
  { id: 'asrs-2', dimension: 'inattention', text: { 'zh-CN': '当你需要做一件需要条理性的事情时，你是否经常难以将事物整理有序？', 'en-US': 'How often do you have difficulty getting things in order when you have to do a task that requires organization?' } },
  { id: 'asrs-3', dimension: 'inattention', text: { 'zh-CN': '你是否经常难以记住约定或承诺？', 'en-US': 'How often do you have problems remembering appointments or obligations?' } },
  { id: 'asrs-4', dimension: 'hyperactivity', text: { 'zh-CN': '当你需要长时间坐着时，你是否经常坐立不安或扭动身体？', 'en-US': 'How often do you fidget or squirm when you have to sit down for a long time?' } },
  { id: 'asrs-5', dimension: 'hyperactivity', text: { 'zh-CN': '你是否经常感觉自己像被发动机驱动一样过度活跃？', 'en-US': 'How often do you feel overly active and compelled to do things, as if driven by a motor?' } },
  { id: 'asrs-6', dimension: 'impulsivity', text: { 'zh-CN': '当你在等候队列中时，你是否经常不耐烦？', 'en-US': 'How often do you feel restless or impatient when you have to wait in line?' } },
];

function scoreASRS(answers: number[]): NeuroScoreResult {
  const total = answers.reduce((s, v) => s + v, 0);
  const inattention = answers.slice(0, 3).reduce((s, v) => s + v, 0);
  const hyperactivity = answers.slice(3, 5).reduce((s, v) => s + v, 0);
  const impulsivity = answers[5] ?? 0;

  let flagged = 0;
  answers.slice(0, 3).forEach((v) => { if (v >= 2) flagged++; });
  answers.slice(3, 6).forEach((v) => { if (v >= 3) flagged++; });

  const level = flagged >= 4 ? 'high' : flagged >= 2 ? 'moderate' : 'low';

  return {
    total,
    maxTotal: 24,
    level,
    levelKey: `neuro.level_${level}`,
    dimensions: [
      { key: 'inattention', nameKey: 'neuro.dim_inattention', score: inattention, max: 12, color: '#e07a60' },
      { key: 'hyperactivity', nameKey: 'neuro.dim_hyperactivity', score: hyperactivity, max: 8, color: '#d4a843' },
      { key: 'impulsivity', nameKey: 'neuro.dim_impulsivity', score: impulsivity, max: 4, color: '#5cb87e' },
    ],
    summaryKey: `neuro.asrs_summary_${level}`,
  };
}

// ─── AQ-10 (Autism Quotient Short) ──────────────────────────
const AQ10_AGREE_SCORED = new Set([0, 6, 7, 9]);

const AQ10_QUESTIONS: NeuroQuestion[] = [
  { id: 'aq-1', dimension: 'social', text: { 'zh-CN': '我经常注意到别人没有注意到的小声音。', 'en-US': 'I often notice small sounds when others do not.' } },
  { id: 'aq-2', dimension: 'social', reverseScored: true, text: { 'zh-CN': '当我阅读一个故事时，我很容易想象出人物的样子。', 'en-US': 'When I\'m reading a story, I can easily imagine what the characters might look like.' } },
  { id: 'aq-3', dimension: 'attention', reverseScored: true, text: { 'zh-CN': '我觉得容易同时做好几件事。', 'en-US': 'I find it easy to do more than one thing at once.' } },
  { id: 'aq-4', dimension: 'attention', reverseScored: true, text: { 'zh-CN': '如果被打断，我能很快回到之前正在做的事情。', 'en-US': 'If there is an interruption, I can switch back to what I was doing very quickly.' } },
  { id: 'aq-5', dimension: 'communication', reverseScored: true, text: { 'zh-CN': '我觉得阅读别人话语中的「弦外之音」很容易。', 'en-US': 'I find it easy to "read between the lines" when someone is talking to me.' } },
  { id: 'aq-6', dimension: 'detail', reverseScored: true, text: { 'zh-CN': '我知道如何判断别人在听我说话时是否感到无聊。', 'en-US': 'I know how to tell if someone listening to me is getting bored.' } },
  { id: 'aq-7', dimension: 'detail', text: { 'zh-CN': '在社交场合中我经常不知道该怎么做。', 'en-US': 'When I talk on the phone, I\'m not sure when it\'s my turn to speak.' } },
  { id: 'aq-8', dimension: 'systemizing', text: { 'zh-CN': '我喜欢收集关于某些类别事物的信息（如汽车类型、鸟类、植物等）。', 'en-US': 'I like to collect information about categories of things (e.g., types of cars, birds, trains, plants).' } },
  { id: 'aq-9', dimension: 'communication', reverseScored: true, text: { 'zh-CN': '我觉得通过别人的面部表情判断他们的想法或感受很容易。', 'en-US': 'I find it easy to work out what someone is thinking or feeling just by looking at their face.' } },
  { id: 'aq-10', dimension: 'social', text: { 'zh-CN': '我觉得很难交到新朋友。', 'en-US': 'I find it difficult to make new friends.' } },
];

function scoreAQ10(answers: number[]): NeuroScoreResult {
  let total = 0;
  const dimScores: Record<string, number> = { social: 0, attention: 0, communication: 0, detail: 0, systemizing: 0 };
  const dimMax: Record<string, number> = { social: 3, attention: 2, communication: 2, detail: 2, systemizing: 1 };

  answers.forEach((v, i) => {
    const q = AQ10_QUESTIONS[i];
    let scored: number;
    if (AQ10_AGREE_SCORED.has(i)) {
      scored = v <= 1 ? 1 : 0;
    } else {
      scored = v >= 2 ? 1 : 0;
    }
    total += scored;
    dimScores[q.dimension] += scored;
  });

  const level = total >= 6 ? 'high' : total >= 3 ? 'moderate' : 'low';

  return {
    total,
    maxTotal: 10,
    level,
    levelKey: `neuro.level_${level}`,
    dimensions: [
      { key: 'social', nameKey: 'neuro.dim_social', score: dimScores.social, max: dimMax.social, color: '#6b8fd4' },
      { key: 'attention', nameKey: 'neuro.dim_attention_switch', score: dimScores.attention, max: dimMax.attention, color: '#e07a60' },
      { key: 'communication', nameKey: 'neuro.dim_communication', score: dimScores.communication, max: dimMax.communication, color: '#5cb87e' },
      { key: 'detail', nameKey: 'neuro.dim_detail', score: dimScores.detail, max: dimMax.detail, color: '#d4a843' },
      { key: 'systemizing', nameKey: 'neuro.dim_systemizing', score: dimScores.systemizing, max: dimMax.systemizing, color: '#9b7fd4' },
    ],
    summaryKey: `neuro.aq10_summary_${level}`,
  };
}

// ─── HSP Scale (27 items, simplified to 12 core items) ──────
const HSP_QUESTIONS: NeuroQuestion[] = [
  { id: 'hsp-1', dimension: 'excitation', text: { 'zh-CN': '当有很多事情同时发生时，我会感到不舒服。', 'en-US': 'I get uncomfortable when a lot of things are happening at once.' } },
  { id: 'hsp-2', dimension: 'excitation', text: { 'zh-CN': '当我需要在短时间内完成很多事情时，我会感到不知所措。', 'en-US': 'When I must compete or be observed while performing a task, I become so nervous that I do much worse.' } },
  { id: 'hsp-3', dimension: 'excitation', text: { 'zh-CN': '嘈杂的环境让我内心混乱。', 'en-US': 'I find noisy environments chaotic and overwhelming.' } },
  { id: 'hsp-4', dimension: 'aesthetic', text: { 'zh-CN': '艺术或音乐能深深打动我。', 'en-US': 'I am deeply moved by arts or music.' } },
  { id: 'hsp-5', dimension: 'aesthetic', text: { 'zh-CN': '我经常被大自然的美所感动。', 'en-US': 'I am deeply moved by the beauty of nature.' } },
  { id: 'hsp-6', dimension: 'aesthetic', text: { 'zh-CN': '我拥有丰富而复杂的内心世界。', 'en-US': 'I have a rich, complex inner life.' } },
  { id: 'hsp-7', dimension: 'threshold', text: { 'zh-CN': '强烈的灯光、气味、粗糙的面料或警笛声让我不舒服。', 'en-US': 'Bright lights, strong smells, coarse fabrics, or sirens nearby bother me.' } },
  { id: 'hsp-8', dimension: 'threshold', text: { 'zh-CN': '我对咖啡因特别敏感。', 'en-US': 'I am particularly sensitive to the effects of caffeine.' } },
  { id: 'hsp-9', dimension: 'threshold', text: { 'zh-CN': '我对疼痛很敏感。', 'en-US': 'I am sensitive to pain.' } },
  { id: 'hsp-10', dimension: 'processing', text: { 'zh-CN': '别人的情绪会影响到我。', 'en-US': 'Other people\'s moods affect me.' } },
  { id: 'hsp-11', dimension: 'processing', text: { 'zh-CN': '我会注意到环境中的细微变化。', 'en-US': 'I notice subtle changes in my environment.' } },
  { id: 'hsp-12', dimension: 'processing', text: { 'zh-CN': '暴力的电影或电视节目让我非常不适。', 'en-US': 'Violent movies or TV shows disturb me greatly.' } },
];

function scoreHSP(answers: number[]): NeuroScoreResult {
  const total = answers.reduce((s, v) => s + v, 0);
  const avg = total / answers.length;

  const dimGroups: Record<string, number[]> = { excitation: [], aesthetic: [], threshold: [], processing: [] };
  answers.forEach((v, i) => {
    dimGroups[HSP_QUESTIONS[i].dimension].push(v);
  });

  const dimAvg = (arr: number[]) => arr.reduce((s, v) => s + v, 0) / arr.length;
  const level = avg >= 4.5 ? 'high' : avg >= 3 ? 'moderate' : 'low';

  return {
    total: Math.round(avg * 10) / 10,
    maxTotal: 7,
    level,
    levelKey: `neuro.level_${level}`,
    dimensions: [
      { key: 'excitation', nameKey: 'neuro.dim_excitation', score: Math.round(dimAvg(dimGroups.excitation) * 10) / 10, max: 7, color: '#e07a60' },
      { key: 'aesthetic', nameKey: 'neuro.dim_aesthetic', score: Math.round(dimAvg(dimGroups.aesthetic) * 10) / 10, max: 7, color: '#9b7fd4' },
      { key: 'threshold', nameKey: 'neuro.dim_threshold', score: Math.round(dimAvg(dimGroups.threshold) * 10) / 10, max: 7, color: '#d4a843' },
      { key: 'processing', nameKey: 'neuro.dim_processing', score: Math.round(dimAvg(dimGroups.processing) * 10) / 10, max: 7, color: '#6b8fd4' },
    ],
    summaryKey: `neuro.hsp_summary_${level}`,
  };
}

// ─── Scale Catalog ──────────────────────────────────────────

export const NEURO_SCALES: NeuroScale[] = [
  {
    id: 'asrs',
    nameKey: 'neuro.asrs_name',
    descKey: 'neuro.asrs_desc',
    emoji: '⚡',
    color: 'bg-warn-soft',
    itemCount: 6,
    dimensions: [
      { key: 'inattention', nameKey: 'neuro.dim_inattention', color: '#e07a60' },
      { key: 'hyperactivity', nameKey: 'neuro.dim_hyperactivity', color: '#d4a843' },
      { key: 'impulsivity', nameKey: 'neuro.dim_impulsivity', color: '#5cb87e' },
    ],
    questions: ASRS_QUESTIONS,
    answerLabels: {
      'zh-CN': ['从不', '很少', '有时', '经常', '非常频繁'],
      'en-US': ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often'],
    },
    score: scoreASRS,
  },
  {
    id: 'aq10',
    nameKey: 'neuro.aq10_name',
    descKey: 'neuro.aq10_desc',
    emoji: '🧩',
    color: 'bg-calm-soft',
    itemCount: 10,
    dimensions: [
      { key: 'social', nameKey: 'neuro.dim_social', color: '#6b8fd4' },
      { key: 'attention', nameKey: 'neuro.dim_attention_switch', color: '#e07a60' },
      { key: 'communication', nameKey: 'neuro.dim_communication', color: '#5cb87e' },
      { key: 'detail', nameKey: 'neuro.dim_detail', color: '#d4a843' },
      { key: 'systemizing', nameKey: 'neuro.dim_systemizing', color: '#9b7fd4' },
    ],
    questions: AQ10_QUESTIONS,
    answerLabels: {
      'zh-CN': ['非常同意', '略微同意', '略微不同意', '非常不同意'],
      'en-US': ['Definitely Agree', 'Slightly Agree', 'Slightly Disagree', 'Definitely Disagree'],
    },
    score: scoreAQ10,
  },
  {
    id: 'hsp',
    nameKey: 'neuro.hsp_name',
    descKey: 'neuro.hsp_desc',
    emoji: '🌸',
    color: 'bg-accent-soft',
    itemCount: 12,
    dimensions: [
      { key: 'excitation', nameKey: 'neuro.dim_excitation', color: '#e07a60' },
      { key: 'aesthetic', nameKey: 'neuro.dim_aesthetic', color: '#9b7fd4' },
      { key: 'threshold', nameKey: 'neuro.dim_threshold', color: '#d4a843' },
      { key: 'processing', nameKey: 'neuro.dim_processing', color: '#6b8fd4' },
    ],
    questions: HSP_QUESTIONS,
    answerLabels: {
      'zh-CN': ['完全不符', '很少符合', '有点不符', '一般', '有点符合', '比较符合', '非常符合'],
      'en-US': ['Not at All', 'Barely', 'Slightly Not', 'Moderately', 'Slightly', 'Very Much', 'Extremely'],
    },
    score: scoreHSP,
  },
];

export function getNeuroScale(id: string): NeuroScale | undefined {
  return NEURO_SCALES.find((s) => s.id === id);
}
