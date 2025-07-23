from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
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
    def create_conversation(db: Session) -> Conversation:
        db_conversation = Conversation()
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    
    def get_conversation(id: str, db: Session) -> Conversation:
        db_conversation = db.query(Conversation).filter_by(id = id).first()
        if db_conversation is None:
            raise HTTPException(status_code=404, detail=f"No conversation {params.conversation_id} found")
        return db_conversation
    
    def add_message(conversation: Conversation, message: str, role: str, db: Session) -> Message:
        db_message = Message(conversation_id=conversation.id, content=message, role=role)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_messages(conversation: Conversation, db: Session, skip: int = 0, limit: int  = 10) -> List[Message]:
        messages = db.query(Message).filter_by(conversation_id = conversation.id)
        return messages or []
    
    try:
        db_conversation = get_conversation(id=params.conversation_id, db=db) if params.conversation_id else create_conversation(db=db)
        add_message(conversation=db_conversation, message=params.message, role="user", db=db)
        # TODO: call llm
        add_message(conversation=db_conversation, message="reply from bot", role="bot", db=db)
        messages = get_messages(conversation=db_conversation, db = db)
        return ConversationResponse(
            conversation_id=db_conversation.id,
            messages=[message.content for message in messages]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))