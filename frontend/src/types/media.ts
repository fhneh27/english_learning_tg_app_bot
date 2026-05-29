export type MediaType = "movie" | "series" | "franchise";
export type MediaSearchFilter = "all" | "movie" | "series";
export type MediaVocabularyScope = "movie" | "series" | "franchise";

export type MediaSearchItem = {
  tmdb_id: number;
  media_type: "movie" | "series";
  title: string;
  year: number | null;
  poster_path: string | null;
  overview: string | null;
  is_in_library: boolean;
};

export type MediaCard = {
  id: string;
  tmdb_id: number | null;
  media_type: MediaType;
  title: string;
  year: number | null;
  poster_path: string | null;
  overview: string | null;
  runtime_minutes: number;
  watched_minutes: number;
  watched_percent: number;
  is_watched: boolean;
};

export type MediaLibrary = {
  movies: MediaCard[];
  series: MediaCard[];
  franchises: MediaCard[];
};

export type MediaSeasonCard = {
  id: string;
  season_number: number;
  title: string;
  overview: string | null;
  episode_count: number;
  watched_episodes: number;
  watched_percent: number;
};

export type MediaEpisodeCard = {
  id: string;
  season_number: number;
  episode_number: number;
  title: string;
  overview: string | null;
  runtime_minutes: number;
  watched_minutes: number;
  watched_percent: number;
  is_watched: boolean;
};

export type MediaWord = {
  id: string;
  original_text: string;
  translation_ru: string;
  meaning_ru: string;
  status: string;
  source_label: string | null;
  media_kind: string | null;
};

export type MovieDetail = {
  item: MediaCard;
  watched_label: string;
  words: MediaWord[];
};

export type SeriesDetail = {
  item: MediaCard;
  seasons: MediaSeasonCard[];
  total_episodes: number;
  watched_episodes: number;
  words: MediaWord[];
};

export type SeasonDetail = {
  series_item_id: string;
  season: MediaSeasonCard;
  episodes: MediaEpisodeCard[];
  words: MediaWord[];
};

export type EpisodeDetail = {
  series_item_id: string;
  season_id: string;
  episode: MediaEpisodeCard;
  watched_label: string;
  words: MediaWord[];
};

export type FranchiseDetail = {
  item: MediaCard;
  movies: MediaCard[];
  total_runtime_minutes: number;
  watched_minutes: number;
  watched_percent: number;
  words: MediaWord[];
};

