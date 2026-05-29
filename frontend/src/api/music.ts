import { apiRequest } from "./client";
import { MusicSearchResponse } from "../types/music";

export function searchMusicTracks(
  tgUserId: number,
  query: string,
  limit = 8,
): Promise<MusicSearchResponse> {
  return apiRequest<MusicSearchResponse>("/music/search", {
    method: "POST",
    body: JSON.stringify({
      tg_user_id: tgUserId,
      query,
      limit,
    }),
    errorMessage: "Could not search songs right now.",
  });
}
