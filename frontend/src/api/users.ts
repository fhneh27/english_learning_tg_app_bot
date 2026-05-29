import { apiRequest } from "./client";
import { RegisterUserPayload } from "../types/vocabulary";
import { DailyVocabularySuggestion, StreakSummary, SuggestionBlacklistResponse } from "../types/user";

export function registerUser(payload: RegisterUserPayload): Promise<void> {
  return apiRequest<void>("/users/register", {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not register user.",
  });
}

export function fetchUserStreak(tgUserId: number): Promise<StreakSummary> {
  return apiRequest<StreakSummary>(`/users/streak?tg_user_id=${tgUserId}`, {
    method: "GET",
    errorMessage: "Could not load streak data.",
  });
}

export function fetchDailyVocabularySuggestions(tgUserId: number): Promise<DailyVocabularySuggestion> {
  return apiRequest<DailyVocabularySuggestion>(`/users/streak/suggestions?tg_user_id=${tgUserId}`, {
    method: "GET",
    errorMessage: "Could not generate today's vocabulary suggestions.",
  });
}

export function blacklistVocabularySuggestion(
  tgUserId: number,
  text: string,
): Promise<SuggestionBlacklistResponse> {
  return apiRequest<SuggestionBlacklistResponse>("/users/streak/suggestions/blacklist", {
    method: "POST",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      text,
    }),
    errorMessage: "Could not blacklist this suggestion.",
  });
}
