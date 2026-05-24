import { VocabularyEntry } from "../types/vocabulary";

type EntryCardProps = {
  entry: VocabularyEntry;
  onDelete: (entryId: string) => Promise<void>;
  onIncreaseRepeat: (entryId: string) => Promise<void>;
  onMarkLearned: (entryId: string) => Promise<void>;
  onOpenDetails: (entryId: string) => void;
};

function EntryCard({
  entry,
  onDelete,
  onIncreaseRepeat,
  onMarkLearned,
  onOpenDetails,
}: EntryCardProps) {
  return (
    <article className="entry-card clickable" onClick={() => onOpenDetails(entry.id)}>
      <div className="entry-card-header">
        <div>
          <h3>{entry.original_text}</h3>
          {entry.transcription ? <p className="transcription">{entry.transcription}</p> : null}
        </div>
        <button
          className="ghost-button danger"
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            void onDelete(entry.id);
          }}
        >
          Delete
        </button>
      </div>

      <p className="translation">{entry.translation_ru}</p>
      <p className="meaning compact">{entry.meaning_ru}</p>

      <div className="entry-footer">
        {entry.status === "learning" ? (
          <div className="learning-actions">
            <p className="meta-text">Repeats: {entry.repeat_count}</p>
            <button
              type="button"
              className="status-pill"
              onClick={(event) => {
                event.stopPropagation();
                void onIncreaseRepeat(entry.id);
              }}
            >
              +1 repeat
            </button>
            <button
              type="button"
              className="status-pill active"
              onClick={(event) => {
                event.stopPropagation();
                void onMarkLearned(entry.id);
              }}
            >
              learned
            </button>
          </div>
        ) : (
          <p className="meta-text">Learned. Repeats: {entry.repeat_count}</p>
        )}

        <p className="meta-text">
          {entry.part_of_speech || "phrase"} {entry.level ? `- ${entry.level}` : ""}
        </p>
      </div>
    </article>
  );
}

export default EntryCard;
