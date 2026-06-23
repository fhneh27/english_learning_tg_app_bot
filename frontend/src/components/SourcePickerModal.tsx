import { ChangeEvent, useRef } from "react";
import { createPortal } from "react-dom";

import Button from "./Button";
import Card from "./Card";
import Input from "./Input";
import { useBodyScrollLock } from "../hooks/useBodyScrollLock";
import { useGsapModal } from "../hooks/useGsapMotion";
import { MediaCard, MediaSearchFilter, MediaSearchItem } from "../types/media";
import { MusicTrackSearchItem } from "../types/music";

type SourcePickerMode = "media" | "music";

type SourcePickerModalProps = {
  mediaError: string | null;
  mediaFilter: MediaSearchFilter;
  mediaLibraryItems: MediaCard[];
  mediaQuery: string;
  mediaResults: MediaSearchItem[];
  mode: SourcePickerMode;
  musicError: string | null;
  musicQuery: string;
  musicResults: MusicTrackSearchItem[];
  onApply: () => void;
  onClose: () => void;
  onMediaFilterChange: (value: MediaSearchFilter) => void;
  onMediaQueryChange: (value: string) => void;
  onMediaSearch: () => void;
  onMusicQueryChange: (value: string) => void;
  onMusicSearch: () => void;
  onSelectLibraryMedia: (item: MediaCard) => void;
  onSelectMediaResult: (item: MediaSearchItem) => void;
  onSelectMusicTrack: (track: MusicTrackSearchItem) => void;
  selectedMedia: MediaCard | null;
  selectedMusicTrack: MusicTrackSearchItem | null;
  isApplying: boolean;
  isMediaSearching: boolean;
  isMusicSearching: boolean;
};

const MEDIA_FILTERS: Array<{ label: string; value: MediaSearchFilter }> = [
  { label: "All", value: "all" },
  { label: "Movies", value: "movie" },
  { label: "Series", value: "series" },
];

