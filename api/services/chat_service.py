from datetime import datetime
from typing import Dict, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from db.models import Conversation, Message


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self) -> Conversation:
        db_conversation = Conversation()
        self.db.add(db_conversation)
        await self.db.commit()
        await self.db.refresh(db_conversation)
        return db_conversation

    async def get_conversation(self, conversation_id: str) -> Conversation:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
        )
        db_conversation = result.scalars().first()
        if db_conversation is None:
            raise HTTPException(
                status_code=404, detail=f"No conversation {conversation_id} found")
        return db_conversation

    async def add_message(self, conversation_id: str, message: str, role: str) -> Message:
        db_message = Message(
            conversation_id=conversation_id,
            content=message,
            role=role,
            timestamp=datetime.now(),
        )
        self.db.add(db_message)
        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def get_messages(
        self,
        conversation_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def format_messages_for_llm(self, conversation_id: str) -> List[Dict]:
        """
        Formats conversation messages for llm API

        user 'questions' expects to see the value "user"
        llm responses expect to see the value "assistant"
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
        )
        messages = result.scalars().all()

        return [
            {
                "role": "assistant" if msg.role == "bot" else msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
