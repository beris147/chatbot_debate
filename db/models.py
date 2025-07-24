import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import TEXT
from db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    conversation_id = Column(
        String,
        ForeignKey("conversations.id"),
        nullable=False,
    )
    content = Column(TEXT, nullable=False)
    role = Column(String, nullable=False)  # Expected values: "user" or "bot"
    timestamp = Column(DateTime)

    conversation = relationship("Conversation", back_populates="messages")
