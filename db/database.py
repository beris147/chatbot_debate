from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(bind=engine)


# Create a connection and keep it open while it's being used
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
