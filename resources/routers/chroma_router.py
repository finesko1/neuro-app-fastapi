from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional
from pydantic import BaseModel

from resources.controllers.llm.llm_controller import LLMController
from resources.controllers.llm.vector_db_controller import VectorDbController
from resources.models.llm.chat.chat_request import ChatRequest
from resources.models.llm.chat.document_request import DocumentChatRequest
from resources.models.llm.chroma.collection_create import CollectionCreate
from langchain_core.documents import Document

from resources.models.llm.chroma.search_query import SearchQuery


router = APIRouter()
chroma = VectorDbController()

#Для хромы
@router.post("/chroma/collections",
          summary="Создать коллекцию",
          response_description="Информация о созданной коллекции")
async def add_collection(collection_data: CollectionCreate):
    """
    Создание новой коллекции в векторной базе данных(Chromadb).

    Args:
        collection_data (CollectionCreate): Данные для создания коллекции
            - name: str - название коллекции
            - metadata: Optional[Dict] - метаданные коллекции

    Returns:
        dict: Результат операции создания коллекции
            - status: str - статус операции
            - message: str - сообщение о результате

    Raises:
        HTTPException: 
            - 409: Если коллекция уже существует
            - 500: При внутренней ошибке сервера
    """    
    response = await chroma.add_collection(collection_data)
    return response

@router.delete("/chroma/collections/{name}",
            summary="Удалить коллекцию")
async def delete_collection(collection_name:str):
    """
    Удаление коллекции из векторной базы данных.

    Args:
        collection_name (str): Название коллекции для удаления

    Returns:
        dict: Результат операции удаления
            - status: str - статус операции
            - message: str - сообщение о результате

    Raises:
        HTTPException:
            - 404: Если коллекция не найдена
            - 500: При внутренней ошибке сервера
    """
    response = await chroma.delete_collection(collection_name)
    return response

@router.post("/chroma/collections/{name}/documents",
          summary="Добавить документ в коллекцию")
async def add_to_collection(name:str, document_chunks:List[Document]):
    """
    Добавление документа в указанную коллекцию.

    Args:
        name (str): Название коллекции
        document_chunks (List[Document]): Документ для добавления
        ebbeding_model (OllamaEmbeddings): ембеддинг модель

    Returns:
        dict: Результат операции добавления
            - status: str - статус операции
            - message: str - сообщение о результате

    Raises:
        HTTPException:
            - 404: Если коллекция не найдена
            - 500: При внутренней ошибке сервера
    """
    response = await chroma.add_to_collection(name=name,document_chunks=document_chunks)
    return response

@router.post("/chroma/collections/{name}/search",
         summary="Cемантический поиск по коллекции")
async def semantic_search(name:str,search_query: SearchQuery):
    """
    Выполнение семантического поиска в указанной коллекции.

    Args:
        name (str): Название коллекции
        search_query (SearchQuery): Параметры поискового запроса
            - query: str - текст запроса
            - n_results: int - количество результатов (по умолчанию 5)

    Returns:
        dict: Результаты поиска
            - status: str - статус операции
            - results: List - найденные документы

    Raises:
        HTTPException:
            - 404: Если коллекция не найдена
            - 500: При внутренней ошибке сервера
    """
    response = await chroma.semantic_search(name=name,search_query=search_query)
    return response