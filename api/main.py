import asyncio
import json
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.logger import logger
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.personas.debate_persona import DebatePersona
from api.services.chat_service import ChatService
from api.services.llm_service import LLMService, get_llm
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


app = FastAPI()


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
async def chat(
        params: ConversationSendMessageParams,
        db: AsyncSession = Depends(get_db),
        llm: LLMService = Depends(get_llm),
):
    try:
        chat_service = ChatService(db)
        db_conversation = await (
            chat_service.get_conversation(params.conversation_id)
            if params.conversation_id
            else chat_service.create_conversation()
        )
        await chat_service.add_message(
            conversation_id=db_conversation.id,
            message=params.message,
            role="user",
        )
        debate_persona = DebatePersona(llm)
        history = await chat_service.format_messages_for_llm(
            conversation_id=db_conversation.id
        )
        bot_response = debate_persona.get_counter_argument(
            conversation_history=history
        )
        await chat_service.add_message(
            conversation_id=db_conversation.id,
            message=bot_response,
            role="bot",
        )
        messages = await chat_service.get_messages(
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


@app.post("/chat/stream", response_model=ConversationResponse)
async def chat_stream(
    params: ConversationSendMessageParams,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    chat_service = ChatService(db)
    try:
        db_conversation = await (
            chat_service.get_conversation(params.conversation_id)
            if params.conversation_id
            else chat_service.create_conversation()
        )
        await chat_service.add_message(
            conversation_id=db_conversation.id,
            message=params.message,
            role="user"
        )

        async def generate():
            full_response = ""
            try:
                history = await chat_service.format_messages_for_llm(
                    conversation_id=db_conversation.id
                )
                debate_persona = DebatePersona(llm)
                chunk_id = 1
                yield "event: start\n\n"
                async for chunk in debate_persona.gen_counter_argument_stream(history):
                    chunk_data = {
                        "conversation_id": db_conversation.id,
                        "message": chunk,
                        "part": chunk_id,
                    }
                    yield f"{json.dumps(chunk_data)}\n\n"
                    full_response += chunk
                    chunk_id += 1

                await chat_service.add_message(
                    conversation_id=db_conversation.id,
                    message=full_response,
                    role="bot"
                )

                messages = await chat_service.get_messages(db_conversation.id)
                complete_data = {
                    "conversation_id": db_conversation.id,
                    "messages": [msg.content for msg in messages],
                    "part": "final",
                }
                yield f"{json.dumps(complete_data)}\n\n"
                yield "event: end\n\n"

            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
