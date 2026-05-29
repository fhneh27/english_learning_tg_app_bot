import { ChangeEvent, memo, useDeferredValue, useMemo, useState } from "react";

import Card from "../components/Card";
import EmptyState from "../components/EmptyState";
import Input from "../components/Input";
import LoadingState from "../components/LoadingState";
import WordCard from "../components/WordCard";
import { VocabularyEntry } from "../types/vocabulary";
import { filterEntries, WordsFilter } from "../utils/vocabulary";

const WORD_FILTER_OPTIONS: Array<{ label: string; value: WordsFilter }> = [
  { label: "All", value: "all" },
  { label: "New", value: "new" },
  { label: "Learning", value: "learning" },
  { label: "Learned", value: "learned" },
  { label: "Unsorted", value: "unsorted" },
  { label: "Movie / Series", value: "media" },
  { label: "Music", value: "music" },
];

type WordsTabProps = {
  entries: VocabularyEntry[];
  isLoading: boolean;
  screenError: string | null;
  onDelete: (entryId: string) => Promise<void>;
  onIncreaseRepeat: (entryId: string) => Promise<void>;
  onMarkLearned: (entryId: string) => Promise<void>;
  onOpenDetails: (entryId: string) => void;
};

function WordsTab({
  entries,
  isLoading,
  screenError,
  onDelete,
  onIncreaseRepeat,
  onMarkLearned,
  onOpenDetails,
}: WordsTabProps) {
  const [wordsQuery, setWordsQuery] = useState("");
  const [wordsFilter, setWordsFilter] = useState<WordsFilter>("all");
  const deferredWordsQuery = useDeferredValue(wordsQuery);
  const filteredWords = useMemo(
    () => filterEntries(entries, wordsFilter, deferredWordsQuery),
    [deferredWordsQuery, entries, wordsFilter]
  );

  function handleWordsQueryChange(event: ChangeEvent<HTMLInputElement>) {
    setWordsQuery(event.target.value);
  }

  return (
    <>
      <Card>
        <div className="stack">
          <Input
            type="search"
            label="Search vocabulary"
            placeholder="Search by word, translation, or meaning"
            value={wordsQuery}
            onChange={handleWordsQueryChange}
          />
          <div className="filter-row">
            {WORD_FILTER_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={option.value === wordsFilter ? "filter-chip active" : "filter-chip"}
                onClick={() => setWordsFilter(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {screenError ? <p className="feedback-message error">{screenError}</p> : null}

      {isLoading ? (
        <LoadingState message="Loading your vocabulary..." />
      ) : filteredWords.length > 0 ? (
        <div className="word-grid">
          {filteredWords.map((entry) => (
            <WordCard
              key={entry.id}
              entry={entry}
              onDelete={onDelete}
              onIncreaseRepeat={onIncreaseRepeat}
              onMarkLearned={onMarkLearned}
              onOpenDetails={onOpenDetails}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="Nothing matches this view"
          description="Try another search or filter, or add a new word from the Home tab."
        />
      )}
    </>
  );
}

export default memo(WordsTab);
