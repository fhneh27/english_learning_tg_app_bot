import { apiRequest } from "./client";
import {
  EpisodeDetail,
  FranchiseDetail,
  MediaCard,
  MediaEpisodeCard,
  MediaLibrary,
  MediaSeasonCard,
  MediaSearchFilter,
  MediaSearchItem,
  MediaVocabularyScope,
  MovieDetail,
  SeasonDetail,
  SeriesDetail,
  MediaWord,
} from "../types/media";

type MediaSearchResponse = {
  results: MediaSearchItem[];
};

type MediaLibraryResponse = MediaLibrary;
type MediaWordsResponse = { words: MediaWord[] };

export function searchMedia(
  tgUserId: number,
  query: string,
  filterType: MediaSearchFilter
): Promise<MediaSearchResponse> {
  return apiRequest<MediaSearchResponse>("/media/search", {
    method: "POST",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      query,
      filter_type: filterType,
    }),
    errorMessage: "Could not search media.",
  });
}

export function addMediaToLibrary(
  tgUserId: number,
  tmdbId: number,
  mediaType: "movie" | "series"
): Promise<MediaCard> {
  return apiRequest<MediaCard>("/media/library/add", {
    method: "POST",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      tmdb_id: tmdbId,
      media_type: mediaType,
    }),
    errorMessage: "Could not add media to your library.",
  });
}

export function fetchMediaLibrary(_tgUserId: number): Promise<MediaLibraryResponse> {
  return apiRequest<MediaLibraryResponse>("/media/library", {
    method: "GET",
    errorMessage: "Could not load media library.",
  });
}

export function fetchMovieDetail(itemId: string, tgUserId: number): Promise<MovieDetail> {
  return apiRequest<MovieDetail>(`/media/movies/${itemId}`, {
    method: "GET",
    errorMessage: "Could not load movie details.",
  });
}

export function fetchSeriesDetail(itemId: string, tgUserId: number): Promise<SeriesDetail> {
  return apiRequest<SeriesDetail>(`/media/series/${itemId}`, {
    method: "GET",
    errorMessage: "Could not load series details.",
  });
}

export function fetchSeasonDetail(seasonId: string, tgUserId: number): Promise<SeasonDetail> {
  return apiRequest<SeasonDetail>(`/media/seasons/${seasonId}`, {
    method: "GET",
    errorMessage: "Could not load season details.",
  });
}

export function fetchEpisodeDetail(episodeId: string, tgUserId: number): Promise<EpisodeDetail> {
  return apiRequest<EpisodeDetail>(`/media/episodes/${episodeId}`, {
    method: "GET",
    errorMessage: "Could not load episode details.",
  });
}

export function fetchFranchiseDetail(itemId: string, tgUserId: number): Promise<FranchiseDetail> {
  return apiRequest<FranchiseDetail>(`/media/franchises/${itemId}`, {
    method: "GET",
    errorMessage: "Could not load franchise details.",
  });
}

export function updateMovieProgress(
  itemId: string,
  tgUserId: number,
  watchedMinutes: number | null,
  markWatched = false
): Promise<MediaCard> {
  return apiRequest<MediaCard>(`/media/movies/${itemId}/progress`, {
    method: "PATCH",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      watched_minutes: watchedMinutes,
      mark_watched: markWatched,
    }),
    errorMessage: "Could not update movie progress.",
  });
}

export function updateEpisodeProgress(
  episodeId: string,
  tgUserId: number,
  watchedMinutes: number | null,
  markWatched = false
): Promise<MediaEpisodeCard> {
  return apiRequest<MediaEpisodeCard>(`/media/episodes/${episodeId}/progress`, {
    method: "PATCH",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      watched_minutes: watchedMinutes,
      mark_watched: markWatched,
    }),
    errorMessage: "Could not update episode progress.",
  });
}

export function updateSeasonProgress(
  seasonId: string,
  tgUserId: number,
  markWatched = true
): Promise<MediaSeasonCard> {
  return apiRequest<MediaSeasonCard>(`/media/seasons/${seasonId}/progress`, {
    method: "PATCH",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      mark_watched: markWatched,
    }),
    errorMessage: "Could not update season progress.",
  });
}

export function updateSeriesProgress(
  itemId: string,
  tgUserId: number,
  markWatched = true
): Promise<MediaCard> {
  return apiRequest<MediaCard>(`/media/series/${itemId}/progress`, {
    method: "PATCH",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      mark_watched: markWatched,
    }),
    errorMessage: "Could not update series progress.",
  });
}

export function fetchMediaVocabulary(
  tgUserId: number,
  scope: MediaVocabularyScope
): Promise<MediaWordsResponse> {
  return apiRequest<MediaWordsResponse>(`/media/vocabulary?scope=${scope}`, {
    method: "GET",
    errorMessage: "Could not load media vocabulary.",
  });
}
