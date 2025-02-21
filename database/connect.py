import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from resources.helpers.environment_helper import EnvironmentHelper

env = EnvironmentHelper()

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Загружаем настройки для подключения к БД из переменных окружения
# Используем значения по умолчанию для DB_HOST и DB_PORT
DB_HOST = env.db_host
DB_PORT = env.db_port
DB_DATABASE = env.db_database
DB_USERNAME = env.db_username
DB_PASSWORD = env.db_password

# Формирование строки подключения
DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
logging.info(f"DATABASE_URL: {DATABASE_URL}")

# Создаем движок SQLAlchemy с указанными настройками
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"options": "-c statement_timeout=10000"}
    )
except SQLAlchemyError as e:
    logging.error("Ошибка при создании движка SQLAlchemy", exc_info=True)
    raise

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Генератор сессий для работы с базой данных.
    При каждом вызове создается новая сессия, которая гарантированно закрывается после использования.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()