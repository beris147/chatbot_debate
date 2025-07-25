
from api.services.chat_service import ChatService


def test_chat_service_create_conversation(db_session):
    service = ChatService(db_session)
    conversation = service.create_conversation()
    assert conversation.id is not None


def test_chat_service_add_message(db_session):
    service = ChatService(db_session)
    conversation = service.create_conversation()
    message = service.add_message(conversation.id, "test", "user")
    assert message.id is not None
    assert message.content == "test"
    assert message.role == "user"
    messages = service.get_messages(conversation.id)
    assert len(messages) == 1
    assert messages[0].content == "test"
    service.add_message(conversation.id, "test reply", "bot")
    messages = service.get_messages(conversation.id)
    assert len(messages) == 2
