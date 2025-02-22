import logging

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from database.connect import sync_engine


def test_session_local_direct():
    """
    Проверяет, что SessionLocal создает сессию, которая корректно выполняет базовый запрос к БД.
    Выполняется запрос SELECT 1, результат которого должен быть равен 1.
    """
    db = None
    try:
        # Выполняем запрос к БД
        with sync_engine.connect() as db:
            result = db.execute(text("SELECT 1")).scalar()
        assert result == 1, f"Неверный результат запроса SELECT 1: {result}"
    except OperationalError as oe:
        pytest.fail(f"Не удалось подключиться к БД через SessionLocal: {oe}")
    except Exception as e:
        pytest.fail(f"Ошибка при тестировании SessionLocal: {e}")
    logging.info("Соединение с базой данных Postgres установлено")

#def test_transaction_rollback():
#    """
#    Проверяет, что транзакции корректно откатываются.
#    """
#    db: Session = SessionLocal()
#    try:
#        # Создаем новую запись
#        new_record = YourModel(name="Test Record")
#        db.add(new_record)
#        db.flush()  # Фиксируем изменения в транзакции
#
#        # Проверяем, что запись была добавлена
#        record = db.query(YourModel).filter(YourModel.name == "Test Record").first()
#        assert record is not None, "Запись не была добавлена в базу данных"
#
#        # Откатываем транзакцию
#        db.rollback()
#
#        # Проверяем, что запись больше не существует
#        record = db.query(YourModel).filter(YourModel.name == "Test Record").first()
#        assert record is None, "Запись не была удалена после отката транзакции"
#    finally:
#        db.close()


#def test_crud_operations():
#    """
#    Проверяет выполнение CRUD-операций.
#    """
#    db: Session = SessionLocal()
#    try:
#        # Create
#        new_record = YourModel(name="Test Record")
#        db.add(new_record)
#        db.commit()
#
#        # Read
#        record = db.query(YourModel).filter(YourModel.name == "Test Record").first()
#        assert record is not None, "Запись не была создана"
#
#        # Update
#        record.name = "Updated Record"
#        db.commit()
#        updated_record = db.query(YourModel).filter(YourModel.name == "Updated Record").first()
#        assert updated_record is not None, "Запись не была обновлена"
#
#        # Delete
#        db.delete(updated_record)
#        db.commit()
#        deleted_record = db.query(YourModel).filter(YourModel.name == "Updated Record").first()
#        assert deleted_record is None, "Запись не была удалена"
#    finally:
#        db.close()

#def test_transaction_isolation():
#    """
#    Проверяет изоляцию транзакций.
#    """
#    db1: Session = SessionLocal()
#    db2: Session = SessionLocal()
#    try:
#        # Добавляем запись в первой транзакции
#        new_record = YourModel(name="Isolation Test")
#        db1.add(new_record)
#        db1.flush()
#
#        # Проверяем, что запись не видна во второй транзакции
#        record_in_db2 = db2.query(YourModel).filter(YourModel.name == "Isolation Test").first()
#        assert record_in_db2 is None, "Запись видна в другой транзакции до коммита"
#
#        # Фиксируем изменения в первой транзакции
#        db1.commit()
#
#        # Проверяем, что запись теперь видна во второй транзакции
#        record_in_db2 = db2.query(YourModel).filter(YourModel.name == "Isolation Test").first()
#        assert record_in_db2 is not None, "Запись не видна в другой транзакции после коммита"
#    finally:
#        db1.close()
#        db2.close()


if __name__ == "__main__":
    pytest.main(["-v", __file__])