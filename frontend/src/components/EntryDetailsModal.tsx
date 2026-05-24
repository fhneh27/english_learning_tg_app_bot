import { VocabularyEntry } from "../types/vocabulary";

type EntryDetailsModalProps = {
  entry: VocabularyEntry;
  onClose: () => void;
};

function EntryDetailsModal({ entry, onClose }: EntryDetailsModalProps) {
  return (
    <div className="entry-modal-overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="entry-modal" onClick={(event) => event.stopPropagation()}>
        <div className="entry-modal-header">
          <h2>{entry.original_text}</h2>
          <button type="button" className="ghost-button" onClick={onClose}>
            Close
          </button>
        </div>

        <p className="translation">{entry.translation_ru}</p>
        <p className="meaning">{entry.meaning_ru}</p>

        {entry.examples.length > 0 ? (
          <div className="examples-block">
            <p className="section-label">Examples</p>
            {entry.examples.map((example, index) => (
              <div className="example-item" key={`${entry.id}-full-${index}`}>
                <p>{example.en}</p>
                <p>{example.ru}</p>
              </div>
            ))}
          </div>
        ) : null}

        {entry.synonyms.length > 0 ? (
          <div className="synonyms-block">
            <p className="section-label">Synonyms</p>
            <p className="meaning">{entry.synonyms.join(", ")}</p>
          </div>
        ) : null}

        {entry.tags.length > 0 ? (
          <div className="tags-row">
            {entry.tags.map((tag) => (
              <span className="tag-chip" key={`${entry.id}-${tag}`}>
                {tag}
              </span>
            ))}
          </div>
        ) : null}

        <div className="ai-note">
          <input className="text-input" type="text" placeholder="Ask AI to explain this word deeper" />
          <button className="secondary-button" type="button" disabled>
            Ask AI (coming soon)
          </button>
        </div>
      </div>
    </div>
  );
}

export default EntryDetailsModal;
