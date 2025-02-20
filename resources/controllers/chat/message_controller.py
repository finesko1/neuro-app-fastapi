# from sqlalchemy.orm import Session
# from chat import Chat
# from message import Message

# def get_chat_messages(chat_id: int) -> list[Message]:
#     """
#     Получает все сообщения для заданного чата из базы данных.

#     :param session: Сессия SQLAlchemy для выполнения запросов.
#     :type session: Session
#     :param chat_id: Число, представляющее уникальный идентификатор чата.
#     :type chat_id: int
#     :return: Список объектов Message, связанных с переданным chat_id.
#     :rtype: list[Message]
#     :raises ValueError: Если сообщения для чата с указанным идентификатором не найдены.
#     """
#     chat = session.query(Chat).filter(Chat.id == chat_id).one_or_none()
#     if not chat:
#         raise ValueError("Chat not found")

#     return chat.messages