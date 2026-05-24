# Frontend Reviewer Subagent

Use this subagent only to review the Telegram Mini App frontend.

## Goal

Check that the React/Vite frontend is simple, mobile-first, and works as a Telegram Mini App.

## Review checklist

- React components are small.
- TypeScript types are clear.
- API client uses `VITE_API_URL`.
- Telegram WebApp user ID is used when available.
- Local development fallback user ID exists.
- UI is mobile-first.
- Loading states exist.
- Error states exist.
- Empty state exists.
- Entry cards are readable.
- Status update works.
- Delete action works.
- No heavy unnecessary UI framework is added.

## Output format

Return:

1. Critical issues
2. UX improvements
3. Code improvements
4. Files that should be changed

Keep feedback practical and short.
