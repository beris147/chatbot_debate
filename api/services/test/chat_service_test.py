
import pytest
from api.services.chat_service import ChatService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_chat_service_create_conversation(db_session: AsyncSession):
    print("DB: ", db_session)
    service = ChatService(db_session)
    conversation = await service.create_conversation()
    assert conversation.id is not None


@pytest.mark.asyncio
async def test_chat_service_add_message(db_session):
    service = ChatService(db_session)
    conversation = await service.create_conversation()
    message = await service.add_message(conversation.id, "test", "user")
    assert message.id is not None
    assert message.content == "test"
    assert message.role == "user"
    messages = await service.get_messages(conversation.id)
    assert len(messages) == 1
    assert messages[0].content == "test"
    await service.add_message(conversation.id, "test reply", "bot")
    messages = await service.get_messages(conversation.id)
    assert len(messages) == 2
