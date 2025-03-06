from fastapi import HTTPException,status
from sqlalchemy.future import select

from database.connect import session, async_session

# Модель сообщений для работы с БД
from resources.controllers.llm.vector_db_controller import VectorDbController
from resources.models.chat.messages import Messages
from resources.models.llm.chat.chat_request import ChatRequest

from resources.controllers.llm.llm_controller import LLMController
llm = LLMController()

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

            # Если сообщений не найдено, возвращаем пустой массив
            if not result:
                return []  # Возвращаем пустой массив вместо исключения

            messages = []
            for message in result:
                messages.append({
                    "id": message.id,
                    "role": message.role,
                    "chat_id": message.chat_id,
                    "content": message.content,
                    "global_collection": message.global_collection,
                    "local_collection": message.local_collection
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
                "content": result.content,
                "global_collection": result.global_collection,
                "local_collection": result.local_collection
            }

            return message

    async def put_chat_message(self, chat_id: int, request: ChatRequest):
        """
        Сохраняет сообщение в БД.

        :param chat_id: ID чата
        :param request: Объект запроса (Pydantic модель)
        :return: Результат операции
        """
        # Создаем объект сообщения
        if request.messages:
            last_message = request.messages[-1]
            message = Messages(
                chat_id=chat_id,
                role=last_message.role,
                content=last_message.content,
                global_collection=last_message.global_collection,
                local_collection=last_message.local_collection
            )
        else:
            return "Массив сообщений не найден"

        
        collection_names = []
        vector_db = VectorDbController()

        last_message = request.messages[-1]
        retrievers = []

        if request.use_local_collection == True:
            collection_names.append(last_message.local_collection)
            retrievers = await vector_db.chroma_as_retrievers(collection_names)

        if request.use_global_collection == True:
            collection_names.append(last_message.global_collection)
            retrievers = await vector_db.chroma_as_retrievers(collection_names)

        if retrievers:
            assistant_message = await llm.unified_chat(request, retrievers)
        else:
            assistant_message = await llm.unified_chat(request)

        assistant_response_message = Messages(
            chat_id=chat_id,
            role="assistant",
            content=assistant_message['response']
        )

        if assistant_response_message.content:
            # Добавляем и сохраняем сообщение
            async with async_session() as db:
                db.add(message)
                await db.commit()
                await db.refresh(message)  # Обновляем объект данными из БД
            # Добавляем и сохраняем ответ от модели
                db.add(assistant_response_message)
                await db.commit()
                await db.refresh(assistant_response_message)

        return assistant_message

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
                raise HTTPException(status_code=404, detail=f"No messages (id: {message_id}) found for (chat_id: {chat_id}).")

    async def update_chat_message(self, chat_id: int, message_id: int, request) -> str:
        """
        Обновляет сообщение в чате БД

        :param chat_id: ID чата
        :param message_id: ID сообщения
        :param request: STR новое содержимое
        :return: Результат операции
        """
        async with async_session() as db:
            message = await db.execute(
                select(Messages).where(Messages.chat_id == chat_id, Messages.id == message_id)
            )
            message = message.scalars().first()
            if message:
                message.content = request.content
                db.add(message)
                await db.commit()
                return "Сообщение успешно изменено"
            else:
                raise HTTPException(status_code=404, detail=f"No messages (id: {message_id}) found for (chat_id: {chat_id}).")
