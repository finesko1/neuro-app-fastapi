from typing import List, Annotated
from fastapi import APIRouter, File, UploadFile, Request

from fastapi.responses import JSONResponse
from resources.controllers.llm.document_controller import DocumentController
from resources.models.llm.chroma.document_response import DocumentResponse

router = APIRouter()

#Для документов
document_controller = DocumentController()

@router.get("/files/{chat_id}", summary="Получение документов")
async def get_files(chat_id: int):
    response = await document_controller.get_documents(chat_id)
    return response

@router.post("/files/{chat_id}", summary="Загрузить документ")
async def upload_files(chat_id: int, files: Annotated[List[UploadFile], File(description="Файлы для загрузки")]):
    """
    Загрузка документов на сервер.

    Args:
        chat_id (int): ID чата
        files (List[UploadFile]): Список файлов для загрузки

    Returns:
        JSONResponse: Информация о загруженных документах
    """
    response = await document_controller.upload_documents(chat_id, files)
    return response


@router.post("/files/upload-collection")
async def upload_collection(files: List[UploadFile] = File(...)):
    response = await document_controller.upload_collection(files)
    return response


@router.get("/files/{chat_id}/{document_id}", summary="Получение документа")
async def get_file(
        chat_id: int,
        document_id: int,
):
    """
    Получение документа по его ID.

    Args:
        chat_id (int): ID чата
        document_id (int): Идентификатор документа

    Returns:
        FileResponse: Файл для просмотра или скачивания

    Raises:
        HTTPException:
            - 404: Если документ не найден
            - 500: При внутренней ошибке сервера
    """
    response = await document_controller.get_document(chat_id, document_id)
    return response

@router.delete("/files/{chat_id}/{document_id}",
            summary="Удалить документ")
async def delete_file(chat_id: int, document_id: int):
    """
    Удаление документа с сервера.

    Args:
        id (str): Идентификатор документа

    Returns:
        DocumentResponse: Результат удаления документа
            - status: str - статус операции
            - message: str - сообщение о результате

    Raises:
        HTTPException:
            - 404: Если документ не найден
            - 500: При внутренней ошибке сервера
    """
    response = await document_controller.delete_document(chat_id, document_id)
    return response