from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import MediaEpisode, MediaItem
from app.models.vocabulary import VocabularyEntry
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import DailyVocabularySuggestionResponse, StreakDayResponse, StreakSummaryResponse
from app.services.openai_service import OpenAIService


class StreakService:
    DAILY_ADD_GOAL = 8
    DAILY_LEARN_GOAL = 2

    def __init__(
        self,
        session: AsyncSession,
        activity_repository: ActivityRepository,
        user_repository: UserRepository,
        openai_service: OpenAIService | None = None,
    ) -> None:
        self.session = session
        self.activity_repository = activity_repository
        self.user_repository = user_repository
        self.openai_service = openai_service or OpenAIService()

    async def record_activity(self, tg_user_id: int, activity_kind: str) -> None:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        await self.activity_repository.mark_daily_activity(
            tg_user_id=tg_user_id,
            activity_date=self._today_utc(),
            activity_kind=activity_kind,
        )

    async def get_summary(self, tg_user_id: int) -> StreakSummaryResponse:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        activity_rows = await self.activity_repository.list_by_user(tg_user_id)
        activity_map = {row.activity_date: row for row in activity_rows}
        active_dates = sorted(activity_map.keys())
        today = self._today_utc()
        current_streak = self._calculate_current_streak(active_dates, today)

        total_words = await self._count_words(tg_user_id)
        learned_words = await self._count_words(tg_user_id, status="learned")
        watched_minutes = await self._sum_watched_minutes(tg_user_id)
        watched_movies = await self._count_watched_movies(tg_user_id)
        watched_episodes = await self._count_watched_episodes(tg_user_id)
        media_vocabulary_count = await self._count_media_words(tg_user_id)
        words_added_today = await self._count_words_added_on_date(tg_user_id, today)
        words_learned_today = await self._count_words_learned_on_date(tg_user_id, today)
        added_counts_by_date = await self._count_words_added_grouped_by_date(tg_user_id)
        learned_counts_by_date = await self._count_words_learned_grouped_by_date(tg_user_id)
        elite_dates = self._build_elite_completion_dates(added_counts_by_date, learned_counts_by_date)
        elite_today_complete = (
            words_added_today >= self.DAILY_ADD_GOAL and words_learned_today >= self.DAILY_LEARN_GOAL
        )

        return StreakSummaryResponse(
            current_streak_days=current_streak,
            best_streak_days=self._calculate_best_streak(active_dates),
            elite_current_streak_days=self._calculate_current_streak(elite_dates, today),
            elite_best_streak_days=self._calculate_best_streak(elite_dates),
            elite_today_complete=elite_today_complete,
            active_days_total=len(active_dates),
            today_actions=activity_map.get(today).action_count if today in activity_map else 0,
            last_activity_date=active_dates[-1] if active_dates else None,
            last_14_days=self._build_day_window(activity_map, today, 14, set(elite_dates)),
            last_30_days_active=self._count_active_days_in_window(activity_map, today, 30),
            next_milestone_days=self._calculate_next_milestone(current_streak),
            total_words=total_words,
            learned_words=learned_words,
            watched_minutes=watched_minutes,
            watched_movies=watched_movies,
            watched_episodes=watched_episodes,
            media_vocabulary_count=media_vocabulary_count,
            daily_add_goal=self.DAILY_ADD_GOAL,
            daily_learn_goal=self.DAILY_LEARN_GOAL,
            words_added_today=words_added_today,
            words_learned_today=words_learned_today,
            remaining_add_goal=max(self.DAILY_ADD_GOAL - words_added_today, 0),
            remaining_learn_goal=max(self.DAILY_LEARN_GOAL - words_learned_today, 0),
        )

    async def get_daily_vocabulary_suggestions(self, tg_user_id: int) -> DailyVocabularySuggestionResponse:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        today = self._today_utc()
        words_added_today = await self._count_words_added_on_date(tg_user_id, today)
        words_learned_today = await self._count_words_learned_on_date(tg_user_id, today)
        recent_words = await self._list_recent_words(tg_user_id, limit=120)
        suggestion_blacklist = await self.user_repository.get_suggestion_blacklist(tg_user_id)

        suggestion_response, _ = await self.openai_service.suggest_daily_vocabulary(
            words_added_today=words_added_today,
            daily_add_goal=self.DAILY_ADD_GOAL,
            words_learned_today=words_learned_today,
            daily_learn_goal=self.DAILY_LEARN_GOAL,
            recent_words=recent_words,
            blacklisted_suggestions=suggestion_blacklist,
        )

        suggestion_response.suggestions = self._filter_suggestions(
            suggestion_response.suggestions,
            excluded_texts={*recent_words, *suggestion_blacklist},
            target_count=max(self.DAILY_ADD_GOAL - words_added_today, 0) or 5,
        )

        if suggestion_response.ai_model is None:
            suggestion_response.ai_model = self.openai_service.settings.openai_model

        suggestion_response.target_new_words = self.DAILY_ADD_GOAL
        suggestion_response.words_added_today = words_added_today
        suggestion_response.remaining_new_words = max(self.DAILY_ADD_GOAL - words_added_today, 0)
        suggestion_response.learned_today = words_learned_today
        suggestion_response.remaining_learned_words = max(self.DAILY_LEARN_GOAL - words_learned_today, 0)
        await self.record_activity(tg_user_id, "ask_ai")
        await self.session.commit()
        return suggestion_response

    async def add_suggestion_to_blacklist(self, tg_user_id: int, text: str) -> int:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        blacklist = await self.user_repository.add_to_suggestion_blacklist(tg_user_id, text)
        await self.session.commit()
        return len(blacklist)

    @staticmethod
    def _today_utc() -> date:
        return datetime.now(timezone.utc).date()

    @staticmethod
    def _calculate_current_streak(active_dates: list[date], today: date) -> int:
        if not active_dates:
            return 0

        active_set = set(active_dates)
        if today in active_set:
            cursor = today
        elif today - timedelta(days=1) in active_set:
            cursor = today - timedelta(days=1)
        else:
            return 0

        streak = 0
        while cursor in active_set:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    @staticmethod
    def _calculate_best_streak(active_dates: list[date]) -> int:
        if not active_dates:
            return 0

        best = 1
        current = 1

        for index in range(1, len(active_dates)):
            if active_dates[index] == active_dates[index - 1] + timedelta(days=1):
                current += 1
                best = max(best, current)
            else:
                current = 1

        return best

    @staticmethod
    def _build_day_window(
        activity_map: dict[date, object],
        end_date: date,
        total_days: int,
        elite_dates: set[date] | None = None,
    ) -> list[StreakDayResponse]:
        start_date = end_date - timedelta(days=total_days - 1)
        days: list[StreakDayResponse] = []
        elite_date_set = elite_dates or set()

        for offset in range(total_days):
            current_date = start_date + timedelta(days=offset)
            row = activity_map.get(current_date)
            days.append(
                StreakDayResponse(
                    date=current_date,
                    is_active=row is not None,
                    action_count=getattr(row, "action_count", 0),
                    is_elite=current_date in elite_date_set,
                )
            )

        return days

    @staticmethod
    def _count_active_days_in_window(activity_map: dict[date, object], end_date: date, total_days: int) -> int:
        start_date = end_date - timedelta(days=total_days - 1)
        return sum(1 for activity_date in activity_map if start_date <= activity_date <= end_date)

    @staticmethod
    def _calculate_next_milestone(current_streak_days: int) -> int:
        for milestone in (3, 7, 14, 30, 60, 100):
            if current_streak_days < milestone:
                return milestone
        return current_streak_days + 25

    async def _count_words(self, tg_user_id: int, status: str | None = None) -> int:
        statement = select(func.count(VocabularyEntry.id)).where(VocabularyEntry.tg_user_id == tg_user_id)
        if status:
            statement = statement.where(VocabularyEntry.status == status)
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def _count_media_words(self, tg_user_id: int) -> int:
        statement = select(func.count(VocabularyEntry.id)).where(
            VocabularyEntry.tg_user_id == tg_user_id,
            VocabularyEntry.source_type == "media",
        )
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def _sum_watched_minutes(self, tg_user_id: int) -> int:
        movies_statement = select(func.coalesce(func.sum(MediaItem.watched_minutes), 0)).where(
            MediaItem.tg_user_id == tg_user_id,
            MediaItem.media_type == "movie",
        )
        episodes_statement = (
            select(func.coalesce(func.sum(MediaEpisode.watched_minutes), 0))
            .join(MediaItem, MediaItem.id == MediaEpisode.series_item_id)
            .where(MediaItem.tg_user_id == tg_user_id, MediaItem.media_type == "series")
        )
        movies_result = await self.session.execute(movies_statement)
        episodes_result = await self.session.execute(episodes_statement)
        return int((movies_result.scalar() or 0) + (episodes_result.scalar() or 0))

    async def _count_watched_movies(self, tg_user_id: int) -> int:
        statement = select(func.count(MediaItem.id)).where(
            MediaItem.tg_user_id == tg_user_id,
            MediaItem.media_type == "movie",
            MediaItem.is_watched.is_(True),
        )
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def _count_watched_episodes(self, tg_user_id: int) -> int:
        statement = (
            select(func.count(MediaEpisode.id))
            .join(MediaItem, MediaItem.id == MediaEpisode.series_item_id)
            .where(
                MediaItem.tg_user_id == tg_user_id,
                MediaItem.media_type == "series",
                MediaEpisode.is_watched.is_(True),
            )
        )
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def _count_words_added_on_date(self, tg_user_id: int, target_date: date) -> int:
        statement = select(func.count(VocabularyEntry.id)).where(
            VocabularyEntry.tg_user_id == tg_user_id,
            func.date(VocabularyEntry.created_at) == target_date,
        )
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def _count_words_learned_on_date(self, tg_user_id: int, target_date: date) -> int:
        statement = select(func.count(VocabularyEntry.id)).where(
            VocabularyEntry.tg_user_id == tg_user_id,
            VocabularyEntry.status == "learned",
            VocabularyEntry.learned_at.is_not(None),
            func.date(VocabularyEntry.learned_at) == target_date,
        )
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def _list_recent_words(self, tg_user_id: int, limit: int = 120) -> list[str]:
        statement = (
            select(VocabularyEntry.normalized_text)
            .where(VocabularyEntry.tg_user_id == tg_user_id)
            .order_by(VocabularyEntry.updated_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return [value for value in result.scalars().all() if value]

    async def _count_words_added_grouped_by_date(self, tg_user_id: int) -> dict[date, int]:
        statement = (
            select(func.date(VocabularyEntry.created_at), func.count(VocabularyEntry.id))
            .where(VocabularyEntry.tg_user_id == tg_user_id)
            .group_by(func.date(VocabularyEntry.created_at))
        )
        result = await self.session.execute(statement)
        return {row[0]: int(row[1]) for row in result.all() if row[0] is not None}

    async def _count_words_learned_grouped_by_date(self, tg_user_id: int) -> dict[date, int]:
        statement = (
            select(func.date(VocabularyEntry.learned_at), func.count(VocabularyEntry.id))
            .where(
                VocabularyEntry.tg_user_id == tg_user_id,
                VocabularyEntry.status == "learned",
                VocabularyEntry.learned_at.is_not(None),
            )
            .group_by(func.date(VocabularyEntry.learned_at))
        )
        result = await self.session.execute(statement)
        return {row[0]: int(row[1]) for row in result.all() if row[0] is not None}

    def _build_elite_completion_dates(
        self,
        added_counts_by_date: dict[date, int],
        learned_counts_by_date: dict[date, int],
    ) -> list[date]:
        all_dates = set(added_counts_by_date) | set(learned_counts_by_date)
        return sorted(
            day
            for day in all_dates
            if added_counts_by_date.get(day, 0) >= self.DAILY_ADD_GOAL
            and learned_counts_by_date.get(day, 0) >= self.DAILY_LEARN_GOAL
        )

    @staticmethod
    def _normalize_excluded_text(text: str) -> str:
        return " ".join(text.strip().lower().split())

    def _filter_suggestions(self, suggestions, excluded_texts: set[str], target_count: int):
        normalized_excluded = {self._normalize_excluded_text(text) for text in excluded_texts if text}
        filtered = []
        seen: set[str] = set()

        for suggestion in suggestions:
            normalized_text = self._normalize_excluded_text(suggestion.text)
            if not normalized_text or normalized_text in normalized_excluded or normalized_text in seen:
                continue
            seen.add(normalized_text)
            filtered.append(suggestion)
            if len(filtered) >= target_count:
                break

        return filtered
