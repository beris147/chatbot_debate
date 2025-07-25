from unittest.mock import Mock
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.services.llm_service import LLMService, get_llm
from db.database import Base, get_db


os.environ["TESTING"] = "1"


def __test_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


def __test_llm():
    mock_service = Mock(spec=LLMService)
    mock_service.chat_completion.return_value = {
        "choices": [{"message": {"content": "Mocked response"}}]
    }
    try:
        yield mock_service
    finally:
        pass


@pytest.fixture
def db_session():
    db = next(__test_db())
    try:
        yield db
    finally:
        pass


@pytest.fixture
def client():
    from api.main import app

    app.dependency_overrides[get_db] = __test_db
    app.dependency_overrides[get_llm] = __test_llm

    with TestClient(app) as test_client:
        yield test_client
