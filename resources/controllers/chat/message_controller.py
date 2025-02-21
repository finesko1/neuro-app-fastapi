import logging
import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from database.connect import get_db
from sqlalchemy.sql import text

#from chat import Chat
#from message import Message

def get_chat_messages(chat_id: int):
    """
    Получает все сообщения для заданного чата из базы данных.

    :param chat_id: Число, представляющее уникальный идентификатор чата.
    :type chat_id: int
    :return: Список сообщений.
    :rtype: list
    :raises ValueError: Если сообщения для чата с указанным идентификатором не найдены.
    """
    # Создаем сессию и выполняем выборку сообщений чата
    with next(get_db()) as db:
        try:
            logging.info(f"chat_id: {chat_id}, тип: {type(chat_id)}")

            # Выполняем SQL-запрос
            result = db.execute(text("SELECT * FROM messages WHERE chat_id = :chat_id"), {"chat_id": chat_id})
            messages = result.fetchall()  # Получаем все сообщения

            # Проверяем, что сообщения найдены
            if not messages:
                raise ValueError("Сообщения для указанного chat_id не найдены")

            logging.info("Сообщения найдены")
            return messages  # Возвращаем все сообщения

        except OperationalError as e:
            logging.error(f"Ошибка подключения к базе данных: {e}")
            pytest.fail("Не удалось подключиться к базе данных")
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            pytest.fail("Произошла ошибка при выполнении запроса")