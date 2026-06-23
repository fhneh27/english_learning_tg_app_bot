import { buildAuthHeaders } from "./auth";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

type RequestOptions = RequestInit & {
  errorMessage: string;
};

export async function apiRequest<T>(path: string, options: RequestOptions): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = options.errorMessage;

    try {
      const data = (await response.json()) as { detail?: string };
      if (response.status === 401) {
        detail = "Authentication failed. Reopen the Mini App from Telegram.";
      } else if (response.status === 403) {
        detail = "You are not allowed to perform this action.";
      } else if (response.status === 429) {
        detail = data.detail || "Too many requests. Please try again later.";
      } else if (data.detail) {
        detail = data.detail;
      }
    } catch {
      detail = options.errorMessage;
    }

    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