function SourcePickerModal({
  mediaError,
  mediaFilter,
  mediaLibraryItems,
  mediaQuery,
  mediaResults,
  mode,
  musicError,
  musicQuery,
  musicResults,
  onApply,
  onClose,
  onMediaFilterChange,
  onMediaQueryChange,
  onMediaSearch,
  onMusicQueryChange,
  onMusicSearch,
  onSelectLibraryMedia,
  onSelectMediaResult,
  onSelectMusicTrack,
  selectedMedia,
  selectedMusicTrack,
  isApplying,
  isMediaSearching,
  isMusicSearching,
}: SourcePickerModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const isMedia = mode === "media";
  const canApply = isMedia ? Boolean(selectedMedia) : Boolean(selectedMusicTrack);

  useGsapModal(modalRef, [mode]);
  useBodyScrollLock(true);

  return createPortal(
    <div className="source-picker-overlay" role="dialog" aria-modal="true" onClick={onClose} ref={modalRef}>
      <Card className="source-picker-modal" onClick={(event) => event.stopPropagation()}>
        <div className="source-picker-header">
          <div>
            <p className="section-title">{isMedia ? "Media source" : "Music source"}</p>
            <h2>{isMedia ? "Choose movie or series" : "Choose song"}</h2>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        {isMedia ? (
          <div className="source-picker-body">
            <Input
              type="search"
              label="Search TMDB"
              placeholder="Dexter, Spider-Man, Interstellar"
              value={mediaQuery}
              onChange={(event: ChangeEvent<HTMLInputElement>) => onMediaQueryChange(event.target.value)}
            />
            <div className="filter-row">
              {MEDIA_FILTERS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={option.value === mediaFilter ? "filter-chip active" : "filter-chip"}
                  onClick={() => onMediaFilterChange(option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <Button type="button" isLoading={isMediaSearching} onClick={onMediaSearch}>
              Search media
            </Button>
            {mediaError ? <p className="feedback-message error">{mediaError}</p> : null}

            {mediaResults.length > 0 ? (
              <div className="source-picker-list">
                {mediaResults.map((item) => (
                  <button
                    key={`${item.media_type}-${item.tmdb_id}`}
                    type="button"
                    className="source-picker-row"
                    onClick={() => onSelectMediaResult(item)}
                  >
                    <MediaPoster path={item.poster_path} title={item.title} />
                    <span>
                      <strong>{item.title}</strong>
                      <small>
                        {item.year || "Year n/a"} - {item.media_type === "movie" ? "Movie" : "Series"}
                        {item.is_in_library ? " - in library" : ""}
                      </small>
                    </span>
                  </button>
                ))}
              </div>
            ) : null}

            {mediaLibraryItems.length > 0 ? (
              <div className="source-picker-section">
                <p className="section-title">My library</p>
                <div className="source-picker-list">
                  {mediaLibraryItems.slice(0, 8).map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className="source-picker-row"
                      onClick={() => onSelectLibraryMedia(item)}
                    >
                      <MediaPoster path={item.poster_path} title={item.title} />
                      <span>
                        <strong>{item.title}</strong>
                        <small>
                          {item.year || "Year n/a"} - {item.media_type === "movie" ? "Movie" : "Series"}
                        </small>
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            {selectedMedia ? <SelectedSource label={selectedMedia.title} meta="Selected media source" /> : null}
          </div>
        ) : (
          <div className="source-picker-body">
            <Input
              type="search"
              label="Search song"
              placeholder="Starboy, Arctic Monkeys 505, Die With A Smile"
              value={musicQuery}
              onChange={(event: ChangeEvent<HTMLInputElement>) => onMusicQueryChange(event.target.value)}
            />
            <Button type="button" isLoading={isMusicSearching} onClick={onMusicSearch}>
              Search song
            </Button>
            {musicError ? <p className="feedback-message error">{musicError}</p> : null}

            {musicResults.length > 0 ? (
              <div className="source-picker-list">
                {musicResults.map((track) => (
                  <button
                    key={`${track.external_id}-${track.release_external_id ?? "release"}`}
                    type="button"
                    className="source-picker-row"
                    onClick={() => onSelectMusicTrack(track)}
                  >
                    <MusicArtwork title={track.title} artworkUrl={track.artwork_url} />
                    <span>
                      <strong>{track.title}</strong>
                      <small>
                        {track.artist_name}
                        {track.release_year ? ` - ${track.release_year}` : ""}
                      </small>
                    </span>
                  </button>
                ))}
              </div>
            ) : null}

            {selectedMusicTrack ? (
              <SelectedSource
                label={selectedMusicTrack.title}
                meta={`${selectedMusicTrack.artist_name}${selectedMusicTrack.release_year ? ` - ${selectedMusicTrack.release_year}` : ""}`}
              />
            ) : null}
          </div>
        )}

        <div className="source-picker-actions">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="button" isLoading={isApplying} disabled={!canApply} onClick={onApply}>
            Apply source
          </Button>
        </div>
      </Card>
    </div>,
    document.body,
  );
}

function SelectedSource({ label, meta }: { label: string; meta: string }) {
  return (
    <div className="source-picker-selected">
      <span>Selected</span>
      <strong>{label}</strong>
      <small>{meta}</small>
    </div>
  );
}

function MediaPoster({ path, title }: { path: string | null; title: string }) {
  if (!path) {
    return <div className="source-picker-thumb source-picker-thumb-placeholder">{title.slice(0, 1).toUpperCase()}</div>;
  }

  return (
    <img
      className="source-picker-thumb"
      src={`https://image.tmdb.org/t/p/w500${path}`}
      alt={title}
      loading="lazy"
    />
  );
}

function MusicArtwork({ title, artworkUrl }: { title: string; artworkUrl: string | null }) {
  if (!artworkUrl) {
    return <div className="source-picker-thumb source-picker-thumb-placeholder">{title.slice(0, 1).toUpperCase()}</div>;
  }

  return <img className="source-picker-thumb" src={artworkUrl} alt={title} loading="lazy" />;
}

export default SourcePickerModal;
