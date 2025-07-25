from datetime import datetime
import uuid
from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import TEXT
from db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),  # UUIDs are 36 chars
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin"  # Recommended for async
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        TEXT,
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(10),  # "user" or "bot"
        nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
        lazy="selectin"  # Recommended for async
    )
