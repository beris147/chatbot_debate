import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base

from api.services.chat_service import ChatService


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        self.db = TestingSessionLocal()
        self.service = ChatService(self.db)

    def tearDown(self):
        self.db.close()

    def test_chat_service_create_conversation(self):
        conversation = self.service.create_conversation()
        assert conversation.id is not None

    def test_chat_service_add_message(self):
        conversation = self.service.create_conversation()
        message = self.service.add_message(conversation.id, "test", "user")
        assert message.id is not None
        assert message.content == "test"
        assert message.role == "user"
        messages = self.service.get_messages(conversation.id)
        assert len(messages) == 1
        assert messages[0].content == "test"
        self.service.add_message(conversation.id, "test reply", "bot")
        messages = self.service.get_messages(conversation.id)
        assert len(messages) == 2
