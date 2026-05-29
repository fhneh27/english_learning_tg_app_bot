export type VocabularyStatus = "new" | "learning" | "learned";
export type VocabularySourceType = "unsorted" | "media" | "music";
export type VocabularyAnalysisMode = "general" | "slang" | "conversation";

export type ExampleItem = {
  en: string;
  ru: string;
};

export type VocabularyAnalysis = {
  original_text: string;
  normalized_text: string;
  translation_ru: string;
  meaning_ru: string;
  part_of_speech: string | null;
  level: string | null;
  transcription: string | null;
  examples: ExampleItem[];
  synonyms: string[];
  tags: string[];
};

export type VocabularyEntry = VocabularyAnalysis & {
  id: string;
  tg_user_id: number;
  status: VocabularyStatus;
  source_type: VocabularySourceType;
  analysis_mode: VocabularyAnalysisMode;
  media_item_id: string | null;
  media_season_id: string | null;
  media_episode_id: string | null;
  media_franchise_id: string | null;
  music_track_id: string | null;
  source_label: string | null;
  source_image_url: string | null;
  repeat_count: number;
  learned_at: string | null;
  ai_model: string | null;
  created_at: string;
  updated_at: string;
};

export type VocabularyAnalyzePayload = {
  tg_user_id: number;
  text: string;
  analysis_mode?: VocabularyAnalysisMode;
};

export type VocabularyCreatePayload = VocabularyAnalyzePayload & {
  source_type?: VocabularySourceType;
  media_item_id?: string;
  media_season_id?: string;
  media_episode_id?: string;
  media_franchise_id?: string;
  music_track_external_id?: string;
  music_release_external_id?: string;
  music_track_title?: string;
  music_artist_name?: string;
  music_release_title?: string;
  music_release_year?: number;
  music_artwork_url?: string;
  music_duration_ms?: number;
  source_label?: string;
};

export type VocabularySavePayload = {
  tg_user_id: number;
  analysis: VocabularyAnalysis;
  source_type?: VocabularySourceType;
  analysis_mode?: VocabularyAnalysisMode;
  media_item_id?: string;
  media_season_id?: string;
  media_episode_id?: string;
  media_franchise_id?: string;
  music_track_external_id?: string;
  music_release_external_id?: string;
  music_track_title?: string;
  music_artist_name?: string;
  music_release_title?: string;
  music_release_year?: number;
  music_artwork_url?: string;
  music_duration_ms?: number;
  source_label?: string;
};

export type VocabularyProgressPayload = {
  status?: VocabularyStatus;
  increment_repetition?: boolean;
};

export type VocabularyAnalysisResponse = {
  analysis: VocabularyAnalysis;
  ai_model: string | null;
  analysis_mode: VocabularyAnalysisMode;
};

export type VocabularyFollowUpPayload = {
  prompt: string;
};

export type VocabularyFollowUpResponse = {
  answer_ru: string;
  usage_notes_ru: string[];
  mistakes_ru: string[];
  extra_examples: ExampleItem[];
  follow_up_model: string | null;
};

export type RegisterUserPayload = {
  tg_user_id: number;
  username?: string;
  first_name?: string;
};
