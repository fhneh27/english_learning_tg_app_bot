let authTgUserId: number | null = null;

export function setApiAuthContext(tgUserId: number): void {
  authTgUserId = tgUserId;
}

export function buildAuthHeaders(): Record<string, string> {
  const initData = window.Telegram?.WebApp?.initData;
  if (initData) {
    return { "X-Telegram-Init-Data": initData };
  }

  if (import.meta.env.DEV && authTgUserId !== null) {
    return { "X-Dev-Tg-User-Id": String(authTgUserId) };
  }

  return {};
}
