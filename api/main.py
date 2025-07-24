from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from api.services.chat_service import ChatService
from db.database import get_db, init_db
from sqlalchemy.orm import Session

from db.models import Conversation, Message

app = FastAPI()

init_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to chatbot debate, go to /chat to get started"}


"""
Conversation params and reponse types used on /chat/ entrypoint
"""


class ConversationSendMessageParams(BaseModel):
    """
    Parameters required to send a message, if conversation id is None, start a 
    new conversation
    """
    conversation_id: str | None = None
    message: str


class ConversationResponse(BaseModel):
    """
    Response type, returns the conversation id with the last messages sent, 
    ordered from last to first
    """
    conversation_id: str
    messages: List[str]


@app.post("/chat/", response_model=ConversationResponse)
def chat(params: ConversationSendMessageParams, db: Session = Depends(get_db)):
    try:
        chat_service = ChatService(db)
        db_conversation = (
            chat_service.get_conversation(params.conversation_id)
            if params.conversation_id
            else chat_service.create_conversation()
        )
        chat_service.add_message(
            conversation_id=db_conversation.id,
            message=params.message,
            role="user",
        )
        chat_service.add_message(
            conversation_id=db_conversation.id,
            message="reply from bot",
            role="bot",
        )
        messages = chat_service.get_messages(
            conversation_id=db_conversation.id,
        )
        return ConversationResponse(
            conversation_id=db_conversation.id,
            messages=[message.content for message in messages]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
