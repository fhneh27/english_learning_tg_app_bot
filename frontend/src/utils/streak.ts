import { StreakSummary } from "../types/user";

export type StreakVisualTier = "none" | "ember" | "diamond";

export function getStreakVisualTier(streak: StreakSummary | null): StreakVisualTier {
  if (!streak) {
    return "none";
  }

  if (streak.elite_current_streak_days > 0) {
    return "diamond";
  }

  if (streak.current_streak_days > 0) {
    return "ember";
  }

  return "none";
}

export function getNavStreakDisplay(streak: StreakSummary | null): {
  count: number;
  tier: StreakVisualTier;
} {
  const tier = getStreakVisualTier(streak);

  if (tier === "diamond") {
    return { count: streak?.elite_current_streak_days ?? 0, tier };
  }

  return { count: streak?.current_streak_days ?? 0, tier };
}

export function getDailyGoalsProgress(streak: StreakSummary): {
  addPct: number;
  learnPct: number;
  combinedPct: number;
  isComplete: boolean;
} {
  const addPct = Math.min(Math.round((streak.words_added_today / streak.daily_add_goal) * 100), 100);
  const learnPct = Math.min(Math.round((streak.words_learned_today / streak.daily_learn_goal) * 100), 100);
  const combinedPct = Math.round((addPct + learnPct) / 2);

  return {
    addPct,
    learnPct,
    combinedPct,
    isComplete: streak.elite_today_complete,
  };
}
