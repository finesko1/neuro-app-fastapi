import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv, find_dotenv

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Попытка найти файл .env
env_path = find_dotenv()

if not env_path:
    # Если тесты запускаются не из корня проекта, указываем относительный путь до .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

if not os.path.exists(env_path):
    logging.warning("Файл .env не найден! Проверьте, что переменные окружения заданы.")
else:
    load_dotenv(env_path)
    logging.info(f"Файл .env загружен из {env_path}")

# Загружаем настройки для подключения к БД из переменных окружения
# Используем значения по умолчанию для DB_HOST и DB_PORT
DB_HOST = "postgres"
DB_PORT = "5432"
DB_DATABASE = os.environ.get("DB_DATABASE")
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Проверяем, что обязательные переменные заданы
if not DB_DATABASE or not DB_USERNAME or not DB_PASSWORD:
    raise EnvironmentError("Отсутствуют необходимые переменные окружения (DB_DATABASE, DB_USERNAME, DB_PASSWORD) для подключения к БД.")

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