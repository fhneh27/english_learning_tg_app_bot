import { ChangeEvent, startTransition, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";

import { useTheme } from "./contexts/ThemeContext";
import {
  addMediaToLibrary,
  fetchEpisodeDetail,
  fetchFranchiseDetail,
  fetchMediaLibrary,
  fetchMediaVocabulary,
  fetchMovieDetail,
  fetchSeasonDetail,
  fetchSeriesDetail,
  searchMedia,
  updateEpisodeProgress,
  updateMovieProgress,
  updateSeasonProgress,
  updateSeriesProgress,
} from "./api/media";
import { searchMusicTracks } from "./api/music";
import { setApiAuthContext } from "./api/auth";
import { APP_DISPLAY_VERSION } from "./appVersion";
import {
  blacklistVocabularySuggestion,
  fetchAIInstructions,
  fetchDailyVocabularySuggestions,
  fetchUserStreak,
  registerUser,
  updateAIInstructions,
} from "./api/users";
import {
  analyzeVocabularyEntry,
  createVocabularyEntry,
  deleteVocabularyEntry,
  fetchVocabularyEntries,
  saveAnalyzedVocabularyEntry,
  updateVocabularyProgress,
} from "./api/vocabulary";
import AppLayout from "./components/AppLayout";
import { AppTab } from "./components/BottomNav";
import Button from "./components/Button";
import Card from "./components/Card";
import EmptyState from "./components/EmptyState";
import EntryDetailsModal from "./components/EntryDetailsModal";
import Input from "./components/Input";
import LoadingState from "./components/LoadingState";
import ResultCard from "./components/ResultCard";
import SourcePickerModal from "./components/SourcePickerModal";
import WordCard from "./components/WordCard";
import StreakPage from "./pages/StreakPage";
import WordsTab from "./pages/WordsTab";
import {
  EpisodeDetail,
  FranchiseDetail,
  MediaCard,
  MediaLibrary,
  MediaSearchFilter,
  MediaSearchItem,
  MediaVocabularyScope,
  MovieDetail,
  SeasonDetail,
  SeriesDetail,
} from "./types/media";
import { MusicTrackSearchItem } from "./types/music";
import {
  DailyVocabularySuggestion,
  DailyVocabularySuggestionItem,
  StreakSummary,
} from "./types/user";
import {
  VocabularyAnalysisResponse,
  VocabularyAnalysisMode,
  VocabularyEntry,
  VocabularySourceType,
} from "./types/vocabulary";
import {
  formatAnalysisModeLabel,
  formatSourceLabel,
} from "./utils/vocabulary";
import { listContainer, listItem } from "./lib/motion";
import { getNavStreakDisplay } from "./utils/streak";

const DEFAULT_DEV_TG_USER_ID = 123456789;
const STORAGE_TG_USER_KEY = "telegram_mini_app_tg_user";
const TMDB_IMAGE_BASE_URL = import.meta.env.VITE_TMDB_IMAGE_BASE_URL || "https://image.tmdb.org/t/p/w500";

const DESTINATION_OPTIONS = [
  {
    value: "unsorted" as const,
    description: "General vocabulary with no source attached yet.",
  },
  {
    value: "media" as const,
    description: "Attach this word to movie or series progress.",
  },
  {
    value: "music" as const,
    description: "Attach this word to a song and keep the source cover.",
  },
];

const ANALYSIS_MODE_OPTIONS: Array<{
  description: string;
  value: VocabularyAnalysisMode;
}> = [
  {
    value: "general",
    description: "Clear default explanation for normal learning.",
  },
  {
    value: "slang",
    description: "Focus on slang meaning, tone, and street-level nuance.",
  },
  {
    value: "conversation",
    description: "Prioritize natural spoken English and real dialogue usage.",
  },
];

const MEDIA_SEARCH_FILTERS: Array<{ label: string; value: MediaSearchFilter }> = [
  { label: "All", value: "all" },
  { label: "Movies", value: "movie" },
  { label: "Series", value: "series" },
];

const MEDIA_WORD_SCOPE_OPTIONS: Array<{ label: string; value: MediaVocabularyScope }> = [
  { label: "Movie words", value: "movie" },
  { label: "Series words", value: "series" },
  { label: "Franchise words", value: "franchise" },
];

type HomeMediaContext = {
  media_item_id?: string;
  media_season_id?: string;
  media_episode_id?: string;
  media_franchise_id?: string;
  source_label: string;
};

type MediaView =
  | { screen: "library" }
  | { screen: "movie"; id: string }
  | { screen: "series"; id: string }
  | { screen: "season"; id: string }
  | { screen: "episode"; id: string }
  | { screen: "franchise"; id: string };

function App() {
  const { theme, setTheme } = useTheme();
  const [entries, setEntries] = useState<VocabularyEntry[]>([]);
  const [activeTab, setActiveTab] = useState<AppTab>("home");
  const [streakSummary, setStreakSummary] = useState<StreakSummary | null>(null);
  const [dailySuggestion, setDailySuggestion] = useState<DailyVocabularySuggestion | null>(null);
  const [isDailySuggestionLoading, setIsDailySuggestionLoading] = useState(false);
  const [dailySuggestionError, setDailySuggestionError] = useState<string | null>(null);
  const [savingSuggestionText, setSavingSuggestionText] = useState<string | null>(null);
  const [blacklistingSuggestionText, setBlacklistingSuggestionText] = useState<string | null>(null);
  const [savedSuggestionTexts, setSavedSuggestionTexts] = useState<string[]>([]);
  const [blacklistedSuggestionTexts, setBlacklistedSuggestionTexts] = useState<string[]>([]);
  const homeInputRef = useRef<HTMLTextAreaElement>(null);
  const [analysisResponse, setAnalysisResponse] = useState<VocabularyAnalysisResponse | null>(null);
  const [analysisMode, setAnalysisMode] = useState<VocabularyAnalysisMode>("general");
  const [selectedSourceType, setSelectedSourceType] = useState<VocabularySourceType>("unsorted");
  const [homeMediaContext, setHomeMediaContext] = useState<HomeMediaContext | null>(null);
  const [musicQuery, setMusicQuery] = useState("");
  const [musicResults, setMusicResults] = useState<MusicTrackSearchItem[]>([]);
  const [selectedMusicTrack, setSelectedMusicTrack] = useState<MusicTrackSearchItem | null>(null);
  const [isMusicSearching, setIsMusicSearching] = useState(false);
  const [musicError, setMusicError] = useState<string | null>(null);
  const [sourcePickerMode, setSourcePickerMode] = useState<"media" | "music" | null>(null);
  const [sourcePickerMediaQuery, setSourcePickerMediaQuery] = useState("");
  const [sourcePickerMediaFilter, setSourcePickerMediaFilter] = useState<MediaSearchFilter>("all");
  const [sourcePickerMediaResults, setSourcePickerMediaResults] = useState<MediaSearchItem[]>([]);
  const [sourcePickerSelectedMedia, setSourcePickerSelectedMedia] = useState<MediaCard | null>(null);
  const [sourcePickerSelectedMusicTrack, setSourcePickerSelectedMusicTrack] = useState<MusicTrackSearchItem | null>(
    null
  );
  const [isSourcePickerMediaSearching, setIsSourcePickerMediaSearching] = useState(false);
  const [isSourcePickerApplying, setIsSourcePickerApplying] = useState(false);
  const [sourcePickerMediaError, setSourcePickerMediaError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isStreakLoading, setIsStreakLoading] = useState(true);
  const [screenError, setScreenError] = useState<string | null>(null);
  const [homeError, setHomeError] = useState<string | null>(null);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);

  const [mediaQuery, setMediaQuery] = useState("");
  const [mediaFilter, setMediaFilter] = useState<MediaSearchFilter>("all");
  const [mediaResults, setMediaResults] = useState<MediaSearchItem[]>([]);
  const [mediaResultsVisible, setMediaResultsVisible] = useState(false);
  const [mediaLibrary, setMediaLibrary] = useState<MediaLibrary | null>(null);
  const [mediaWordsScope, setMediaWordsScope] = useState<MediaVocabularyScope>("movie");
  const [mediaScopeWords, setMediaScopeWords] = useState<VocabularyEntry[]>([]);
  const [mediaView, setMediaView] = useState<MediaView>({ screen: "library" });
  const [movieDetail, setMovieDetail] = useState<MovieDetail | null>(null);
  const [seriesDetail, setSeriesDetail] = useState<SeriesDetail | null>(null);
  const [seasonDetail, setSeasonDetail] = useState<SeasonDetail | null>(null);
  const [episodeDetail, setEpisodeDetail] = useState<EpisodeDetail | null>(null);
  const [franchiseDetail, setFranchiseDetail] = useState<FranchiseDetail | null>(null);
  const [isMediaSearching, setIsMediaSearching] = useState(false);
  const [isMediaLoading, setIsMediaLoading] = useState(true);
  const [isMediaDetailLoading, setIsMediaDetailLoading] = useState(false);
  const [isMediaProgressSaving, setIsMediaProgressSaving] = useState(false);
  const [isMediaWordsLoading, setIsMediaWordsLoading] = useState(false);
  const [mediaError, setMediaError] = useState<string | null>(null);
  const [musicTabQuery, setMusicTabQuery] = useState("");
  const [musicTabResults, setMusicTabResults] = useState<MusicTrackSearchItem[]>([]);
  const [isMusicTabSearching, setIsMusicTabSearching] = useState(false);
  const [musicTabError, setMusicTabError] = useState<string | null>(null);
  
  const [aiInstructions, setAiInstructions] = useState<string>("");
  const [isAiInstructionsLoading, setIsAiInstructionsLoading] = useState(false);
  const [isAiInstructionsSaving, setIsAiInstructionsSaving] = useState(false);
  const [aiInstructionsError, setAiInstructionsError] = useState<string | null>(null);
  const [aiInstructionsSaved, setAiInstructionsSaved] = useState(false);

  const [tgUser, setTgUser] = useState(() => getTelegramUser());
  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.id === selectedEntryId) ?? null,
    [entries, selectedEntryId]
  );
  const recentEntries = useMemo(() => entries.slice(0, 5), [entries]);
  const recentMusicEntries = useMemo(
    () => entries.filter((entry) => entry.source_type === "music").slice(0, 8),
    [entries]
  );
  const sourcePickerMediaLibraryItems = useMemo(
    () => [...(mediaLibrary?.movies ?? []), ...(mediaLibrary?.series ?? [])],
    [mediaLibrary]
  );
  const activeSourceLabel =
    homeMediaContext?.source_label ??
    (selectedMusicTrack ? `${selectedMusicTrack.artist_name} - ${selectedMusicTrack.title}` : null);
  const tgUserId = tgUser.id;

  useEffect(() => {
    setApiAuthContext(tgUserId);
  }, [tgUserId]);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }

    const syncTelegramUser = () => {
      const nextUser = getTelegramUser();
      setTgUser((currentUser) => {
        if (
          currentUser.id === nextUser.id &&
          currentUser.username === nextUser.username &&
          currentUser.firstName === nextUser.firstName
        ) {
          return currentUser;
        }
        return nextUser;
      });
    };

    syncTelegramUser();
    const delayedSync = window.setTimeout(syncTelegramUser, 300);
    return () => window.clearTimeout(delayedSync);
  }, []);

  useEffect(() => {
    void registerUser({
      tg_user_id: tgUser.id,
      username: tgUser.username,
      first_name: tgUser.firstName,
    }).catch(() => {
      // Registration is best-effort and must not block the UI.
    });
  }, [tgUser.firstName, tgUser.id, tgUser.username]);

  useEffect(() => {
    void loadEntries();
    void loadStreak();
    void loadMediaLibrary();
    void loadMediaVocabulary(mediaWordsScope);
    void loadAiInstructions();
    setDailySuggestion(null);
    setDailySuggestionError(null);
    setSavedSuggestionTexts([]);
    setBlacklistedSuggestionTexts([]);
    setMusicQuery("");
    setMusicResults([]);
    setSelectedMusicTrack(null);
    setMusicError(null);
    setSourcePickerMode(null);
    setSourcePickerMediaQuery("");
    setSourcePickerMediaResults([]);
    setSourcePickerSelectedMedia(null);
    setSourcePickerSelectedMusicTrack(null);
    setSourcePickerMediaError(null);
    setMusicTabQuery("");
    setMusicTabResults([]);
    setMusicTabError(null);
  }, [tgUserId]);

  async function loadEntries() {
    setIsLoading(true);
    setScreenError(null);

    try {
      const data = await fetchVocabularyEntries({ tgUserId });
      setEntries(data);
    } catch (requestError) {
      setScreenError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadStreak() {
    setIsStreakLoading(true);

    try {
      const data = await fetchUserStreak(tgUserId);
      setStreakSummary(data);
    } catch (requestError) {
      setScreenError(getErrorMessage(requestError));
    } finally {
      setIsStreakLoading(false);
    }
  }
  
  async function loadAiInstructions() {
    setIsAiInstructionsLoading(true);
    setAiInstructionsError(null);

    try {
      const data = await fetchAIInstructions(tgUserId);
      setAiInstructions(data.ai_custom_instructions || "");
    } catch (requestError) {
      setAiInstructionsError(getErrorMessage(requestError));
    } finally {
      setIsAiInstructionsLoading(false);
    }
  }

  async function handleSaveAiInstructions() {
    setIsAiInstructionsSaving(true);
    setAiInstructionsError(null);
    setAiInstructionsSaved(false);

    try {
      const trimmed = aiInstructions.trim();
      await updateAIInstructions(tgUserId, trimmed || null);
      setAiInstructionsSaved(true);
      setTimeout(() => setAiInstructionsSaved(false), 3000);
    } catch (requestError) {
      setAiInstructionsError(getErrorMessage(requestError));
    } finally {
      setIsAiInstructionsSaving(false);
    }
  }

  async function handleFetchDailySuggestions() {
    setIsDailySuggestionLoading(true);
    setDailySuggestionError(null);
    setSavedSuggestionTexts([]);
    setBlacklistedSuggestionTexts([]);

    try {
      const data = await fetchDailyVocabularySuggestions(tgUserId);
      setDailySuggestion(data);
      await loadStreak();
    } catch (requestError) {
      setDailySuggestionError(getErrorMessage(requestError));
    } finally {
      setIsDailySuggestionLoading(false);
    }
  }

  async function handleSaveSuggestedWord(item: DailyVocabularySuggestionItem) {
    if (savingSuggestionText === item.text || savedSuggestionTexts.includes(item.text)) {
      return;
    }

    setSavingSuggestionText(item.text);
    setDailySuggestionError(null);

    try {
      const normalizedCategory = item.category.toLowerCase();
      const analysisMode: VocabularyAnalysisMode = normalizedCategory.includes("slang")
        ? "slang"
        : normalizedCategory.includes("conversation")
          ? "conversation"
          : "general";

      const savedEntry = await createVocabularyEntry({
        tg_user_id: tgUserId,
        text: item.text,
        source_type: "unsorted",
        analysis_mode: analysisMode,
      });

      setEntries((currentEntries) => [savedEntry, ...currentEntries]);
      setSavedSuggestionTexts((current) => [...current, item.text]);
      await loadStreak();
    } catch (requestError) {
      setDailySuggestionError(getErrorMessage(requestError));
    } finally {
      setSavingSuggestionText(null);
    }
  }

  async function handleBlacklistSuggestedWord(item: DailyVocabularySuggestionItem) {
    if (blacklistingSuggestionText === item.text || blacklistedSuggestionTexts.includes(item.text)) {
      return;
    }

    setBlacklistingSuggestionText(item.text);
    setDailySuggestionError(null);

    try {
      await blacklistVocabularySuggestion(tgUserId, item.text);
      setBlacklistedSuggestionTexts((current) => [...current, item.text]);
      setDailySuggestion((current) =>
        current
          ? {
              ...current,
              suggestions: current.suggestions.filter((suggestionItem) => suggestionItem.text !== item.text),
            }
          : current
      );
    } catch (requestError) {
      setDailySuggestionError(getErrorMessage(requestError));
    } finally {
      setBlacklistingSuggestionText(null);
    }
  }

  async function loadMediaLibrary() {
    setIsMediaLoading(true);
    setMediaError(null);

    try {
      const data = await fetchMediaLibrary(tgUserId);
      setMediaLibrary(data);
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaLoading(false);
    }
  }

  async function loadMediaVocabulary(scope: MediaVocabularyScope) {
    setIsMediaWordsLoading(true);
    setMediaError(null);

    try {
      const data = await fetchMediaVocabulary(tgUserId, scope);
      const mappedWords: VocabularyEntry[] = data.words.map((word) => {
        const existing = entries.find((entry) => entry.id === word.id);
        if (existing) {
          return existing;
        }

        return {
          id: word.id,
          tg_user_id: tgUserId,
          original_text: word.original_text,
          normalized_text: word.original_text.toLowerCase(),
          translation_ru: word.translation_ru,
          meaning_ru: word.meaning_ru,
          part_of_speech: null,
          level: null,
          transcription: null,
          examples: [],
          synonyms: [],
          tags: [],
          status: normalizeVocabularyStatus(word.status),
          source_type: "media" as VocabularySourceType,
          analysis_mode: "general" as VocabularyAnalysisMode,
          media_item_id: null,
          media_season_id: null,
          media_episode_id: null,
          media_franchise_id: null,
          music_track_id: null,
          source_label: word.source_label,
          source_image_url: null,
          repeat_count: 0,
          learned_at: null,
          ai_model: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      });
      setMediaScopeWords(mappedWords);
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaWordsLoading(false);
    }
  }

  async function handleAnalyzeEntry() {
    const trimmedText = homeInputRef.current?.value.trim() ?? "";
    if (!trimmedText) {
      setHomeError("Enter an English word or phrase first.");
      return;
    }

    setIsAnalyzing(true);
    setHomeError(null);

    try {
      const result = await analyzeVocabularyEntry({
        tg_user_id: tgUserId,
        text: trimmedText,
        analysis_mode: analysisMode,
      });
      setAnalysisResponse(result);
      if (selectedSourceType === "media" && !homeMediaContext) {
        setSelectedSourceType("unsorted");
      }
    } catch (requestError) {
      setHomeError(getErrorMessage(requestError));
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleSaveAnalyzedEntry() {
    if (!analysisResponse) {
      return;
    }

    const isMediaTarget = selectedSourceType === "media";
    const isMusicTarget = selectedSourceType === "music";

    if (isMediaTarget && !homeMediaContext) {
      setHomeError("Choose a movie or series first so this word can be saved under Media.");
      openSourcePicker("media");
      return;
    }

    if (isMusicTarget && !selectedMusicTrack) {
      setHomeError("Choose a song first so this word can be saved under Music.");
      openSourcePicker("music");
      return;
    }

    setIsSaving(true);
    setHomeError(null);

    try {
      const savedEntry = await saveAnalyzedVocabularyEntry({
        tg_user_id: tgUserId,
        analysis: analysisResponse.analysis,
        source_type: selectedSourceType,
        analysis_mode: analysisResponse.analysis_mode,
        media_item_id: isMediaTarget ? homeMediaContext?.media_item_id : undefined,
        media_season_id: isMediaTarget ? homeMediaContext?.media_season_id : undefined,
        media_episode_id: isMediaTarget ? homeMediaContext?.media_episode_id : undefined,
        media_franchise_id: isMediaTarget ? homeMediaContext?.media_franchise_id : undefined,
        music_track_external_id: isMusicTarget ? selectedMusicTrack?.external_id : undefined,
        music_release_external_id: isMusicTarget ? selectedMusicTrack?.release_external_id ?? undefined : undefined,
        music_track_title: isMusicTarget ? selectedMusicTrack?.title : undefined,
        music_artist_name: isMusicTarget ? selectedMusicTrack?.artist_name : undefined,
        music_release_title: isMusicTarget ? selectedMusicTrack?.release_title ?? undefined : undefined,
        music_release_year: isMusicTarget ? selectedMusicTrack?.release_year ?? undefined : undefined,
        music_artwork_url: isMusicTarget ? selectedMusicTrack?.artwork_url ?? undefined : undefined,
        music_duration_ms: isMusicTarget ? selectedMusicTrack?.duration_ms ?? undefined : undefined,
        source_label: isMediaTarget
          ? homeMediaContext?.source_label
          : isMusicTarget
            ? `${selectedMusicTrack?.artist_name} - ${selectedMusicTrack?.title}`
            : undefined,
      });
      setEntries((currentEntries) => [savedEntry, ...currentEntries]);
      await loadStreak();
      if (isMediaTarget) {
        await loadMediaVocabulary(mediaWordsScope);
      }
      setAnalysisResponse(null);
      if (homeInputRef.current) {
        homeInputRef.current.value = "";
      }
      if (!isMusicTarget) {
        setMusicQuery("");
        setMusicResults([]);
        setSelectedMusicTrack(null);
        setMusicError(null);
      }
      setSelectedSourceType(isMediaTarget ? "media" : isMusicTarget ? "music" : "unsorted");
    } catch (requestError) {
      setHomeError(getErrorMessage(requestError));
    } finally {
      setIsSaving(false);
    }
  }

  function handleDismissAnalyzedEntry() {
    setAnalysisResponse(null);
    setHomeError(null);
    setSelectedSourceType(homeMediaContext ? "media" : selectedMusicTrack ? "music" : "unsorted");
  }

  async function handleIncreaseRepeat(entryId: string) {
    setScreenError(null);

    try {
      const updatedEntry = await updateVocabularyProgress(entryId, tgUserId, {
        increment_repetition: true,
      });
      setEntries((currentEntries) =>
        currentEntries.map((entry) => (entry.id === entryId ? updatedEntry : entry))
      );
      await loadStreak();
    } catch (requestError) {
      setScreenError(getErrorMessage(requestError));
    }
  }

  async function handleMarkLearned(entryId: string) {
    setScreenError(null);

    try {
      const updatedEntry = await updateVocabularyProgress(entryId, tgUserId, {
        status: "learned",
      });
      setEntries((currentEntries) =>
        currentEntries.map((entry) => (entry.id === entryId ? updatedEntry : entry))
      );
      await loadStreak();
    } catch (requestError) {
      setScreenError(getErrorMessage(requestError));
    }
  }

  async function handleDeleteEntry(entryId: string) {
    setScreenError(null);

    try {
      await deleteVocabularyEntry(entryId, tgUserId);
      setEntries((currentEntries) => currentEntries.filter((entry) => entry.id !== entryId));
      setSelectedEntryId((currentId) => (currentId === entryId ? null : currentId));
      await loadStreak();
    } catch (requestError) {
      setScreenError(getErrorMessage(requestError));
    }
  }

  async function handleMusicSearch() {
    const trimmedQuery = musicQuery.trim();
    if (!trimmedQuery) {
      setMusicError("Type the song title or artist first.");
      return;
    }

    setIsMusicSearching(true);
    setMusicError(null);
    try {
      const result = await searchMusicTracks(tgUserId, trimmedQuery, 8);
      setMusicResults(result.results);
      if (result.results.length === 0) {
        setMusicError("Nothing matched yet. Try a more specific title or add the artist name.");
      }
    } catch (requestError) {
      setMusicError(getErrorMessage(requestError));
    } finally {
      setIsMusicSearching(false);
    }
  }

  function handleSelectMusicTrack(track: MusicTrackSearchItem) {
    setSourcePickerSelectedMusicTrack(track);
    setMusicError(null);
  }

  function openSourcePicker(mode: "media" | "music") {
    setSourcePickerMode(mode);
    setHomeError(null);

    if (mode === "media") {
      const selectedMedia =
        homeMediaContext?.media_item_id
          ? sourcePickerMediaLibraryItems.find((item) => item.id === homeMediaContext.media_item_id) ?? null
          : null;
      setSourcePickerSelectedMedia(selectedMedia);
      setSourcePickerMediaError(null);
      return;
    }

    setSourcePickerSelectedMusicTrack(selectedMusicTrack);
    setMusicError(null);
  }

  function clearHomeSource() {
    setSelectedSourceType("unsorted");
    setHomeMediaContext(null);
    setSelectedMusicTrack(null);
    setSourcePickerSelectedMedia(null);
    setSourcePickerSelectedMusicTrack(null);
    setMusicQuery("");
    setMusicResults([]);
    setMusicError(null);
    setSourcePickerMediaError(null);
  }

  function closeSourcePicker() {
    setSourcePickerMode(null);
    setSourcePickerMediaError(null);
    setMusicError(null);
  }

  async function handleMediaSearch() {
    const trimmedQuery = mediaQuery.trim();
    if (!trimmedQuery) {
      setMediaError("Type movie or series title first.");
      return;
    }

    setIsMediaSearching(true);
    setMediaError(null);
    try {
      const result = await searchMedia(tgUserId, trimmedQuery, mediaFilter);
      setMediaResults(result.results);
      setMediaResultsVisible(true);
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaSearching(false);
    }
  }

  async function handleSourcePickerMediaSearch() {
    const trimmedQuery = sourcePickerMediaQuery.trim();
    if (!trimmedQuery) {
      setSourcePickerMediaError("Type movie or series title first.");
      return;
    }

    setIsSourcePickerMediaSearching(true);
    setSourcePickerMediaError(null);
    try {
      const result = await searchMedia(tgUserId, trimmedQuery, sourcePickerMediaFilter);
      setSourcePickerMediaResults(result.results);
      if (result.results.length === 0) {
        setSourcePickerMediaError("Nothing matched yet. Try the original title or add a year.");
      }
    } catch (requestError) {
      setSourcePickerMediaError(getErrorMessage(requestError));
    } finally {
      setIsSourcePickerMediaSearching(false);
    }
  }

  async function handleMusicTabSearch() {
    const trimmedQuery = musicTabQuery.trim();
    if (!trimmedQuery) {
      setMusicTabError("Type a song title or artist first.");
      return;
    }

    setIsMusicTabSearching(true);
    setMusicTabError(null);
    try {
      const result = await searchMusicTracks(tgUserId, trimmedQuery, 12);
      setMusicTabResults(result.results);
      if (result.results.length === 0) {
        setMusicTabError("No songs found yet. Try adding the artist name.");
      }
    } catch (requestError) {
      setMusicTabError(getErrorMessage(requestError));
    } finally {
      setIsMusicTabSearching(false);
    }
  }

  async function handleAddMedia(item: MediaSearchItem) {
    setMediaError(null);
    try {
      await addMediaToLibrary(tgUserId, item.tmdb_id, item.media_type);
      setMediaResults((current) =>
        current.map((mediaItem) =>
          mediaItem.tmdb_id === item.tmdb_id && mediaItem.media_type === item.media_type
            ? { ...mediaItem, is_in_library: true }
            : mediaItem
        )
      );
      setMediaResultsVisible(false);
      await loadMediaLibrary();
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    }
  }

  async function handleSelectSourcePickerMedia(item: MediaSearchItem) {
    const existingItem = sourcePickerMediaLibraryItems.find(
      (libraryItem) => libraryItem.tmdb_id === item.tmdb_id && libraryItem.media_type === item.media_type
    );

    if (existingItem) {
      setSourcePickerSelectedMedia(existingItem);
      setSourcePickerMediaError(null);
      return;
    }

    setIsSourcePickerApplying(true);
    setSourcePickerMediaError(null);
    try {
      const addedItem = await addMediaToLibrary(tgUserId, item.tmdb_id, item.media_type);
      setSourcePickerSelectedMedia(addedItem);
      setSourcePickerMediaResults((current) =>
        current.map((mediaItem) =>
          mediaItem.tmdb_id === item.tmdb_id && mediaItem.media_type === item.media_type
            ? { ...mediaItem, is_in_library: true }
            : mediaItem
        )
      );
      await loadMediaLibrary();
    } catch (requestError) {
      setSourcePickerMediaError(getErrorMessage(requestError));
    } finally {
      setIsSourcePickerApplying(false);
    }
  }

  function handleApplySourcePicker() {
    if (sourcePickerMode === "media") {
      if (!sourcePickerSelectedMedia) {
        setSourcePickerMediaError("Choose a movie or series first.");
        return;
      }

      setHomeMediaContext({
        media_item_id: sourcePickerSelectedMedia.id,
        source_label: sourcePickerSelectedMedia.title,
      });
      setSelectedSourceType("media");
      setSelectedMusicTrack(null);
      setMusicQuery("");
      setMusicResults([]);
      setMusicError(null);
      setSourcePickerMode(null);
      setHomeError(null);
      return;
    }

    if (sourcePickerMode === "music") {
      if (!sourcePickerSelectedMusicTrack) {
        setMusicError("Choose a song first.");
        return;
      }

      setSelectedMusicTrack(sourcePickerSelectedMusicTrack);
      setSelectedSourceType("music");
      setHomeMediaContext(null);
      setSourcePickerMode(null);
      setHomeError(null);
    }
  }

  async function openMediaDetail(item: MediaCard) {
    if (item.media_type === "movie") {
      await openMovie(item.id);
      return;
    }

    if (item.media_type === "series") {
      await openSeries(item.id);
      return;
    }

    await openFranchise(item.id);
  }

  async function openMovie(id: string) {
    setMediaView({ screen: "movie", id });
    setIsMediaDetailLoading(true);
    setMediaError(null);
    try {
      setMovieDetail(await fetchMovieDetail(id, tgUserId));
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaDetailLoading(false);
    }
  }

  async function openSeries(id: string) {
    setMediaView({ screen: "series", id });
    setIsMediaDetailLoading(true);
    setMediaError(null);
    try {
      setSeriesDetail(await fetchSeriesDetail(id, tgUserId));
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaDetailLoading(false);
    }
  }

  async function openSeason(id: string) {
    setMediaView({ screen: "season", id });
    setIsMediaDetailLoading(true);
    setMediaError(null);
    try {
      setSeasonDetail(await fetchSeasonDetail(id, tgUserId));
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaDetailLoading(false);
    }
  }

  async function openEpisode(id: string) {
    setMediaView({ screen: "episode", id });
    setIsMediaDetailLoading(true);
    setMediaError(null);
    try {
      setEpisodeDetail(await fetchEpisodeDetail(id, tgUserId));
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaDetailLoading(false);
    }
  }

  async function openFranchise(id: string) {
    setMediaView({ screen: "franchise", id });
    setIsMediaDetailLoading(true);
    setMediaError(null);
    try {
      setFranchiseDetail(await fetchFranchiseDetail(id, tgUserId));
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaDetailLoading(false);
    }
  }

  function openHomeWithMediaContext(context: HomeMediaContext) {
    setSelectedSourceType("media");
    setHomeMediaContext(context);
    setMusicQuery("");
    setMusicResults([]);
    setSelectedMusicTrack(null);
    setMusicError(null);
    setSourcePickerMode(null);
    setSourcePickerSelectedMusicTrack(null);
    setSourcePickerSelectedMedia(null);
    setActiveTab("home");
  }

  async function saveMovieProgress(markWatched: boolean) {
    if (!movieDetail) {
      return;
    }

    setIsMediaProgressSaving(true);
    setMediaError(null);
    try {
      const updated = await updateMovieProgress(
        movieDetail.item.id,
        tgUserId,
        markWatched ? null : movieDetail.item.watched_minutes,
        markWatched
      );
      setMovieDetail((current) => (current ? { ...current, item: updated } : current));
      await loadMediaLibrary();
      await loadStreak();
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaProgressSaving(false);
    }
  }

  async function saveEpisodeProgress(markWatched: boolean) {
    if (!episodeDetail) {
      return;
    }

    setIsMediaProgressSaving(true);
    setMediaError(null);
    try {
      const updated = await updateEpisodeProgress(
        episodeDetail.episode.id,
        tgUserId,
        markWatched ? null : episodeDetail.episode.watched_minutes,
        markWatched
      );
      setEpisodeDetail((current) => (current ? { ...current, episode: updated } : current));
      await loadMediaLibrary();
      await loadStreak();
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaProgressSaving(false);
    }
  }

  async function markSeasonWatched() {
    if (!seasonDetail) {
      return;
    }

    setIsMediaProgressSaving(true);
    setMediaError(null);
    try {
      const updatedSeason = await updateSeasonProgress(seasonDetail.season.id, tgUserId, true);
      setSeasonDetail((current) =>
        current
          ? {
              ...current,
              season: updatedSeason,
              episodes: current.episodes.map((episode) => ({
                ...episode,
                watched_minutes: episode.runtime_minutes,
                watched_percent: episode.runtime_minutes > 0 ? 100 : episode.watched_percent,
                is_watched: true,
              })),
            }
          : current
      );
      await loadMediaLibrary();
      await openSeason(seasonDetail.season.id);
      await loadStreak();
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaProgressSaving(false);
    }
  }

  async function markSeriesWatched() {
    if (!seriesDetail) {
      return;
    }

    setIsMediaProgressSaving(true);
    setMediaError(null);
    try {
      await updateSeriesProgress(seriesDetail.item.id, tgUserId, true);
      await openSeries(seriesDetail.item.id);
      await loadMediaLibrary();
      await loadStreak();
    } catch (requestError) {
      setMediaError(getErrorMessage(requestError));
    } finally {
      setIsMediaProgressSaving(false);
    }
  }

  function resetTabRoot(tab: AppTab) {
    setSelectedEntryId(null);
    if (tab === "home") {
      setHomeError(null);
      setMusicError(null);
      return;
    }

    if (tab === "words") {
      return;
    }

    if (tab === "media") {
      setMediaView({ screen: "library" });
      setMediaError(null);
      setMediaResultsVisible(false);
      return;
    }

    if (tab === "music") {
      setMusicTabError(null);
      return;
    }
  }

  const currentModel = analysisResponse?.ai_model || entries.find((entry) => entry.ai_model)?.ai_model || null;
  const handleMediaQueryChange = (event: ChangeEvent<HTMLInputElement>) => {
    setMediaQuery(event.target.value);
  };
  const handleMusicTabQueryChange = (event: ChangeEvent<HTMLInputElement>) => {
    setMusicTabQuery(event.target.value);
  };

  const navStreak = getNavStreakDisplay(streakSummary);

  return (
    <AppLayout
      activeTab={activeTab}
      streakCount={navStreak.count}
      streakTier={navStreak.tier}
      onTabChange={(tab) => {
        startTransition(() => {
          resetTabRoot(tab);
          setActiveTab(tab);
        });
      }}
    >
      {activeTab === "home" ? (
        <>
          <Card className="hero-card">
            <div className="card-heading">
              <div>
                <p className="section-title">Fast action</p>
                <h2>Add vocabulary in one clean flow</h2>
              </div>
              <span className="app-version-badge">v{APP_DISPLAY_VERSION}</span>
            </div>

            <div className="stack">
              <div className="mode-selector">
                <div className="mode-selector-head">
                  <div>
                    <p className="section-title">Slang mode</p>
                    <p className="detail-line">
                      Choose how AI should interpret and explain this word before analysis.
                    </p>
                  </div>
                </div>
                <div className="mode-grid">
                  {ANALYSIS_MODE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      data-mode={option.value}
                      className={option.value === analysisMode ? "mode-option active" : "mode-option"}
                      onClick={() => setAnalysisMode(option.value)}
                    >
                      <strong>{formatAnalysisModeLabel(option.value)}</strong>
                      <span>{option.description}</span>
                    </button>
                  ))}
                </div>
              </div>

              {activeSourceLabel ? (
                <Card className="home-source-context">
                  <div className="source-context-row">
                    <div>
                      <p className="section-title">
                        {selectedSourceType === "music" ? "Music source attached" : "Media source attached"}
                      </p>
                      <h3>{activeSourceLabel}</h3>
                    </div>
                    <div className="source-context-actions">
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => openSourcePicker(selectedSourceType === "music" ? "music" : "media")}
                      >
                        Change
                      </Button>
                      <Button type="button" variant="ghost" onClick={clearHomeSource}>
                        Clear
                      </Button>
                    </div>
                  </div>
                </Card>
              ) : null}

              <label className="input-field">
                <span className="input-label">English word or phrase</span>
                <textarea
                  ref={homeInputRef}
                  className="input-control input-control-textarea"
                  placeholder="For example: shallow, take it easy, or a short sentence"
                  rows={4}
                  autoCapitalize="sentences"
                  autoComplete="on"
                  autoCorrect="on"
                  enterKeyHint="done"
                  inputMode="text"
                  lang="en"
                  spellCheck={true}
                />
              </label>
              <Button type="button" isLoading={isAnalyzing} onClick={() => void handleAnalyzeEntry()}>
                Add / Analyze
              </Button>
            </div>

            {homeError ? <p className="feedback-message error">{homeError}</p> : null}
          </Card>

          {isAnalyzing ? <LoadingState message="AI is analyzing your word..." /> : null}

          {analysisResponse ? (
            <>
              <ResultCard
                aiModel={analysisResponse.ai_model}
                analysis={analysisResponse.analysis}
                analysisMode={analysisResponse.analysis_mode}
                destinationOptions={DESTINATION_OPTIONS}
                isSaveDisabled={
                  (selectedSourceType === "music" && !selectedMusicTrack) ||
                  (selectedSourceType === "media" && !homeMediaContext)
                }
                isSaving={isSaving}
                onDestinationChange={(next) => {
                  setHomeError(null);

                  if (next === "unsorted") {
                    clearHomeSource();
                    return;
                  }

                  if (next === "media") {
                    openSourcePicker("media");
                    return;
                  }

                  openSourcePicker("music");
                }}
                onSave={handleSaveAnalyzedEntry}
                onDismiss={handleDismissAnalyzedEntry}
                saveHint={
                  selectedSourceType === "music" && !selectedMusicTrack
                    ? "Pick a song first, then save the word to Music."
                    : selectedSourceType === "media" && !homeMediaContext
                      ? "Pick a movie or series first, then save the word to Media."
                      : null
                }
                selectedDestination={selectedSourceType}
              />
            </>
          ) : null}

          <Card className="voice-hint-card">
            <p className="section-title">Add by voice</p>
            <p className="detail-line">
              You can also send a <strong>voice message</strong> directly to the bot instead of typing.
            </p>
            <p className="detail-line">
              Try: <em>"I learned shallow from a song"</em> or <em>"What does gring mean in slang?"</em>
            </p>
          </Card>

          <Card>
            <div className="card-heading">
              <div>
                <p className="section-title">Recent words</p>
                <h2>Last 5 saved entries</h2>
              </div>
            </div>

            {isLoading ? (
              <LoadingState message="Loading recent words..." />
            ) : recentEntries.length > 0 ? (
              <motion.div className="recent-list" variants={listContainer} initial="hidden" animate="show">
                {recentEntries.map((entry) => (
                  <motion.button
                    key={entry.id}
                    type="button"
                    className="recent-item"
                    variants={listItem}
                    onClick={() => setSelectedEntryId(entry.id)}
                  >
                    <div className={entry.source_image_url ? "recent-item-main has-thumb" : "recent-item-main"}>
                      {entry.source_image_url ? (
                        <img
                          className="recent-item-thumb"
                          src={entry.source_image_url}
                          alt={entry.source_label || entry.original_text}
                          loading="lazy"
                        />
                      ) : null}
                      <strong>{entry.original_text}</strong>
                      <span>{entry.translation_ru}</span>
                    </div>
                    <small>{entry.source_label || formatSourceLabel(entry.source_type)}</small>
                  </motion.button>
                ))}
              </motion.div>
            ) : (
              <EmptyState
                title="No words saved yet"
                description="Analyze your first word above and it will appear here for quick access."
              />
            )}
          </Card>
        </>
      ) : null}

      {activeTab === "words" ? (
        <WordsTab
          entries={entries}
          isLoading={isLoading}
          screenError={screenError}
          onDelete={handleDeleteEntry}
          onIncreaseRepeat={handleIncreaseRepeat}
          onMarkLearned={handleMarkLearned}
          onOpenDetails={setSelectedEntryId}
        />
      ) : null}

      {activeTab === "streak" ? (
        <>
          {screenError ? <p className="feedback-message error">{screenError}</p> : null}

          <StreakPage
            streak={streakSummary}
            isLoading={isStreakLoading}
            isSuggestionLoading={isDailySuggestionLoading}
            onGoHome={() => {
              startTransition(() => {
                setActiveTab("home");
              });
            }}
            onSuggestWords={() => {
              void handleFetchDailySuggestions();
            }}
            onSaveSuggestion={(item) => {
              void handleSaveSuggestedWord(item);
            }}
            onBlacklistSuggestion={(item) => {
              void handleBlacklistSuggestedWord(item);
            }}
            suggestion={dailySuggestion}
            suggestionError={dailySuggestionError}
            savingSuggestionText={savingSuggestionText}
            blacklistingSuggestionText={blacklistingSuggestionText}
            savedSuggestionTexts={savedSuggestionTexts}
            blacklistedSuggestionTexts={blacklistedSuggestionTexts}
          />
        </>
      ) : null}

      {activeTab === "media" ? (
        <>
          <Card>
            <div className="stack">
              <Input
                type="search"
                label="Search media"
                placeholder="Try: Dexter, Spider-Man, Interstellar"
                value={mediaQuery}
                onChange={handleMediaQueryChange}
              />
              <div className="filter-row">
                {MEDIA_SEARCH_FILTERS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={option.value === mediaFilter ? "filter-chip active" : "filter-chip"}
                    onClick={() => setMediaFilter(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              <Button type="button" isLoading={isMediaSearching} onClick={() => void handleMediaSearch()}>
                Search
              </Button>
            </div>
          </Card>

          {mediaError ? <p className="feedback-message error">{mediaError}</p> : null}

          {isMediaSearching ? <LoadingState message="Searching TMDB..." /> : null}

          {mediaResultsVisible && mediaResults.length > 0 ? (
            <div className="media-grid">
              <Card className="media-results-toolbar">
                <div className="card-heading">
                  <div>
                    <p className="section-title">Search results</p>
                    <h3>{mediaResults.length} items found</h3>
                  </div>
                  <Button type="button" variant="ghost" onClick={() => setMediaResultsVisible(false)}>
                    Hide results
                  </Button>
                </div>
              </Card>
              {mediaResults.map((item) => (
                <Card key={`${item.media_type}-${item.tmdb_id}`} className="media-card">
                  <div className="media-card-body">
                    <Poster path={item.poster_path} title={item.title} />
                    <div className="media-card-copy">
                      <p className="section-title">{item.media_type === "movie" ? "Movie" : "Series"}</p>
                      <h3>{item.title}</h3>
                      <p className="detail-line">
                        {item.year || "Year n/a"} • {item.media_type === "movie" ? "Movie" : "Series"}
                      </p>
                      <p className="detail-line clamp-3">{item.overview || "No overview yet."}</p>
                      <Button
                        type="button"
                        variant={item.is_in_library ? "ghost" : "primary"}
                        disabled={item.is_in_library}
                        onClick={() => void handleAddMedia(item)}
                      >
                        {item.is_in_library ? "Added" : "Add to library"}
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : null}

          {mediaView.screen === "library" ? (
            <>
              <Card>
                <div className="card-heading">
                  <div>
                    <p className="section-title">My library</p>
                    <h2>Movies, series, and franchises</h2>
                  </div>
                </div>

                {isMediaLoading ? (
                  <LoadingState message="Loading library..." />
                ) : mediaLibrary ? (
                  <div className="stack">
                    <LibraryGroup title="Movies" items={mediaLibrary.movies} onOpen={openMediaDetail} />
                    <LibraryGroup title="Series" items={mediaLibrary.series} onOpen={openMediaDetail} />
                    <LibraryGroup title="Franchises" items={mediaLibrary.franchises} onOpen={openMediaDetail} />
                  </div>
                ) : (
                  <EmptyState
                    title="Library is empty"
                    description="Search media above and add your first movie or series."
                  />
                )}
              </Card>

              <Card>
                <div className="card-heading">
                  <div>
                    <p className="section-title">Media vocabulary</p>
                    <h2>Open words by media scope</h2>
                  </div>
                </div>

                <div className="filter-row">
                  {MEDIA_WORD_SCOPE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={option.value === mediaWordsScope ? "filter-chip active" : "filter-chip"}
                      onClick={() => {
                        setMediaWordsScope(option.value);
                        void loadMediaVocabulary(option.value);
                      }}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>

                {isMediaWordsLoading ? (
                  <LoadingState message="Loading media words..." />
                ) : mediaScopeWords.length > 0 ? (
                  <div className="word-grid">
                    {mediaScopeWords.map((entry) => (
                      <WordCard
                        key={entry.id}
                        entry={entry}
                        onDelete={handleDeleteEntry}
                        onIncreaseRepeat={handleIncreaseRepeat}
                        onMarkLearned={handleMarkLearned}
                        onOpenDetails={setSelectedEntryId}
                      />
                    ))}
                  </div>
                ) : (
                  <EmptyState
                    title="No words in this scope yet"
                    description="Add vocabulary from media pages and it will appear here."
                  />
                )}
              </Card>
            </>
          ) : null}

          {isMediaDetailLoading ? <LoadingState message="Loading media details..." /> : null}

          {mediaView.screen === "movie" && movieDetail ? (
            <Card>
              <div className="card-heading">
                <Button type="button" variant="ghost" onClick={() => setMediaView({ screen: "library" })}>
                  Back to library
                </Button>
              </div>
              <div className="media-card-body">
                <Poster path={movieDetail.item.poster_path} title={movieDetail.item.title} />
                <div className="media-card-copy">
                  <p className="section-title">Movie</p>
                  <h2>{movieDetail.item.title}</h2>
                  <p className="detail-line">
                    Runtime: {movieDetail.item.runtime_minutes || 0} min • {movieDetail.item.watched_percent}%
                  </p>
                  <p className="detail-line">{movieDetail.item.overview || "No overview yet."}</p>
                  <p className="detail-line">{movieDetail.item.watched_minutes} / {movieDetail.item.runtime_minutes} min</p>
                </div>
              </div>

              <div className="stack media-progress-block">
                <input
                  className="progress-slider"
                  type="range"
                  min={0}
                  max={Math.max(movieDetail.item.runtime_minutes, 1)}
                  value={movieDetail.item.watched_minutes}
                  onChange={(event) => {
                    const nextMinutes = Number(event.target.value);
                    setMovieDetail((current) =>
                      current
                        ? {
                            ...current,
                            item: {
                              ...current.item,
                              watched_minutes: nextMinutes,
                              watched_percent: calcPercent(nextMinutes, current.item.runtime_minutes),
                            },
                          }
                        : current
                    );
                  }}
                />
                <div className="media-progress-actions">
                  <Button type="button" isLoading={isMediaProgressSaving} onClick={() => void saveMovieProgress(false)}>
                    Save progress
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    isLoading={isMediaProgressSaving}
                    onClick={() => void saveMovieProgress(true)}
                  >
                    Mark watched
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() =>
                      openHomeWithMediaContext({
                        media_item_id: movieDetail.item.id,
                        source_label: movieDetail.item.title,
                      })
                    }
                  >
                    Add word from this movie
                  </Button>
                </div>
              </div>

              <MediaWordsSection words={movieDetail.words} onOpenWord={setSelectedEntryId} />
            </Card>
          ) : null}

          {mediaView.screen === "series" && seriesDetail ? (
            <Card>
              <div className="card-heading">
                <Button type="button" variant="ghost" onClick={() => setMediaView({ screen: "library" })}>
                  Back to library
                </Button>
              </div>
              <div className="media-card-body">
                <Poster path={seriesDetail.item.poster_path} title={seriesDetail.item.title} />
                <div className="media-card-copy">
                  <p className="section-title">Series</p>
                  <h2>{seriesDetail.item.title}</h2>
                  <p className="detail-line">
                    Episodes watched: {seriesDetail.watched_episodes} / {seriesDetail.total_episodes}
                  </p>
                  <p className="detail-line">{seriesDetail.item.overview || "No overview yet."}</p>
                </div>
              </div>

              <div className="stack">
                <Button
                  type="button"
                  isLoading={isMediaProgressSaving}
                  onClick={() => void markSeriesWatched()}
                >
                  Mark whole series watched
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() =>
                    openHomeWithMediaContext({
                      media_item_id: seriesDetail.item.id,
                      source_label: seriesDetail.item.title,
                    })
                  }
                >
                  Add word from this series
                </Button>

                <div className="stack">
                  {seriesDetail.seasons.map((season) => (
                    <button
                      key={season.id}
                      type="button"
                      className="list-row-button"
                      onClick={() => void openSeason(season.id)}
                    >
                      <strong>
                        S{season.season_number}: {season.title}
                      </strong>
                      <span>
                        {season.watched_episodes}/{season.episode_count} episodes • {season.watched_percent}%
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <MediaWordsSection words={seriesDetail.words} onOpenWord={setSelectedEntryId} />
            </Card>
          ) : null}

          {mediaView.screen === "season" && seasonDetail ? (
            <Card>
              <div className="card-heading">
                <Button type="button" variant="ghost" onClick={() => void openSeries(seasonDetail.series_item_id)}>
                  Back to series
                </Button>
              </div>

              <p className="section-title">Season</p>
              <h2>
                S{seasonDetail.season.season_number}: {seasonDetail.season.title}
              </h2>
              <p className="detail-line">
                {seasonDetail.season.watched_episodes}/{seasonDetail.season.episode_count} episodes watched •{" "}
                {seasonDetail.season.watched_percent}%
              </p>

              <div className="stack">
                <Button type="button" isLoading={isMediaProgressSaving} onClick={() => void markSeasonWatched()}>
                  Mark whole season watched
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() =>
                    openHomeWithMediaContext({
                      media_item_id: seasonDetail.series_item_id,
                      media_season_id: seasonDetail.season.id,
                      source_label: `Season ${seasonDetail.season.season_number}`,
                    })
                  }
                >
                  Add word from this season
                </Button>

                {seasonDetail.episodes.map((episode) => (
                  <button
                    key={episode.id}
                    type="button"
                    className="list-row-button"
                    onClick={() => void openEpisode(episode.id)}
                  >
                    <strong>
                      E{episode.episode_number}: {episode.title}
                    </strong>
                    <span>
                      {episode.watched_minutes}/{episode.runtime_minutes} min • {episode.watched_percent}%
                    </span>
                  </button>
                ))}
              </div>

              <MediaWordsSection words={seasonDetail.words} onOpenWord={setSelectedEntryId} />
            </Card>
          ) : null}

          {mediaView.screen === "episode" && episodeDetail ? (
            <Card>
              <div className="card-heading">
                <Button type="button" variant="ghost" onClick={() => void openSeason(episodeDetail.season_id)}>
                  Back to season
                </Button>
              </div>

              <p className="section-title">Episode</p>
              <h2>
                S{episodeDetail.episode.season_number}E{episodeDetail.episode.episode_number}: {episodeDetail.episode.title}
              </h2>
              <p className="detail-line">{episodeDetail.episode.overview || "No overview yet."}</p>
              <p className="detail-line">
                {episodeDetail.episode.watched_minutes}/{episodeDetail.episode.runtime_minutes} min •{" "}
                {episodeDetail.episode.watched_percent}%
              </p>

              <div className="stack media-progress-block">
                <input
                  className="progress-slider"
                  type="range"
                  min={0}
                  max={Math.max(episodeDetail.episode.runtime_minutes, 1)}
                  value={episodeDetail.episode.watched_minutes}
                  onChange={(event) => {
                    const nextMinutes = Number(event.target.value);
                    setEpisodeDetail((current) =>
                      current
                        ? {
                            ...current,
                            episode: {
                              ...current.episode,
                              watched_minutes: nextMinutes,
                              watched_percent: calcPercent(nextMinutes, current.episode.runtime_minutes),
                            },
                          }
                        : current
                    );
                  }}
                />
                <div className="media-progress-actions">
                  <Button
                    type="button"
                    isLoading={isMediaProgressSaving}
                    onClick={() => void saveEpisodeProgress(false)}
                  >
                    Save progress
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    isLoading={isMediaProgressSaving}
                    onClick={() => void saveEpisodeProgress(true)}
                  >
                    Mark watched
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() =>
                      openHomeWithMediaContext({
                        media_item_id: episodeDetail.series_item_id,
                        media_season_id: episodeDetail.season_id,
                        media_episode_id: episodeDetail.episode.id,
                        source_label: `S${episodeDetail.episode.season_number}E${episodeDetail.episode.episode_number}`,
                      })
                    }
                  >
                    Add word from this episode
                  </Button>
                </div>
              </div>

              <MediaWordsSection words={episodeDetail.words} onOpenWord={setSelectedEntryId} />
            </Card>
          ) : null}

          {mediaView.screen === "franchise" && franchiseDetail ? (
            <Card>
              <div className="card-heading">
                <Button type="button" variant="ghost" onClick={() => setMediaView({ screen: "library" })}>
                  Back to library
                </Button>
              </div>
              <p className="section-title">Franchise</p>
              <h2>{franchiseDetail.item.title}</h2>
              <p className="detail-line">
                {franchiseDetail.watched_minutes}/{franchiseDetail.total_runtime_minutes} min watched •{" "}
                {franchiseDetail.watched_percent}%
              </p>

              <Button
                type="button"
                variant="ghost"
                onClick={() =>
                  openHomeWithMediaContext({
                    media_franchise_id: franchiseDetail.item.id,
                    source_label: franchiseDetail.item.title,
                  })
                }
              >
                Add word from this franchise
              </Button>

              <div className="stack">
                {franchiseDetail.movies.map((movie) => (
                  <button
                    key={movie.id}
                    type="button"
                    className="list-row-button"
                    onClick={() => void openMovie(movie.id)}
                  >
                    <strong>{movie.title}</strong>
                    <span>
                      {movie.watched_minutes}/{movie.runtime_minutes} min • {movie.watched_percent}%
                    </span>
                  </button>
                ))}
              </div>

              <MediaWordsSection words={franchiseDetail.words} onOpenWord={setSelectedEntryId} />
            </Card>
          ) : null}
        </>
      ) : null}

      {activeTab === "music" ? (
        <>
          <Card>
            <div className="stack">
              <Input
                type="search"
                label="Search songs"
                placeholder="Try: The Weeknd Starboy, Arctic Monkeys 505"
                value={musicTabQuery}
                onChange={handleMusicTabQueryChange}
              />
              <Button type="button" isLoading={isMusicTabSearching} onClick={() => void handleMusicTabSearch()}>
                Search songs
              </Button>
            </div>
          </Card>

          {musicTabError ? <p className="feedback-message error">{musicTabError}</p> : null}

          {musicTabResults.length > 0 ? (
            <Card>
              <div className="card-heading">
                <div>
                  <p className="section-title">Song results</p>
                  <h2>Pick a track for your next word</h2>
                </div>
              </div>
              <div className="music-search-results">
                {musicTabResults.map((track) => (
                  <button
                    key={`${track.external_id}-${track.release_external_id ?? "release"}`}
                    type="button"
                    className="music-search-item"
                    onClick={() => {
                      setSelectedSourceType("music");
                      setSelectedMusicTrack(track);
                      setHomeMediaContext(null);
                      setHomeError(null);
                      setActiveTab("home");
                    }}
                  >
                    {track.artwork_url ? (
                      <img className="music-track-artwork" src={track.artwork_url} alt={track.title} loading="lazy" />
                    ) : (
                      <div className="music-track-artwork music-track-artwork-placeholder">
                        {track.title.slice(0, 1).toUpperCase()}
                      </div>
                    )}
                    <div className="music-search-copy">
                      <strong>{track.title}</strong>
                      <span>{track.artist_name}</span>
                      <small>
                        {[track.release_title, track.release_year].filter(Boolean).join(" · ") || "MusicBrainz"}
                      </small>
                    </div>
                    <span className="music-search-select">Use on Home</span>
                  </button>
                ))}
              </div>
            </Card>
          ) : null}

          <Card>
            <div className="card-heading">
              <div>
                <p className="section-title">My music words</p>
                <h2>Vocabulary saved from songs</h2>
              </div>
            </div>
            {recentMusicEntries.length > 0 ? (
              <div className="word-grid">
                {recentMusicEntries.map((entry) => (
                  <WordCard
                    key={entry.id}
                    entry={entry}
                    onDelete={handleDeleteEntry}
                    onIncreaseRepeat={handleIncreaseRepeat}
                    onMarkLearned={handleMarkLearned}
                    onOpenDetails={setSelectedEntryId}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                title="No music words yet"
                description="Choose Music as destination on Home, pick a song, and save your first entry."
              />
            )}
          </Card>
        </>
      ) : null}

      {activeTab === "settings" ? (
        <>
          <div className="settings-grid">
            <Card>
              <div className="theme-toggle-card">
                <div className="theme-toggle-info">
                  <p className="section-title" style={{ margin: 0 }}>
                    Appearance
                  </p>
                  <h3 style={{ margin: "4px 0 0" }}>
                    {theme === "dark" ? "Dark mode" : "Light mode"}
                  </h3>
                  <p className="detail-line" style={{ marginTop: 4 }}>
                    {theme === "dark" ? "Easy on the eyes at night." : "Clean and bright for day use."}
                  </p>
                </div>
                <button
                  type="button"
                  className="theme-switch"
                  onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                  aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
                >
                  <div className={`theme-switch-track${theme === "light" ? " on" : ""}`}>
                    <div className="theme-switch-thumb" />
                  </div>
                </button>
              </div>
            </Card>

            <Card className="ai-instructions-card">
              <div className="card-heading">
                <div>
                  <p className="section-title">AI Custom Instructions</p>
                  <h3 style={{ margin: "4px 0 0" }}>Customize AI behavior</h3>
                  <p className="detail-line" style={{ marginTop: 4 }}>
                    Add your preferences for how AI should explain words, create examples, and suggest vocabulary.
                  </p>
                </div>
              </div>
              
              <div className="stack">
                {isAiInstructionsLoading ? (
                  <LoadingState message="Loading your instructions..." />
                ) : (
                  <>
                    <label className="input-field">
                      <span className="input-label">Your instructions (optional)</span>
                      <textarea
                        className="input-control input-control-textarea"
                        placeholder="Example: Focus on British English, use simple explanations, include idioms..."
                        rows={6}
                        value={aiInstructions}
                        onChange={(e) => setAiInstructions(e.target.value)}
                        autoCapitalize="sentences"
                        autoComplete="on"
                        autoCorrect="on"
                        enterKeyHint="done"
                        inputMode="text"
                        spellCheck={true}
                      />
                    </label>
                    
                    <Button 
                      type="button" 
                      isLoading={isAiInstructionsSaving} 
                      onClick={() => void handleSaveAiInstructions()}
                    >
                      {aiInstructionsSaved ? "✓ Saved!" : "Save Instructions"}
                    </Button>
                    
                    {aiInstructionsError ? (
                      <p className="feedback-message error">{aiInstructionsError}</p>
                    ) : null}
                  </>
                )}
              </div>
            </Card>

            <Card>
              <p className="section-title">App</p>
              <h3 style={{ margin: "0 0 8px" }}>Telegram English Vocabulary</h3>
              <p className="detail-line">Vocabulary notebook for Russian-speaking English learners.</p>
            </Card>
            <Card>
              <p className="section-title">AI Provider</p>
              <h3 style={{ margin: "0 0 8px" }}>Gemini</h3>
              <p className="detail-line">Model: {currentModel || "Configured in backend environment"}</p>
            </Card>
            <Card>
              <p className="section-title">Media Provider</p>
              <h3 style={{ margin: "0 0 8px" }}>TMDB</h3>
              <p className="detail-line">Movies, TV series, and franchise metadata.</p>
            </Card>
          </div>
        </>
      ) : null}

      {selectedEntry ? (
        <EntryDetailsModal
          entry={selectedEntry}
          tgUserId={tgUserId}
          onFollowUpComplete={() => {
            void loadStreak();
          }}
          onClose={() => {
            setSelectedEntryId(null);
          }}
        />
      ) : null}

      {sourcePickerMode ? (
        <SourcePickerModal
          mediaError={sourcePickerMediaError}
          mediaFilter={sourcePickerMediaFilter}
          mediaLibraryItems={sourcePickerMediaLibraryItems}
          mediaQuery={sourcePickerMediaQuery}
          mediaResults={sourcePickerMediaResults}
          mode={sourcePickerMode}
          musicError={musicError}
          musicQuery={musicQuery}
          musicResults={musicResults}
          onApply={handleApplySourcePicker}
          onClose={closeSourcePicker}
          onMediaFilterChange={setSourcePickerMediaFilter}
          onMediaQueryChange={setSourcePickerMediaQuery}
          onMediaSearch={() => void handleSourcePickerMediaSearch()}
          onMusicQueryChange={setMusicQuery}
          onMusicSearch={() => void handleMusicSearch()}
          onSelectLibraryMedia={(item) => {
            setSourcePickerSelectedMedia(item);
            setSourcePickerMediaError(null);
          }}
          onSelectMediaResult={(item) => void handleSelectSourcePickerMedia(item)}
          onSelectMusicTrack={handleSelectMusicTrack}
          selectedMedia={sourcePickerSelectedMedia}
          selectedMusicTrack={sourcePickerSelectedMusicTrack}
          isApplying={isSourcePickerApplying}
          isMediaSearching={isSourcePickerMediaSearching}
          isMusicSearching={isMusicSearching}
        />
      ) : null}
    </AppLayout>
  );
}

type LibraryGroupProps = {
  title: string;
  items: MediaCard[];
  onOpen: (item: MediaCard) => Promise<void>;
};

function LibraryGroup({ title, items, onOpen }: LibraryGroupProps) {
  return (
    <div className="library-group">
      <p className="section-title">{title}</p>
      {items.length > 0 ? (
        <div className="stack">
          {items.map((item) => (
            <button key={item.id} type="button" className="list-row-button" onClick={() => void onOpen(item)}>
              <strong>{item.title}</strong>
              <span>
                {item.watched_minutes}/{item.runtime_minutes} min • {item.watched_percent}% •{" "}
                {item.is_watched ? "watched" : "in progress"}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <p className="detail-line">No items yet.</p>
      )}
    </div>
  );
}

type PosterProps = {
  path: string | null;
  title: string;
};

function Poster({ path, title }: PosterProps) {
  if (!path) {
    return <div className="media-poster-placeholder">{title.slice(0, 1).toUpperCase()}</div>;
  }

  return <img className="media-poster" src={`${TMDB_IMAGE_BASE_URL}${path}`} alt={title} loading="lazy" />;
}

type MediaWordsSectionProps = {
  words: Array<{
    id: string;
    original_text: string;
    translation_ru: string;
    status: string;
    source_label: string | null;
  }>;
  onOpenWord: (id: string) => void;
};

function MediaWordsSection({ words, onOpenWord }: MediaWordsSectionProps) {
  return (
    <div className="media-words-section">
      <p className="section-title">Words from this source</p>
      {words.length > 0 ? (
        <div className="stack">
          {words.map((word) => (
            <button key={word.id} type="button" className="list-row-button" onClick={() => onOpenWord(word.id)}>
              <strong>{word.original_text}</strong>
              <span>
                {word.translation_ru} • {word.status}
                {word.source_label ? ` • ${word.source_label}` : ""}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <p className="detail-line">No words linked yet.</p>
      )}
    </div>
  );
}

function calcPercent(current: number, total: number): number {
  if (!total || total <= 0) {
    return 0;
  }
  return Math.round((current / total) * 100);
}

function normalizeVocabularyStatus(value: string): VocabularyEntry["status"] {
  if (value === "new" || value === "learning" || value === "learned") {
    return value;
  }
  return "learning";
}

function getTelegramUser(): { id: number; username?: string; firstName?: string } {
  const user = window.Telegram?.WebApp?.initDataUnsafe?.user;

  if (user?.id) {
    window.localStorage.setItem(STORAGE_TG_USER_KEY, String(user.id));
    return {
      id: user.id,
      username: user.username,
      firstName: user.first_name,
    };
  }

  if (import.meta.env.PROD) {
    const storedUserId = Number(window.localStorage.getItem(STORAGE_TG_USER_KEY) || "");
    if (Number.isFinite(storedUserId) && storedUserId > 0) {
      return { id: storedUserId };
    }
    return { id: 0 };
  }

  const envDevUserId = Number(import.meta.env.VITE_DEV_TG_USER_ID || DEFAULT_DEV_TG_USER_ID);
  const storedUserId = Number(window.localStorage.getItem(STORAGE_TG_USER_KEY) || "");
  const fallbackUserId = Number.isFinite(storedUserId) && storedUserId > 0 ? storedUserId : envDevUserId;

  return {
    id: fallbackUserId,
    username: undefined,
    firstName: undefined,
  };
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

export default App;
