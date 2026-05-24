import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VocabularyEntry(Base):
    __tablename__ = "vocabulary_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    translation_ru: Mapped[str] = mapped_column(Text, nullable=False)
    meaning_ru: Mapped[str] = mapped_column(Text, nullable=False)
    part_of_speech: Mapped[str | None] = mapped_column(String(64), nullable=True)
    level: Mapped[str | None] = mapped_column(String(16), nullable=True)
    transcription: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False, default=list)
    synonyms: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="learning")
    repeat_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    learned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
