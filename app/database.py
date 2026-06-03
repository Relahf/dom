from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import os

os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)

engine = create_engine(
    f'sqlite:///{settings.DATABASE_PATH}',
    connect_args={'check_same_thread': False},
    echo=False
)

with engine.connect() as conn:
    conn.execute('PRAGMA journal_mode=WAL')
    conn.commit()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
