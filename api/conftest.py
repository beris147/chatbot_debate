import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

    with TestClient(app) as test_client:
        yield test_client
