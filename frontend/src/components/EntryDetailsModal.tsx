import { ChangeEvent, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { requestVocabularyFollowUp } from "../api/vocabulary";
import { useBodyScrollLock } from "../hooks/useBodyScrollLock";
import Badge from "./Badge";
import Button from "./Button";
import Card from "./Card";
import Input from "./Input";
import LoadingState from "./LoadingState";
import { useGsapModal } from "../hooks/useGsapMotion";
import { VocabularyEntry, VocabularyFollowUpResponse } from "../types/vocabulary";
import { formatAnalysisModeLabel, formatSourceLabel, formatStatusLabel } from "../utils/vocabulary";

type EntryDetailsModalProps = {
  entry: VocabularyEntry;
  onClose: () => void;
  onFollowUpComplete: () => void;
  tgUserId: number;
};

const PROMPT_SUGGESTIONS = [
  "Explain this word in simpler Russian.",
  "Give me 3 more natural examples.",
  "When does this sound natural in real conversation?",
];

function EntryDetailsModal({ entry, onClose, onFollowUpComplete, tgUserId }: EntryDetailsModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const [prompt, setPrompt] = useState("");
  const [followUp, setFollowUp] = useState<VocabularyFollowUpResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useBodyScrollLock(true);

  async function handleAskAI() {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt) {
      setError("Type a question for AI first.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setFollowUp(null);

    try {
      const response = await requestVocabularyFollowUp(entry.id, tgUserId, { prompt: trimmedPrompt });
      setFollowUp(response);
      onFollowUpComplete();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not get an AI explanation.");
    } finally {
      setIsLoading(false);
    }
  }

  function handlePromptChange(event: ChangeEvent<HTMLInputElement>) {
    setPrompt(event.target.value);
  }

  useGsapModal(modalRef, [entry.id]);

  return createPortal(
    <div className="entry-modal-overlay" role="dialog" aria-modal="true" onClick={onClose} ref={modalRef}>
      <Card className="entry-modal" onClick={(event) => event.stopPropagation()}>
        <div className="entry-modal-header">
          <div>
            <h2>{entry.original_text}</h2>
            <div className="entry-modal-badges">
              <Badge tone={entry.status === "learned" ? "success" : "status"}>
                {formatStatusLabel(entry.status)}
              </Badge>
              <Badge tone="source">{formatSourceLabel(entry.source_type)}</Badge>
              <Badge tone="neutral">{formatAnalysisModeLabel(entry.analysis_mode)}</Badge>
            </div>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <div className="entry-modal-body">
          <p className="word-card-translation">{entry.translation_ru}</p>
          <p className="word-card-meaning">{entry.meaning_ru}</p>
          {entry.source_label || entry.source_image_url ? (
            <div className="entry-source-block">
              {entry.source_image_url ? (
                <img
                  className="source-artwork-thumb source-artwork-thumb-large"
                  src={entry.source_image_url}
                  alt={entry.source_label || entry.original_text}
                  loading="lazy"
                />
              ) : null}
              <div className="entry-source-copy">
                <p className="section-title" style={{ margin: 0 }}>
                  Source
                </p>
                <p className="detail-line">{entry.source_label || formatSourceLabel(entry.source_type)}</p>
              </div>
            </div>
          ) : null}
          <div className="entry-detail-grid">
            <p className="detail-line">Normalized: {entry.normalized_text}</p>
            <p className="detail-line">Part of speech: {entry.part_of_speech || "phrase"}</p>
            <p className="detail-line">Level: {entry.level || "n/a"}</p>
            <p className="detail-line">Transcription: {entry.transcription || "n/a"}</p>
            <p className="detail-line">Reviews: {entry.repeat_count}</p>
          </div>

          {entry.examples.length > 0 ? (
            <div className="examples-block">
              <p className="section-title">Examples</p>
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
              <p className="section-title">Synonyms</p>
              <p className="word-card-meaning">{entry.synonyms.join(", ")}</p>
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
            <div className="ai-note-header">
              <div>
                <p className="section-title">Ask AI deeper</p>
                <p className="detail-line">Ask for nuance, more examples, tone, or a simpler explanation.</p>
              </div>
            </div>

            <div className="prompt-suggestions">
              {PROMPT_SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="prompt-chip"
                  onClick={() => setPrompt(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>

            <Input
              type="text"
              placeholder="For example: explain the slang nuance, give 3 more examples, or compare it with a similar phrase"
              value={prompt}
              onChange={handlePromptChange}
            />
            <Button className="modal-action" type="button" variant="secondary" isLoading={isLoading} onClick={() => void handleAskAI()}>
              Ask AI
            </Button>

            {error ? <p className="feedback-message error">{error}</p> : null}
            {isLoading ? <LoadingState message="AI is preparing a deeper explanation..." /> : null}

            {followUp ? (
              <div className="follow-up-card">
                <div className="result-card-badges">
                  <Badge tone="neutral">{followUp.follow_up_model || "Gemini"}</Badge>
                </div>
                <p className="follow-up-answer">{followUp.answer_ru}</p>

                {followUp.usage_notes_ru.length > 0 ? (
                  <div className="follow-up-section">
                    <p className="section-title">Usage notes</p>
                    <ul className="follow-up-list">
                      {followUp.usage_notes_ru.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {followUp.mistakes_ru.length > 0 ? (
                  <div className="follow-up-section">
                    <p className="section-title">Watch out</p>
                    <ul className="follow-up-list">
                      {followUp.mistakes_ru.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {followUp.extra_examples.length > 0 ? (
                  <div className="follow-up-section">
                    <p className="section-title">Extra examples</p>
                    <div className="examples-block">
                      {followUp.extra_examples.map((example, index) => (
                        <div className="example-item" key={`${entry.id}-follow-up-${index}`}>
                          <p>{example.en}</p>
                          <p>{example.ru}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>
      </Card>
    </div>,
    document.body,
  );
}

export default EntryDetailsModal;
