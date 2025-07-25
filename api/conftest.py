import pytest
import os
from unittest.mock import Mock
from fastapi.testclient import TestClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from api.services.llm_service import LLMService, get_llm
from db.database import Base, get_db

os.environ["TESTING"] = "1"


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_llm():
    mock_service = Mock(spec=LLMService)
    mock_service.chat_completion.return_value = {
        "choices": [{"message": {"content": "Mocked response"}}]
    }
    return mock_service


@pytest.fixture
def client(db_session, mock_llm):
    from api.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_llm] = lambda: mock_llm

    with TestClient(app) as test_client:
        yield test_client
