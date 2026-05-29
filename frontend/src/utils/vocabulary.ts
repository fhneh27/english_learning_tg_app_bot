import {
  VocabularyAnalysisMode,
  VocabularyEntry,
  VocabularySourceType,
  VocabularyStatus,
} from "../types/vocabulary";

export type WordsFilter = "all" | VocabularyStatus | VocabularySourceType;

export function formatStatusLabel(status: VocabularyStatus): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

export function formatSourceLabel(sourceType: VocabularySourceType): string {
  if (sourceType === "unsorted") {
    return "Unsorted";
  }

  if (sourceType === "media") {
    return "Movie / Series";
  }

  return "Music";
}

export function formatAnalysisModeLabel(mode: VocabularyAnalysisMode): string {
  if (mode === "general") {
    return "General";
  }

  if (mode === "slang") {
    return "Slang";
  }

  return "Conversation";
}

export function filterEntries(entries: VocabularyEntry[], filter: WordsFilter, query: string): VocabularyEntry[] {
  const trimmedQuery = query.trim().toLowerCase();

  return entries.filter((entry) => {
    const matchesFilter =
      filter === "all" || entry.status === filter || entry.source_type === filter;

    if (!matchesFilter) {
      return false;
    }

    if (!trimmedQuery) {
      return true;
    }

    return [entry.original_text, entry.translation_ru, entry.meaning_ru, entry.normalized_text]
      .join(" ")
      .toLowerCase()
      .includes(trimmedQuery);
  });
}

export function sortReviewEntries(entries: VocabularyEntry[]): VocabularyEntry[] {
  return [...entries]
    .filter((entry) => entry.status === "new" || entry.status === "learning")
    .sort((left, right) => {
      if (left.repeat_count !== right.repeat_count) {
        return left.repeat_count - right.repeat_count;
      }

      return Date.parse(right.created_at) - Date.parse(left.created_at);
    });
}
