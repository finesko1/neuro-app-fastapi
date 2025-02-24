from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from langchain_core.documents import Document


from resources.controllers.llm.document_controller import DocumentController
from resources.models.llm.chroma.document_response import DocumentResponse

router = APIRouter()

#Для документов
document_controller = DocumentController()

@router.post("/files",
          summary="Загрузить документ",
          response_description="Информация о загруженном документе",
          response_model=DocumentResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Загрузка документа на сервер.

    Args:
        file (UploadFile): Загружаемый файл (PDF)

    Returns:
        DocumentResponse: Информация о загруженном документе
            - status: str - статус операции
            - message: str - сообщение о результате
            - document_id: str - идентификатор документа

    Raises:
        HTTPException: 
            - 400: Если формат файла не поддерживается
            - 500: При внутренней ошибке сервера
    """
    response = await document_controller.upload_document(file)
    return response

@router.post("/files/upload-collection")
async def upload_collection(files: List[UploadFile] = File(...)):
    response = await document_controller.upload_collection(files)
    return response

@router.get("/files/{id}/get",
         summary="Получить чанки документа",
         response_description="Список чанков документа",
         response_model=List[Document])
async def get_document_chunks(id: str):
    """
    Получение документа, разделенного на чанки.

    Args:
        id (str): Идентификатор документа

    Returns:
        List[Document]: Список чанков документа, где каждый чанк содержит:
            - page_content: str - текстовое содержимое
            - metadata: dict - метаданные чанка

    Raises:
        HTTPException:
            - 404: Если документ не найден
            - 500: При внутренней ошибке сервера
    """
    response = await document_controller.get_document_chunks(id)
    return response

@router.delete("/files/{id}",
            summary="Удалить документ",
            response_description="Информация об удалении документа",
            response_model=DocumentResponse)

async def delete_file(id: str):
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
    response = await document_controller.delete_document(id)
    return response