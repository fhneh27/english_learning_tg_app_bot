export type MusicTrackSearchItem = {
  provider: string;
  external_id: string;
  release_external_id: string | null;
  title: string;
  artist_name: string;
  release_title: string | null;
  release_year: number | null;
  artwork_url: string | null;
  duration_ms: number | null;
};

export type MusicSearchResponse = {
  results: MusicTrackSearchItem[];
};
