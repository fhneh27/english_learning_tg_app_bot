import { memo } from "react";

import Button from "./Button";
import Card from "./Card";
import { VocabularyEntry } from "../types/vocabulary";
import { formatSourceLabel, formatStatusLabel } from "../utils/vocabulary";

type WordCardProps = {
  entry: VocabularyEntry;
  onDelete: (entryId: string) => Promise<void>;
  onIncreaseRepeat: (entryId: string) => Promise<void>;
  onMarkLearned: (entryId: string) => Promise<void>;
  onOpenDetails: (entryId: string) => void;
};

const STATUS_BADGE_TONE: Record<
  VocabularyEntry["status"],
  "badge-status-new" | "badge-status-learning" | "badge-status-learned"
> = {
  new: "badge-status-new",
  learning: "badge-status-learning",
  learned: "badge-status-learned",
};

function WordCard({ entry, onDelete, onIncreaseRepeat, onMarkLearned, onOpenDetails }: WordCardProps) {
  const statusClass = `status-${entry.status}`;
  const hasSourceMedia = entry.source_label || entry.source_image_url;

  return (
    <Card as="article" className={`word-card ${statusClass}`}>
      <button type="button" className="word-card-main" onClick={() => onOpenDetails(entry.id)}>
        <div className="word-card-head">
          <div>
            <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 800 }}>{entry.original_text}</h3>
            {entry.transcription ? <p className="word-card-subtitle">{entry.transcription}</p> : null}
          </div>
          <div className="word-card-badges">
            <span className={`badge ${STATUS_BADGE_TONE[entry.status]}`}>{formatStatusLabel(entry.status)}</span>
            <span className="badge badge-source">{formatSourceLabel(entry.source_type)}</span>
          </div>
        </div>

        <p className="word-card-translation">{entry.translation_ru}</p>
        <p className="word-card-meaning">{entry.meaning_ru}</p>
        {hasSourceMedia ? (
          <div className="word-card-source-row">
            {entry.source_image_url ? (
              <img
                className="source-artwork-thumb"
                src={entry.source_image_url}
                alt={entry.source_label || entry.original_text}
                loading="lazy"
              />
            ) : null}
            <p className="word-card-source">Source: {entry.source_label || formatSourceLabel(entry.source_type)}</p>
          </div>
        ) : null}
        <div className="word-card-meta">
          <span>{entry.part_of_speech || "phrase"}</span>
          {entry.level ? <span>{entry.level}</span> : null}
          <span>Reviews: {entry.repeat_count}</span>
        </div>
      </button>

      <div className="word-card-actions">
        {entry.status !== "learned" ? (
          <>
            <Button type="button" variant="secondary" onClick={() => void onIncreaseRepeat(entry.id)}>
              +1 Review
            </Button>
            <Button type="button" variant="primary" onClick={() => void onMarkLearned(entry.id)}>
              Mark Learned
            </Button>
          </>
        ) : null}
        <Button type="button" variant="ghost" onClick={() => void onDelete(entry.id)}>
          Delete
        </Button>
      </div>
    </Card>
  );
}

export default memo(WordCard);
