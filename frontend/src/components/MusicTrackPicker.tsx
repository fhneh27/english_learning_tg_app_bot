import { ChangeEvent } from "react";

import Button from "./Button";
import Card from "./Card";
import Input from "./Input";
import { MusicTrackSearchItem } from "../types/music";

type MusicTrackPickerProps = {
  error: string | null;
  isSearching: boolean;
  onClearSelection: () => void;
  onQueryChange: (value: string) => void;
  onSearch: () => void;
  onSelectTrack: (track: MusicTrackSearchItem) => void;
  query: string;
  results: MusicTrackSearchItem[];
  selectedTrack: MusicTrackSearchItem | null;
};

function formatDuration(durationMs: number | null): string | null {
  if (!durationMs || durationMs <= 0) {
    return null;
  }

  const totalSeconds = Math.round(durationMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function MusicArtwork({
  title,
  artworkUrl,
  className = "music-track-artwork",
}: {
  title: string;
  artworkUrl: string | null;
  className?: string;
}) {
  if (artworkUrl) {
    return <img className={className} src={artworkUrl} alt={title} loading="lazy" />;
  }

  return <div className={`${className} music-track-artwork-placeholder`}>{title.slice(0, 1).toUpperCase()}</div>;
}

function MusicTrackPicker({
  error,
  isSearching,
  onClearSelection,
  onQueryChange,
  onSearch,
  onSelectTrack,
  query,
  results,
  selectedTrack,
}: MusicTrackPickerProps) {
  return (
    <Card className="music-picker-card">
      <div className="music-picker-head">
        <div>
          <p className="section-title">Music source</p>
          <h3>Choose the song this word came from</h3>
          <p className="detail-line">
            Search tracks with the free MusicBrainz catalog, then save this word with the song attached.
          </p>
        </div>
      </div>

      {selectedTrack ? (
        <div className="music-selected-card">
          <MusicArtwork title={selectedTrack.title} artworkUrl={selectedTrack.artwork_url} />
          <div className="music-search-copy">
            <strong>{selectedTrack.title}</strong>
            <span>{selectedTrack.artist_name}</span>
            <small>
              {[selectedTrack.release_title, selectedTrack.release_year, formatDuration(selectedTrack.duration_ms)]
                .filter(Boolean)
                .join(" · ") || "Track selected"}
            </small>
          </div>
          <Button type="button" variant="ghost" onClick={onClearSelection}>
            Change
          </Button>
        </div>
      ) : null}

      <div className="music-search-form">
        <Input
          type="search"
          label="Song title or artist"
          placeholder="For example: Starboy, Arctic Monkeys, Die With A Smile"
          value={query}
          onChange={(event: ChangeEvent<HTMLInputElement>) => onQueryChange(event.target.value)}
        />
        <div className="music-search-actions">
          <Button type="button" isLoading={isSearching} onClick={onSearch}>
            Search song
          </Button>
        </div>
      </div>

      {error ? <p className="feedback-message error">{error}</p> : null}

      {results.length > 0 ? (
        <div className="music-search-results">
          {results.map((track) => (
            <button
              key={`${track.external_id}-${track.release_external_id ?? "release"}`}
              type="button"
              className="music-search-item"
              onClick={() => onSelectTrack(track)}
            >
              <MusicArtwork title={track.title} artworkUrl={track.artwork_url} />
              <div className="music-search-copy">
                <strong>{track.title}</strong>
                <span>{track.artist_name}</span>
                <small>
                  {[track.release_title, track.release_year, formatDuration(track.duration_ms)]
                    .filter(Boolean)
                    .join(" · ") || "Track result"}
                </small>
              </div>
              <span className="music-search-select">Pick</span>
            </button>
          ))}
        </div>
      ) : null}
    </Card>
  );
}

export default MusicTrackPicker;
