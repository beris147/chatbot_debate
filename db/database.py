import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """
    Create tables if they don't exist
    """
    if not os.getenv("TESTING"):
        Base.metadata.create_all(bind=engine)


def get_db():
    """
    Create a connection and keep it open while it's being used
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
