import { CSSProperties, useRef } from "react";

import Button from "../components/Button";
import Card from "../components/Card";
import EmptyState from "../components/EmptyState";
import LoadingState from "../components/LoadingState";
import StreakTierMark from "../components/StreakTierMark";
import { useGsapProgress } from "../hooks/useGsapMotion";
import {
  DailyVocabularySuggestion,
  DailyVocabularySuggestionItem,
  StreakDay,
  StreakSummary,
} from "../types/user";
import { getDailyGoalsProgress, getStreakVisualTier, StreakVisualTier } from "../utils/streak";

type StreakPageProps = {
  streak: StreakSummary | null;
  isLoading: boolean;
  isSuggestionLoading: boolean;
  onGoHome: () => void;
  onSuggestWords: () => void;
  onSaveSuggestion: (item: DailyVocabularySuggestionItem) => void;
  onBlacklistSuggestion: (item: DailyVocabularySuggestionItem) => void;
  suggestion: DailyVocabularySuggestion | null;
  suggestionError: string | null;
  savingSuggestionText: string | null;
  blacklistingSuggestionText: string | null;
  savedSuggestionTexts: string[];
  blacklistedSuggestionTexts: string[];
};

type AccentVariant = "fire" | "gold" | "purple" | "green" | "diamond";

