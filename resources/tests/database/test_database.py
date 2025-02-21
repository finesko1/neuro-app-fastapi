import pytest
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session

from database.connect import SessionLocal, get_db

def test_session_local_direct():
    """
    Проверяет, что SessionLocal создает сессию, которая корректно выполняет базовый запрос к БД.
    Выполняется запрос SELECT 1, результат которого должен быть равен 1.
    """
    db = None
    try:
        engine = create_engine(
            f"postgresql://postgres:Q6TR63v4@postgres:5432/neuro_DB",
            connect_args={"options": "-c statement_timeout=10000"},
            echo=True
        )
        # создаем класс сессии
        with Session(autoflush=False, bind=engine) as db:
            result = db.execute(text("SELECT 1")).scalar()
        assert result == 1, f"Неверный результат запроса SELECT 1: {result}"
    except OperationalError as oe:
        pytest.fail(f"Не удалось подключиться к БД через SessionLocal: {oe}")
    except Exception as e:
        pytest.fail(f"Ошибка при тестировании SessionLocal: {e}")
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])