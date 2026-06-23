import { apiRequest } from "./client";
import {
  VocabularyAnalysisResponse,
  VocabularyAnalyzePayload,
  VocabularyCreatePayload,
  VocabularyEntry,
  VocabularyFollowUpPayload,
  VocabularyFollowUpResponse,
  VocabularyProgressPayload,
  VocabularySavePayload,
  VocabularySourceType,
  VocabularyStatus,
} from "../types/vocabulary";

type FetchEntriesParams = {
  tgUserId: number;
  q?: string;
  status?: VocabularyStatus;
  sourceType?: VocabularySourceType;
};

export function createVocabularyEntry(payload: VocabularyCreatePayload): Promise<VocabularyEntry> {
  return apiRequest<VocabularyEntry>("/vocabulary", {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not create the vocabulary entry.",
  });
}

export function analyzeVocabularyEntry(
  payload: VocabularyAnalyzePayload
): Promise<VocabularyAnalysisResponse> {
  return apiRequest<VocabularyAnalysisResponse>("/vocabulary/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not analyze the vocabulary entry.",
  });
}

export function saveAnalyzedVocabularyEntry(payload: VocabularySavePayload): Promise<VocabularyEntry> {
  return apiRequest<VocabularyEntry>("/vocabulary/save", {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not save the analyzed vocabulary entry.",
  });
}

export function requestVocabularyFollowUp(
  entryId: string,
  tgUserId: number,
  payload: VocabularyFollowUpPayload
): Promise<VocabularyFollowUpResponse> {
  return apiRequest<VocabularyFollowUpResponse>(`/vocabulary/${entryId}/follow-up`, {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not get a deeper explanation for this entry.",
  });
}

export function fetchVocabularyEntries(params: FetchEntriesParams): Promise<VocabularyEntry[]> {
  const searchParams = new URLSearchParams();

  if (params.q) {
    searchParams.set("q", params.q);
  }

  if (params.status) {
    searchParams.set("status", params.status);
  }

  if (params.sourceType) {
    searchParams.set("source_type", params.sourceType);
  }

  const query = searchParams.toString();
  return apiRequest<VocabularyEntry[]>(`/vocabulary${query ? `?${query}` : ""}`, {
    method: "GET",
    errorMessage: "Could not load vocabulary entries.",
  });
}

export function updateVocabularyProgress(
  entryId: string,
  tgUserId: number,
  payload: VocabularyProgressPayload
): Promise<VocabularyEntry> {
  return apiRequest<VocabularyEntry>(`/vocabulary/${entryId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    errorMessage: "Could not update the entry progress.",
  });
}

export function deleteVocabularyEntry(entryId: string, tgUserId: number): Promise<void> {
  return apiRequest<void>(`/vocabulary/${entryId}`, {
    method: "DELETE",
    errorMessage: "Could not delete the entry.",
  });
}
