from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from api.personas.debate_persona import DebatePersona
from api.services.chat_service import ChatService
from api.services.llm_service import LLMService, get_llm
from db.database import get_db, init_db
from sqlalchemy.orm import Session


def create_app():
    app = FastAPI()
    init_db()
    return app


app = create_app()


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
def chat(
        params: ConversationSendMessageParams,
        db: Session = Depends(get_db),
        llm: LLMService = Depends(get_llm),
):
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
        debate_persona = DebatePersona(llm)
        bot_response = debate_persona.get_counter_argument(
            conversation_history=chat_service.format_messages_for_llm(
                conversation_id=db_conversation.id
            )
        )
        chat_service.add_message(
            conversation_id=db_conversation.id,
            message=bot_response,
            role="bot",
        )
        messages = chat_service.get_messages(
            conversation_id=db_conversation.id,
        )
        return ConversationResponse(
            conversation_id=db_conversation.id,
            messages=[message.content for message in messages]
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
