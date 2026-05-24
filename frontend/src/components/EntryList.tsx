import EntryCard from "./EntryCard";
import { VocabularyEntry } from "../types/vocabulary";

type EntryListProps = {
  entries: VocabularyEntry[];
  isLoading: boolean;
  onDelete: (entryId: string) => Promise<void>;
  onIncreaseRepeat: (entryId: string) => Promise<void>;
  onMarkLearned: (entryId: string) => Promise<void>;
  onOpenDetails: (entryId: string) => void;
};

function EntryList({
  entries,
  isLoading,
  onDelete,
  onIncreaseRepeat,
  onMarkLearned,
  onOpenDetails,
}: EntryListProps) {
  if (isLoading && entries.length === 0) {
    return <p className="state-message">Loading your vocabulary...</p>;
  }

  if (entries.length === 0) {
    return (
      <p className="state-message">
        No entries yet. Add your first word or phrase above and it will appear here.
      </p>
    );
  }

  return (
    <div className={isLoading ? "entry-list is-loading" : "entry-list"}>
      {isLoading ? <p className="list-loading">Updating list...</p> : null}
      {entries.map((entry) => (
        <EntryCard
          key={entry.id}
          entry={entry}
          onDelete={onDelete}
          onIncreaseRepeat={onIncreaseRepeat}
          onMarkLearned={onMarkLearned}
          onOpenDetails={onOpenDetails}
        />
      ))}
    </div>
  );
}

export default EntryList;
