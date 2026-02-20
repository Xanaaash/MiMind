export interface User {
  user_id: string;
  email: string;
  locale: string;
  created_at: string;
}

export type TriageChannel = 'GREEN' | 'YELLOW' | 'RED';

export interface AuthSessionPayload {
  authenticated: boolean;
  user_id?: string;
  email?: string;
  channel?: TriageChannel;
  expires_at?: string;
  user?: {
    user_id: string;
    email: string;
    locale: string;
  };
}

export interface TriageDecision {
  channel: TriageChannel;
  reasons: string[];
  halt_coaching: boolean;
  show_hotline: boolean;
  dialogue_risk_level: string | null;
}

export interface AssessmentScoreSet {
  phq9_score: number;
  gad7_score: number;
  pss10_score: number;
  cssrs_positive: boolean;
  scl90_global_index: number | null;
  scl90_dimension_scores: Record<string, number> | null;
  scl90_moderate_or_above: boolean;
}

export interface ScaleCatalogItem {
  display_name: string;
  item_count: number;
  question_bank: {
    questions: ScaleQuestion[];
    answer_labels?: Record<string, string[]>;
  };
}

export interface ScaleQuestion {
  question_id: string;
  text: Record<string, string>;
  dimension_key?: string;
}

export interface ScaleScoreResult {
  scale_id: string;
  score: number;
  severity?: string;
  interpretation?: Record<string, string>;
}

export interface TestCatalogItem {
  display_name: string;
  input_dimension_count: number;
  required_answer_keys: string[];
  answer_range: string;
  question_bank: {
    questions: TestQuestion[];
  };
}

export interface TestQuestion {
  question_id: string;
  text: Record<string, string>;
  dimension_key: string;
}

export interface TestResult {
  result_id: string;
  user_id: string;
  test_id: string;
  summary: Record<string, unknown>;
  created_at: string;
}

export interface CoachSession {
  session_id: string;
  user_id: string;
  style_id: string;
  started_at: string;
  active: boolean;
}

export interface CoachChatResponse {
  coach_message: string;
  mode: string;
  halted: boolean;
  safety?: {
    detection?: { level: string; reasons: string[] };
    action?: { message: string };
    hotline?: { text: string };
  };
}

export interface CoachStyle {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface AudioTrack {
  trackId: string;
  name: string;
  category: string;
  duration_seconds: number;
}

export interface MeditationItem {
  meditationId: string;
  name: string;
  category: string;
  duration_seconds: number;
}

export interface JournalEntry {
  entry_id: string;
  user_id: string;
  mood: string;
  energy: number;
  note: string;
  created_at: string;
}

export interface JournalTrend {
  entries: JournalEntry[];
  average_energy: number;
  mood_distribution: Record<string, number>;
}

export interface BillingPlan {
  plan_id: string;
  display_name: string;
  reports_enabled: boolean;
  tools_enabled: boolean;
  ai_sessions_per_month: number;
  trial_days: number;
}

export interface SubscriptionRecord {
  user_id: string;
  plan_id: string;
  status: string;
  started_at: string;
  ends_at: string;
  trial: boolean;
  ai_quota_monthly: number;
  ai_used_in_cycle: number;
}

export interface Hotline {
  label: string;
  number: string;
  region: string;
}
