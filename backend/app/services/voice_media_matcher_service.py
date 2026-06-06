import logging
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.media_repository import MediaRepository

logger = logging.getLogger(__name__)


@dataclass
class MediaMatchResult:
    """IDs resolved from the user's media library. All fields are None when nothing matched."""

    media_item_id: UUID | None = field(default=None)
    media_season_id: UUID | None = field(default=None)
    media_episode_id: UUID | None = field(default=None)
    matched_title: str | None = field(default=None)

    @property
    def found(self) -> bool:
        return self.media_item_id is not None


class VoiceMediaMatcherService:
    """Matches a voice-extracted media title against the user's existing media library.

    Matching order:
    1. Exact normalized title (case-insensitive, stripped).
    2. Substring match (needle inside title, or title inside needle).

    Never creates new media items. Returns empty MediaMatchResult when nothing is found.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = MediaRepository(session)

    async def match(
        self,
        tg_user_id: int,
        media_title: str,
        media_type: str | None,
        season_number: int | None,
        episode_number: int | None,
    ) -> MediaMatchResult:
        """Return the best matching media IDs from the user's library.

        media_type should be "movie" or "series" when known; None means search all.
        Season/episode IDs are only resolved for series items.
        """
        item = await self._find_item(tg_user_id, media_title, media_type)
        if item is None:
            logger.info(
                "No media match found for title=%r type=%s user=%s",
                media_title,
                media_type,
                tg_user_id,
            )
            return MediaMatchResult()

        result = MediaMatchResult(media_item_id=item.id, matched_title=item.title)
        logger.info("Matched media item: %r (id=%s)", item.title, item.id)

        if item.media_type == "series" and season_number is not None:
            season = await self.repository.get_season_by_number(item.id, season_number)
            if season is not None:
                result.media_season_id = season.id
                if episode_number is not None:
                    episode = await self.repository.get_episode_by_number(
                        season.id, episode_number
                    )
                    if episode is not None:
                        result.media_episode_id = episode.id

        return result

    async def _find_item(
        self,
        tg_user_id: int,
        media_title: str,
        media_type: str | None,
    ):  # returns MediaItem | None
        items = await self.repository.get_library_items(tg_user_id)
        if not items:
            return None

        needle = media_title.lower().strip()

        # Narrow to the given media_type when it maps to a DB type.
        db_type = media_type if media_type in ("movie", "series") else None
        candidates = [i for i in items if i.media_type == db_type] if db_type else items

        # Pass 1: exact normalized match on the filtered candidates.
        for item in candidates:
            if item.title.lower().strip() == needle:
                return item

        # Pass 2: substring match on the filtered candidates.
        for item in candidates:
            haystack = item.title.lower().strip()
            if needle in haystack or haystack in needle:
                return item

        # Pass 3: fall back to all items if the type filter produced no result.
        if db_type is not None:
            for item in items:
                if item.title.lower().strip() == needle:
                    return item
            for item in items:
                haystack = item.title.lower().strip()
                if needle in haystack or haystack in needle:
                    return item

        return None
