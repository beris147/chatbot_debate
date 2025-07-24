from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models import Conversation, Message


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self) -> Conversation:
        db_conversation = Conversation()
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation

    def get_conversation(self, conversation_id: str) -> Conversation:
        db_conversation = self.db.query(
            Conversation).filter_by(id=conversation_id).first()
        if db_conversation is None:
            raise HTTPException(
                status_code=404, detail=f"No conversation {conversation_id} found")
        return db_conversation

    def add_message(self, conversation_id: str, message: str, role: str) -> Message:
        db_message = Message(
            conversation_id=conversation_id,
            content=message,
            role=role,
            timestamp=datetime.now(),
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        print(
            "Message added with: ",
            db_message.id,
            db_message.content,
            db_message.timestamp
        )
        return db_message

    def get_messages(self, conversation_id: str, skip: int = 0, limit: int = 10) -> List[Message]:
        messages = self.db.query(Message)\
            .filter_by(conversation_id=conversation_id)\
            .order_by(Message.timestamp.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        return messages
