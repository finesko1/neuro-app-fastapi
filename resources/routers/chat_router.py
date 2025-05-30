from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse

from resources.controllers.chat.message_controller import MessageController
from resources.models.llm.chat.chat_request import ChatRequest
from resources.models.llm.chat.message import Message
router = APIRouter()
messages = MessageController()
#круд
@router.get("/chats/{chat_id}/messages", response_model=list, summary="Получить сообщения чата")
def get_messages_by_chat(chat_id: int):
    """
    Получение списка сообщений по chat_id.

    :param chat_id: Идентификатор чата.
    :type int

    :return: Сообщения чата
    rtype: list
    """
    response = messages.get_chat_messages(chat_id)
    return response

@router.post("/chats/{chat_id}/messages", summary="Cоздать сообщение в чате")
async def send_message(chat_id: int, request: ChatRequest) -> JSONResponse:
    """
    Отправление сообщения на сервер.

    :param chat_id: ID чата
    :param request: Объект запроса
    :return: Результат, код состояния
    """
    response = await messages.put_chat_message(chat_id, request)

    return JSONResponse(content={"message": response["response"]}, status_code=201)

@router.post("/chats/{chat_id}/survey_messages", summary="Cоздать сообщение в чате")
async def send_message(chat_id: int, request: ChatRequest) -> JSONResponse:
    """
    Отправление сообщения на сервер.

    :param chat_id: ID чата
    :param request: Объект запроса
    :return: Результат, код состояния
    """
    response = await messages.put_chat_message_survey(chat_id, request)

    return JSONResponse(content={"message": response["response"]}, status_code=201)

@router.get("/chats/{chat_id}/messages/{message_id}",summary="Получить сообщение чата")
def get_message_by_chat(chat_id: int, message_id: int) -> JSONResponse:
    """
    Получение сообщения по chat_id

    :param chat_id: Идентификатор чата.
    :type int

    :param message_id: Идентификатор сообщения.
    :type int
    :return: Сообщение id из чата chat_id
    rtype: dict
    """
    response = messages.get_chat_message(chat_id, message_id)
    return JSONResponse(content={"message": response}, status_code=200)


@router.delete("/chats/{chat_id}/messages/{message_id}",summary="Удалить сообщение чата")
async def delete_message(chat_id: int, message_id: int):
    """
    Удаление сообщения на сервере.

    :param chat_id: ID чата
    :param message_id: ID сообщения
    :return: Код состояния
    """
    response = await messages.delete_chat_message(chat_id, message_id)
    return Response(status_code=204)


@router.patch("/chats/{chat_id}/messages/{message_id}",summary="Обновить сообщение чата")
async def update_message(chat_id: int, message_id: int, request: Message) -> Response:
    """
    Обновление сообщения на сервере.

    :param chat_id: ID чата
    :param message_id: ID сообщения
    :return: Код состояния
    """
    response = await messages.update_chat_message(chat_id, message_id, request)
    return Response(status_code=204)