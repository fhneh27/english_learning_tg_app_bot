from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    tg_user_id: int
    username: str | None = Field(default=None, max_length=64)
    first_name: str | None = Field(default=None, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tg_user_id: int
    username: str | None
    first_name: str | None
    created_at: datetime
    updated_at: datetime


class StreakDayResponse(BaseModel):
    date: date
    is_active: bool
    action_count: int
    is_elite: bool = False


class StreakSummaryResponse(BaseModel):
    current_streak_days: int
    best_streak_days: int
    elite_current_streak_days: int
    elite_best_streak_days: int
    elite_today_complete: bool
    active_days_total: int
    today_actions: int
    last_activity_date: date | None
    last_14_days: list[StreakDayResponse]
    last_30_days_active: int
    next_milestone_days: int
    total_words: int
    learned_words: int
    watched_minutes: int
    watched_movies: int
    watched_episodes: int
    media_vocabulary_count: int
    daily_add_goal: int
    daily_learn_goal: int
    words_added_today: int
    words_learned_today: int
    remaining_add_goal: int
    remaining_learn_goal: int


class DailyVocabularySuggestionItemResponse(BaseModel):
    text: str
    kind: str
    level: str
    category: str
    reason_ru: str
    usage_hint_ru: str


class DailyVocabularySuggestionResponse(BaseModel):
    summary_ru: str
    target_new_words: int
    words_added_today: int
    remaining_new_words: int
    learned_today: int
    remaining_learned_words: int
    suggestions: list[DailyVocabularySuggestionItemResponse]
    ai_model: str | None


class SuggestionBlacklistRequest(BaseModel):
    tg_user_id: int
    text: str = Field(min_length=1, max_length=256)


class SuggestionBlacklistResponse(BaseModel):
    text: str
    blacklist_size: int
