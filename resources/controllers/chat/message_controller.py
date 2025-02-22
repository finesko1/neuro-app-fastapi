import logging

from sqlalchemy import text

from database.connect import session
from resources.models.chat.messages import Messages

class MessageController:
    def __init__(self):
        pass

    def get_chat_messages(self, chat_id: int):
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
            if not messages:
                raise ValueError(f"No messages found for chat_id {chat_id}")
            return messages

    def get_chat_message(self, chat_id: int, message_id: int) -> dict:
        """
        Получает определенное сообщение из чата базы данных

        Эта функция получает определенное сообщение из БД, основываясь на уникальные номера чата и сообщения.
        Если сообщение для данного чата не найдено, будет вызвано исключение ValueError.

        :param chat_id: Число, представляющее уникальный идентификатор чата.
        :rtype int

        :param message_id:
        :rtype int

        :return: Сообщение чата в виде словаря, основываясь на идентификатор.
        :rtype: dict
        :raises ValueError: Если сообщения для чата с указанным идентификатором не найдены.
        """

        with session() as db:
            result = db.query(Messages).filter(Messages.chat_id == chat_id, Messages.id == message_id).first()
            message = {
                "id": result.id,
                "role": result.role,
                "chat_id": result.chat_id,
                "content": result.content
            }
            if not message:
                raise ValueError(f"No messages (id: {message_id}) found for (chat_id: {chat_id}).")
            return message

