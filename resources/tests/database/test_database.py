# test_database.py
import logging
import sys
import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
sys.path.append("resources/tests/")
from database.connect import get_db

def test_database_connection():
    """
    Тестирует подключение к базе данных, проверяя возможность создания сессии.
    """
    try:
        # Создаем сессию и выполняем простой запрос
        with next(get_db()) as db:
            result = db.execute(text("SELECT 1"))
            assert result.scalar() == 1
            logging.info("Подключение к базе данных выполнено")
    except OperationalError:
        pytest.fail("Не удалось подключиться к базе данных")

if __name__ == "__main__":
    pytest.main(["-v", "test_database.py"])