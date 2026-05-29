export type StreakDay = {
  date: string;
  is_active: boolean;
  action_count: number;
};

export type StreakSummary = {
  current_streak_days: number;
  best_streak_days: number;
  elite_current_streak_days: number;
  elite_best_streak_days: number;
  elite_today_complete: boolean;
  active_days_total: number;
  today_actions: number;
  last_activity_date: string | null;
  last_14_days: StreakDay[];
  last_30_days_active: number;
  next_milestone_days: number;
  total_words: number;
  learned_words: number;
  watched_minutes: number;
  watched_movies: number;
  watched_episodes: number;
  media_vocabulary_count: number;
  daily_add_goal: number;
  daily_learn_goal: number;
  words_added_today: number;
  words_learned_today: number;
  remaining_add_goal: number;
  remaining_learn_goal: number;
};

export type DailyVocabularySuggestionItem = {
  text: string;
  kind: string;
  level: string;
  category: string;
  reason_ru: string;
  usage_hint_ru: string;
};

export type DailyVocabularySuggestion = {
  summary_ru: string;
  target_new_words: number;
  words_added_today: number;
  remaining_new_words: number;
  learned_today: number;
  remaining_learned_words: number;
  suggestions: DailyVocabularySuggestionItem[];
  ai_model: string | null;
};

export type SuggestionBlacklistResponse = {
  text: string;
  blacklist_size: number;
};
