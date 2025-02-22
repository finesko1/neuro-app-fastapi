from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from database.config import settings

# Создание подключений к БД
sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False,
)
async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False,
)

session = sessionmaker(bind=sync_engine)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)

# Основа для моделей
class Base(DeclarativeBase):
    pass


# Проверка работы с БД
def check_connect():
    try:
        # Проверка синхронного подключения
        with sync_engine.connect() as db:
            res = db.execute(text("SELECT VERSION()"))
            print(f"Версия PostgreSQL: {res.scalar()}")

        # Проверка сессии
        with session() as db:
            res = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            tables = [row[0] for row in res]
            print(f"Список таблиц: {tables}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise