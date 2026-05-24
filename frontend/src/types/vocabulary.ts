export type VocabularyStatus = "new" | "learning" | "learned";

export type ExampleItem = {
  en: string;
  ru: string;
};

export type VocabularyEntry = {
  id: string;
  tg_user_id: number;
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
  status: VocabularyStatus;
  repeat_count: number;
  learned_at: string | null;
  ai_model: string | null;
  created_at: string;
  updated_at: string;
};

export type VocabularyCreatePayload = {
  tg_user_id: number;
  text: string;
};

export type VocabularyProgressPayload = {
  status?: VocabularyStatus;
  increment_repetition?: boolean;
};

export type RegisterUserPayload = {
  tg_user_id: number;
  username?: string;
  first_name?: string;
};
