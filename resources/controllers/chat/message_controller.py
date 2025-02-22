import logging
from fastapi import Request, HTTPException
from sqlalchemy.future import select
from sqlalchemy import text
from starlette.responses import JSONResponse

from database.connect import session, async_session
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
            result = db.query(Messages).filter(Messages.chat_id == chat_id).all()
            if not result:
                raise HTTPException(status_code=404, detail=f"No messages found for (chat_id: {chat_id}).")

            messages = []
            for message in result:
                messages.append({
                    "id": message.id,
                    "role": message.role,
                    "chat_id": message.chat_id,
                    "content": message.content,
                })

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

            if result is None:
                raise HTTPException(status_code=404, detail=f"No messages (id: {message_id}) found for (chat_id: {chat_id}).")

            message = {
                "id": result.id,
                "role": result.role,
                "chat_id": result.chat_id,
                "content": result.content
            }

            return message

    async def put_chat_message(self, chat_id: int, request) -> str:
        """
        Сохраняет сообщение в БД.

        :param chat_id: ID чата
        :param request: Объект запроса (Pydantic модель)
        :return: Результат операции
        """
        async with async_session() as db:
            # Создаем объект сообщения
            message = Messages(
                chat_id=chat_id,
                role=request.role,
                content=request.content
            )

        ollama_model = request.model

            ## Добавляем и сохраняем сообщение
            #db.add(message)
            #await db.commit()
            #await db.refresh(message)  # Обновляем объект данными из БД
        return "Сообщение успешно добавлено"

    async def delete_chat_message(selfself, chat_id: int, message_id: int):
        """
        Удаляет сообщения из чата БД

        :param chat_id:
        :param message_id:
        :return: Результат операции
        """
        async with async_session() as db:
            result = await db.execute(
                select(Messages).where(Messages.chat_id == chat_id, Messages.id == message_id)
            )
            message = result.scalars().first()
            if message:
                await db.delete(message)
                await db.commit()
                return "Сообщение успешно удалено"
            else:
                return "Сообщения не существует"