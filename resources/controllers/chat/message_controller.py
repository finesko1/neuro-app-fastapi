import logging

from sqlalchemy import text

from database.connect import session
from resources.models.chat.messages import Messages

def get_chat_messages(chat_id: int):
    """
    Получает все сообщения для заданного чата из базы данных.

    Эта функция выполняет запрос к базе данных для извлечения всех сообщений, связанных с указанным идентификатором чата.
    Если сообщения для данного чата не найдены, будет вызвано исключение ValueError.

    :param chat_id: Число, представляющее уникальный идентификатор чата.
    :type chat_id: int
    :return: Список сообщений, связанных с указанным чатом.
    :rtype: list
    :raises ValueError: Если сообщения для чата с указанным идентификатором не найдены.
    """
    with session() as db:
        #result = db.execute(text("SELECT * FROM messages")).all()
        result = db.query(Messages).all()
        messages = []
        for message in result:
            messages.append({
                "id": message.id,
                "role": message.role,
                "chat_id": message.chat_id,
                "content": message.content,
            })
        if not result:
            raise ValueError(f"No messages found for chat_id {chat_id}")
        return messages