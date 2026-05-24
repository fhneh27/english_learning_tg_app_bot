import { apiRequest } from "./client";
import {
  VocabularyCreatePayload,
  VocabularyEntry,
  VocabularyProgressPayload,
  VocabularyStatus,
} from "../types/vocabulary";

type FetchEntriesParams = {
  tgUserId: number;
  q?: string;
  status?: VocabularyStatus;
};

export function createVocabularyEntry(payload: VocabularyCreatePayload): Promise<VocabularyEntry> {
  return apiRequest<VocabularyEntry>("/vocabulary", {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not create the vocabulary entry.",
  });
}

export function fetchVocabularyEntries(params: FetchEntriesParams): Promise<VocabularyEntry[]> {
  const searchParams = new URLSearchParams({
    tg_user_id: String(params.tgUserId),
  });

  if (params.q) {
    searchParams.set("q", params.q);
  }

  if (params.status) {
    searchParams.set("status", params.status);
  }

  return apiRequest<VocabularyEntry[]>(`/vocabulary?${searchParams.toString()}`, {
    method: "GET",
    errorMessage: "Could not load vocabulary entries.",
  });
}

export function updateVocabularyProgress(
  entryId: string,
  tgUserId: number,
  payload: VocabularyProgressPayload
): Promise<VocabularyEntry> {
  return apiRequest<VocabularyEntry>(`/vocabulary/${entryId}?tg_user_id=${tgUserId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    errorMessage: "Could not update the entry progress.",
  });
}

export function deleteVocabularyEntry(entryId: string, tgUserId: number): Promise<void> {
  return apiRequest<void>(`/vocabulary/${entryId}?tg_user_id=${tgUserId}`, {
    method: "DELETE",
    errorMessage: "Could not delete the entry.",
  });
}