function getTodayStr(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

function getDayLabel(dateStr: string): string {
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en", { weekday: "short" });
}

function build7DayWindow(last14: StreakDay[]): Array<StreakDay | null> {
  const last7 = last14.slice(-7);
  return [...Array<null>(Math.max(0, 7 - last7.length)).fill(null), ...last7];
}

function tierLabel(tier: StreakVisualTier): string {
  if (tier === "diamond") {
    return "Diamond streak";
  }
  if (tier === "ember") {
    return "Fire streak";
  }
  return "Start a streak";
}

function StatCard({
  value,
  label,
  unit,
  variant,
}: {
  value: number | string;
  label: string;
  unit?: string;
  variant: AccentVariant;
}) {
  return (
    <Card className={`streak-stat-card streak-stat-card-${variant}`}>
      <div className={`streak-stat-value streak-stat-value-${variant}`}>
        {value}
        {unit ? <span className="streak-stat-unit">{unit}</span> : null}
      </div>
      <div className="streak-stat-label">{label}</div>
    </Card>
  );
}

function StreakHero({ streak }: { streak: StreakSummary }) {
  const tier = getStreakVisualTier(streak);
  const isActiveToday = streak.today_actions > 0;
  const heroCount = tier === "diamond" ? streak.elite_current_streak_days : streak.current_streak_days;
  const heroUnit =
    heroCount === 1
      ? tier === "diamond"
        ? "diamond day"
        : "day streak"
      : tier === "diamond"
        ? "diamond days"
        : "days streak";

  return (
    <section
      className={`card streak-hero-card streak-hero-card--${tier}`}
      aria-label={`${tierLabel(tier)} hero`}
    >
      <div className="streak-hero-inner">
        <div className="streak-flame-container">
          <StreakTierMark tier={tier} className="streak-hero-tier-mark" />
        </div>

        <div className="streak-hero-count-block">
          <p className="streak-hero-tier-label">{tierLabel(tier)}</p>
          <div className="streak-hero-number">{heroCount}</div>
          <span className="streak-hero-unit">{heroUnit}</span>
        </div>

        <p className="streak-hero-message">
          {tier === "diamond"
            ? "Both daily goals completed on consecutive days. Keep the diamond chain alive."
            : tier === "ember"
              ? isActiveToday
                ? `You showed up today with ${streak.today_actions} action${streak.today_actions === 1 ? "" : "s"}.`
                : "Your fire streak is active. One move today keeps it burning."
              : isActiveToday
                ? "You started today. Complete both daily goals to unlock a diamond streak."
                : "Add words or mark progress today to start your streak."}
        </p>

        <div className="streak-hero-meta-row">
          {tier === "diamond" ? (
            <span className="streak-hero-chip streak-hero-chip-fire">
              Fire streak: {streak.current_streak_days}d
            </span>
          ) : null}
          {tier !== "none" && streak.elite_today_complete ? (
            <span className="streak-hero-chip streak-hero-chip-diamond">Goals done today</span>
          ) : null}
          {isActiveToday && !streak.elite_today_complete ? (
            <span className="streak-hero-chip streak-hero-chip-neutral">Active today</span>
          ) : null}
          {!isActiveToday && tier !== "none" ? (
            <span className="streak-hero-chip streak-hero-chip-neutral">Today is still open</span>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function EliteStreakCard({ streak }: { streak: StreakSummary }) {
  const progress = getDailyGoalsProgress(streak);
  const isDiamondActive = streak.elite_current_streak_days > 0;
  const cardClass = [
    "streak-diamond-card",
    isDiamondActive ? "streak-diamond-card--active" : "",
    streak.elite_today_complete ? "streak-diamond-card--today-complete" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <Card className={cardClass}>
      <div className="streak-diamond-shine" aria-hidden="true" />

      <div className="streak-diamond-top">
        <div>
          <p className="section-title streak-diamond-eyebrow">Diamond streak</p>
          <h3 className="streak-diamond-title">Full daily goals streak</h3>
          <p className="detail-line streak-diamond-subtitle">
            Add {streak.daily_add_goal} words and mark {streak.daily_learn_goal} as learned in one day.
          </p>
        </div>
        <span
          className={
            streak.elite_today_complete ? "streak-diamond-badge streak-diamond-badge--live" : "streak-diamond-badge"
          }
        >
          {streak.elite_today_complete ? "Diamond day secured" : "Goals in progress"}
        </span>
      </div>

      <div className="streak-diamond-progress-ring" style={{ "--progress": `${progress.combinedPct}%` } as CSSProperties}>
        <div className="streak-diamond-progress-inner">
          <StreakTierMark tier={isDiamondActive ? "diamond" : "none"} className="streak-diamond-progress-icon" />
          <strong>{streak.elite_current_streak_days}</strong>
          <span>current</span>
        </div>
      </div>

      <div className="streak-diamond-grid">
        <div className="streak-diamond-metric">
          <strong>{streak.elite_current_streak_days}</strong>
          <span>current diamond</span>
        </div>
        <div className="streak-diamond-metric">
          <strong>{streak.elite_best_streak_days}</strong>
          <span>personal best</span>
        </div>
      </div>

      <div className="streak-diamond-goals-preview">
        <div className="streak-diamond-goal-line">
          <span>Added today</span>
          <strong>
            {streak.words_added_today}/{streak.daily_add_goal}
          </strong>
        </div>
        <div className="streak-diamond-goal-track">
          <div className="streak-diamond-goal-fill streak-diamond-goal-fill-add" style={{ width: `${progress.addPct}%` } as CSSProperties} />
        </div>
        <div className="streak-diamond-goal-line">
          <span>Learned today</span>
          <strong>
            {streak.words_learned_today}/{streak.daily_learn_goal}
          </strong>
        </div>
        <div className="streak-diamond-goal-track">
          <div
            className="streak-diamond-goal-fill streak-diamond-goal-fill-learn"
            style={{ width: `${progress.learnPct}%` } as CSSProperties}
          />
        </div>
      </div>
    </Card>
  );
}

function WeeklyCalendar({ last14 }: { last14: StreakDay[] }) {
  const today = getTodayStr();
  const days = build7DayWindow(last14);
  const activeDays = last14.slice(-7).filter((day) => day.is_active).length;
  const diamondDays = last14.slice(-7).filter((day) => day.is_elite).length;

  return (
    <Card className="streak-week-card">
      <div className="streak-week-header">
        <div>
          <p className="section-title" style={{ margin: 0 }}>
            Last 7 days
          </p>
          <p className="detail-line streak-week-legend">
            <span className="streak-week-legend-item streak-week-legend-fire">Fire day</span>
            <span className="streak-week-legend-item streak-week-legend-diamond">Diamond day</span>
          </p>
        </div>
        <span className="streak-week-meta">
          {activeDays}/7 fire · {diamondDays}/7 diamond
        </span>
      </div>
      <div className="streak-week-grid">
        {days.map((day, index) => {
          if (!day) {
            return (
              <div key={`pad-${index}`} className="streak-week-day">
                <span className="streak-week-day-label">&nbsp;</span>
                <div className="streak-week-dot empty" />
              </div>
            );
          }

          const isToday = day.date === today;
          const dotClass = [
            "streak-week-dot",
            day.is_elite ? "diamond" : day.is_active ? "active" : "",
            isToday ? "today" : "",
          ]
            .filter(Boolean)
            .join(" ");

          return (
            <div key={day.date} className="streak-week-day">
              <span className="streak-week-day-label">{getDayLabel(day.date)}</span>
              <div className={dotClass} title={`${day.date}: ${day.action_count} actions`}>
                {day.is_elite ? "◆" : day.is_active ? "●" : isToday ? "·" : ""}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function DailyGoalsCard({ streak }: { streak: StreakSummary }) {
  const progress = getDailyGoalsProgress(streak);
  const addPct = progress.addPct;
  const learnPct = progress.learnPct;

  return (
    <Card className={`streak-progress-card${streak.elite_today_complete ? " streak-progress-card--diamond-ready" : ""}`}>
      <div className="streak-progress-header">
        <div>
          <p className="section-title" style={{ margin: 0 }}>
            Daily goals
          </p>
          <p className="detail-line" style={{ marginTop: 4 }}>
            Complete both goals to earn a diamond day and grow your diamond streak.
          </p>
        </div>
        {streak.elite_today_complete ? (
          <span className="streak-diamond-badge streak-diamond-badge--live">Diamond ready</span>
        ) : null}
      </div>

      <div className="daily-goal-block">
        <div className="daily-goal-head">
          <strong>Added today</strong>
          <span>
            {streak.words_added_today} of {streak.daily_add_goal}
          </span>
        </div>
        <div className="streak-progress-bar-track">
          <div className="streak-progress-bar-fill streak-progress-bar-fill-add" style={{ width: `${addPct}%` } as CSSProperties} />
        </div>
        <p className="detail-line">
          {streak.remaining_add_goal > 0
            ? `${streak.remaining_add_goal} more to reach today's add goal.`
            : "Daily add goal completed."}
        </p>
      </div>

      <div className="daily-goal-block">
        <div className="daily-goal-head">
          <strong>Learned today</strong>
          <span>
            {streak.words_learned_today} of {streak.daily_learn_goal}
          </span>
        </div>
        <div className="streak-progress-bar-track">
          <div
            className="streak-progress-bar-fill streak-progress-bar-fill-learn"
            style={{ width: `${learnPct}%` } as CSSProperties}
          />
        </div>
        <p className="detail-line">
          {streak.remaining_learn_goal > 0
            ? `${streak.remaining_learn_goal} more to reach today's learned goal.`
            : "Daily learned goal completed."}
        </p>
      </div>
    </Card>
  );
}

function SuggestionsCard({
  suggestion,
  suggestionError,
  isSuggestionLoading,
  onSuggestWords,
  onSaveSuggestion,
  onBlacklistSuggestion,
  savingSuggestionText,
  blacklistingSuggestionText,
  savedSuggestionTexts,
  blacklistedSuggestionTexts,
}: {
  suggestion: DailyVocabularySuggestion | null;
  suggestionError: string | null;
  isSuggestionLoading: boolean;
  onSuggestWords: () => void;
  onSaveSuggestion: (item: DailyVocabularySuggestionItem) => void;
  onBlacklistSuggestion: (item: DailyVocabularySuggestionItem) => void;
  savingSuggestionText: string | null;
  blacklistingSuggestionText: string | null;
  savedSuggestionTexts: string[];
  blacklistedSuggestionTexts: string[];
}) {
  return (
    <Card className="streak-milestones-card">
      <div className="streak-progress-header">
        <div>
          <p className="section-title" style={{ margin: 0 }}>
            Smart suggestions
          </p>
          <p className="detail-line" style={{ marginTop: 4 }}>
            Ask AI for useful B2-C2 words, living phrases, conversational pieces, and modern slang. Tap “I already know this” to blacklist it forever.
          </p>
        </div>
        <div style={{ width: "min(100%, 220px)" }}>
          <Button type="button" isLoading={isSuggestionLoading} onClick={onSuggestWords}>
            Suggest words for today
          </Button>
        </div>
      </div>

      {suggestionError ? <p className="feedback-message error">{suggestionError}</p> : null}

      {suggestion ? (
        <div className="streak-suggestion-stack">
          <div className="result-card-badges">
            <span className="badge badge-neutral">
              {suggestion.remaining_new_words > 0
                ? `${suggestion.remaining_new_words} to add today`
                : "Daily add goal already reached"}
            </span>
            {suggestion.ai_model ? <span className="badge badge-neutral">{suggestion.ai_model}</span> : null}
          </div>
          <p className="detail-line">{suggestion.summary_ru}</p>
          <div className="streak-suggestion-list">
            {suggestion.suggestions.map((item) => (
              <div key={`${item.text}-${item.category}`} className="streak-suggestion-item">
                <div className="streak-suggestion-top">
                  <strong>{item.text}</strong>
                  <span className="badge badge-source">
                    {item.level} · {item.category}
                  </span>
                </div>
                <p className="detail-line">{item.reason_ru}</p>
                <p className="detail-line">{item.usage_hint_ru}</p>
                <div className="streak-suggestion-actions streak-suggestion-actions-grid">
                  <Button
                    type="button"
                    variant={savedSuggestionTexts.includes(item.text) ? "ghost" : "secondary"}
                    isLoading={savingSuggestionText === item.text}
                    disabled={savedSuggestionTexts.includes(item.text)}
                    onClick={() => onSaveSuggestion(item)}
                  >
                    {savedSuggestionTexts.includes(item.text) ? "Saved" : "Save suggestion"}
                  </Button>
                  <Button
                    type="button"
                    variant={blacklistedSuggestionTexts.includes(item.text) ? "ghost" : "ghost"}
                    isLoading={blacklistingSuggestionText === item.text}
                    disabled={blacklistedSuggestionTexts.includes(item.text)}
                    onClick={() => onBlacklistSuggestion(item)}
                  >
                    {blacklistedSuggestionTexts.includes(item.text) ? "Hidden forever" : "I already know this"}
                  </Button>
                </div>
              </div>
            ))}
          </div>
          {suggestion.suggestions.length === 0 ? (
            <p className="detail-line">
              Nothing left in this batch. Ask for a new set and AI will avoid everything you blacklisted.
            </p>
          ) : null}
        </div>
      ) : null}
    </Card>
  );
}

function StreakPage({
  streak,
  isLoading,
  isSuggestionLoading,
  onGoHome,
  onSuggestWords,
  onSaveSuggestion,
  onBlacklistSuggestion,
  suggestion,
  suggestionError,
  savingSuggestionText,
  blacklistingSuggestionText,
  savedSuggestionTexts,
  blacklistedSuggestionTexts,
}: StreakPageProps) {
  const pageRef = useRef<HTMLDivElement>(null);

  useGsapProgress(pageRef, [
    streak?.words_added_today,
    streak?.words_learned_today,
    streak?.elite_today_complete,
    streak?.elite_current_streak_days,
    suggestion?.suggestions.length,
  ]);

  if (isLoading) {
    return <LoadingState message="Loading your streak..." />;
  }

  if (!streak) {
    return (
      <EmptyState
        title="No streak data yet"
        description="Start adding words and watching content to see your stats here."
        action={
          <Button type="button" onClick={onGoHome}>
            Add first word
          </Button>
        }
      />
    );
  }

  const isEmpty = streak.current_streak_days === 0 && streak.total_words === 0;

  if (isEmpty) {
    return (
      <Card>
        <div className="streak-empty-hero">
          <h2 style={{ margin: 0 }}>Begin your journey</h2>
          <p className="detail-line">
            Add your first English word to start tracking your learning streak and achievements.
          </p>
          <div style={{ marginTop: 8, width: "min(100%, 220px)" }}>
            <Button type="button" onClick={onGoHome}>
              Add first word
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="streak-page" ref={pageRef}>
      <StreakHero streak={streak} />
      <EliteStreakCard streak={streak} />
      <WeeklyCalendar last14={streak.last_14_days} />

      <div className="streak-stats-grid">
        <StatCard value={streak.current_streak_days} unit="d" label="Fire streak" variant="fire" />
        <StatCard value={streak.elite_current_streak_days} unit="d" label="Diamond streak" variant="diamond" />
        <StatCard value={streak.total_words} label="Total words" variant="purple" />
        <StatCard value={streak.learned_words} label="Learned" variant="green" />
      </div>

      <DailyGoalsCard streak={streak} />
      <SuggestionsCard
        suggestion={suggestion}
        suggestionError={suggestionError}
        isSuggestionLoading={isSuggestionLoading}
        onSuggestWords={onSuggestWords}
        onSaveSuggestion={onSaveSuggestion}
        onBlacklistSuggestion={onBlacklistSuggestion}
        savingSuggestionText={savingSuggestionText}
        blacklistingSuggestionText={blacklistingSuggestionText}
        savedSuggestionTexts={savedSuggestionTexts}
        blacklistedSuggestionTexts={blacklistedSuggestionTexts}
      />
    </div>
  );
}

export default StreakPage;
