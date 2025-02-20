import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_CONNECTION = os.getenv("DB_CONNECTION", "postgresql")
DB_HOST = os.getenv("DB_HOST", "172.18.0.1")
DB_PORT = os.getenv("DB_PORT", "54321")
DB_DATABASE = os.getenv("DB_DATABASE", "neuro_DB")
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apDgiX")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()