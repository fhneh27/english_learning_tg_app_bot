import Badge from "./Badge";
import Button from "./Button";
import Card from "./Card";
import { VocabularyAnalysis, VocabularyAnalysisMode, VocabularySourceType } from "../types/vocabulary";
import { formatAnalysisModeLabel, formatSourceLabel } from "../utils/vocabulary";

type DestinationOption = {
  description: string;
  disabled?: boolean;
  value: VocabularySourceType;
};

type ResultCardProps = {
  aiModel: string | null;
  analysis: VocabularyAnalysis;
  analysisMode: VocabularyAnalysisMode;
  destinationOptions: DestinationOption[];
  isSaveDisabled?: boolean;
  isSaving: boolean;
  onDestinationChange: (value: VocabularySourceType) => void;
  onSave: () => Promise<void>;
  saveHint?: string | null;
  selectedDestination: VocabularySourceType;
};

function ResultCard({
  aiModel,
  analysis,
  analysisMode,
  destinationOptions,
  isSaveDisabled = false,
  isSaving,
  onDestinationChange,
  onSave,
  saveHint = null,
  selectedDestination,
}: ResultCardProps) {
  return (
    <Card className="result-card">
      <div className="result-card-top">
        <div>
          <p className="page-eyebrow">AI Result</p>
          <h2>{analysis.original_text}</h2>
        </div>
        <div className="result-card-badges">
          <Badge tone="neutral">{formatAnalysisModeLabel(analysisMode)}</Badge>
          {aiModel ? <Badge tone="neutral">{aiModel}</Badge> : null}
        </div>
      </div>

      <p className="word-card-translation">{analysis.translation_ru}</p>
      <p className="word-card-meaning">{analysis.meaning_ru}</p>

      <div className="result-card-grid">
        <div>
          <p className="section-title">Basics</p>
          <p className="detail-line">Normalized: {analysis.normalized_text}</p>
          <p className="detail-line">Part of speech: {analysis.part_of_speech || "phrase"}</p>
          <p className="detail-line">Level: {analysis.level || "n/a"}</p>
          <p className="detail-line">Transcription: {analysis.transcription || "n/a"}</p>
        </div>
        <div>
          <p className="section-title">Examples</p>
          {analysis.examples.length > 0 ? (
            <div className="result-examples">
              {analysis.examples.slice(0, 2).map((example, index) => (
                <div className="result-example" key={`${analysis.normalized_text}-${index}`}>
                  <p>{example.en}</p>
                  <p>{example.ru}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="detail-line">No examples generated.</p>
          )}
        </div>
      </div>

      <div className="destination-selector">
        <div className="destination-selector-head">
          <p className="section-title">Save destination</p>
          <Badge tone="source">{formatSourceLabel(selectedDestination)}</Badge>
        </div>
        <div className="destination-grid">
          {destinationOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              className={
                option.value === selectedDestination
                  ? "destination-option active"
                  : option.disabled
                    ? "destination-option disabled"
                    : "destination-option"
              }
              onClick={() => {
                if (!option.disabled) {
                  onDestinationChange(option.value);
                }
              }}
              disabled={option.disabled}
            >
              <strong>{formatSourceLabel(option.value)}</strong>
              <span>{option.description}</span>
              {option.disabled ? <em>Coming soon</em> : null}
            </button>
          ))}
        </div>
      </div>

      <div className="result-card-actions">
        <Button type="button" isLoading={isSaving} disabled={isSaveDisabled} onClick={() => void onSave()}>
          Save Word
        </Button>
      </div>
      {saveHint ? <p className="detail-line">{saveHint}</p> : null}
    </Card>
  );
}

export default ResultCard;
