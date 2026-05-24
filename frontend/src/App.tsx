import { FormEvent, startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";

import { registerUser } from "./api/users";
import {
  createVocabularyEntry,
  deleteVocabularyEntry,
  fetchVocabularyEntries,
  updateVocabularyProgress,
} from "./api/vocabulary";
import EntryForm from "./components/EntryForm";
import EntryDetailsModal from "./components/EntryDetailsModal";
import EntryList from "./components/EntryList";
import { VocabularyEntry, VocabularyStatus } from "./types/vocabulary";

const DEFAULT_DEV_TG_USER_ID = 123456789;
const STORAGE_TG_USER_KEY = "telegram_mini_app_tg_user";
const STATUS_FILTERS: Array<"all" | VocabularyStatus> = ["all", "learning", "learned"];

function App() {
  const [entries, setEntries] = useState<VocabularyEntry[]>([]);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | VocabularyStatus>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [tgUser, setTgUser] = useState(() => getTelegramUser());
  const deferredStatusFilter = useDeferredValue(statusFilter);
  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.id === selectedEntryId) ?? null,
    [entries, selectedEntryId]
  );
  const tgUserId = tgUser.id;

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }

    const syncTelegramUser = () => {
      const nextUser = getTelegramUser();
      setTgUser((currentUser) => {
        if (
          currentUser.id === nextUser.id &&
          currentUser.username === nextUser.username &&
          currentUser.firstName === nextUser.firstName
        ) {
          return currentUser;
        }
        return nextUser;
      });
    };

    syncTelegramUser();
    const delayedSync = window.setTimeout(syncTelegramUser, 300);
    return () => window.clearTimeout(delayedSync);
  }, []);

  useEffect(() => {
    void registerUser({
      tg_user_id: tgUser.id,
      username: tgUser.username,
      first_name: tgUser.firstName,
    }).catch(() => {
      // Registration is best-effort and must not block the UI.
    });
  }, [tgUser.firstName, tgUser.id, tgUser.username]);

  useEffect(() => {
    void loadEntries();
  }, [deferredStatusFilter, tgUserId]);

  async function loadEntries() {
    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchVocabularyEntries({
        tgUserId,
        q: query.trim() || undefined,
        status: deferredStatusFilter === "all" ? undefined : deferredStatusFilter,
      });
      setEntries(data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateEntry(text: string) {
    setIsSubmitting(true);
    setError(null);

    try {
      await createVocabularyEntry({ tg_user_id: tgUserId, text });
      await loadEntries();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleIncreaseRepeat(entryId: string) {
    setError(null);

    try {
      const updatedEntry = await updateVocabularyProgress(entryId, tgUserId, {
        increment_repetition: true,
      });
      setEntries((currentEntries) =>
        currentEntries.map((entry) => (entry.id === entryId ? updatedEntry : entry))
      );
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    }
  }

  async function handleMarkLearned(entryId: string) {
    setError(null);

    try {
      const updatedEntry = await updateVocabularyProgress(entryId, tgUserId, {
        status: "learned",
      });
      if (statusFilter === "learning" && selectedEntryId === entryId) {
        setSelectedEntryId(null);
      }
      setEntries((currentEntries) => {
        if (statusFilter === "learning") {
          return currentEntries.filter((entry) => entry.id !== entryId);
        }
        return currentEntries.map((entry) => (entry.id === entryId ? updatedEntry : entry));
      });
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    }
  }

  async function handleDeleteEntry(entryId: string) {
    setError(null);

    try {
      await deleteVocabularyEntry(entryId, tgUserId);
      setEntries((currentEntries) => currentEntries.filter((entry) => entry.id !== entryId));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    }
  }

  function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void loadEntries();
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <h1>Vocabulary</h1>
        <div className="hero-meta">
          <span>ID {tgUserId}</span>
          <span>OpenAI</span>
        </div>
      </section>

      <EntryForm isSubmitting={isSubmitting} onSubmit={handleCreateEntry} />

      <section className="panel">
        <form className="search-row" onSubmit={handleSearchSubmit}>
          <input
            className="text-input"
            type="search"
            placeholder="Search by word or Russian meaning"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button className="secondary-button" type="submit">
            Search
          </button>
        </form>

        <div className="status-filter-row">
          {STATUS_FILTERS.map((filterValue) => (
            <button
              key={filterValue}
              type="button"
              className={filterValue === statusFilter ? "filter-chip active" : "filter-chip"}
              onClick={() => {
                startTransition(() => {
                  setStatusFilter(filterValue);
                });
              }}
            >
              {formatStatusLabel(filterValue)}
            </button>
          ))}
        </div>

        <div className="entries-area">
          {error ? <p className="state-message error">{error}</p> : null}
          <EntryList
            entries={entries}
            isLoading={isLoading}
            onDelete={handleDeleteEntry}
            onIncreaseRepeat={handleIncreaseRepeat}
            onMarkLearned={handleMarkLearned}
            onOpenDetails={setSelectedEntryId}
          />
        </div>
      </section>

      {selectedEntry ? (
        <EntryDetailsModal
          entry={selectedEntry}
          onClose={() => {
            setSelectedEntryId(null);
          }}
        />
      ) : null}
    </main>
  );
}

function getTelegramUser(): { id: number; username?: string; firstName?: string } {
  const user = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const envDevUserId = Number(import.meta.env.VITE_DEV_TG_USER_ID || DEFAULT_DEV_TG_USER_ID);
  const storedUserId = Number(window.localStorage.getItem(STORAGE_TG_USER_KEY) || "");
  const fallbackUserId = Number.isFinite(storedUserId) && storedUserId > 0 ? storedUserId : envDevUserId;

  if (user?.id) {
    window.localStorage.setItem(STORAGE_TG_USER_KEY, String(user.id));
  }

  return {
    id: user?.id ?? fallbackUserId,
    username: user?.username,
    firstName: user?.first_name,
  };
}

function formatStatusLabel(status: "all" | VocabularyStatus): string {
  if (status === "all") {
    return "All";
  }

  return status.charAt(0).toUpperCase() + status.slice(1);
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

export default App;
