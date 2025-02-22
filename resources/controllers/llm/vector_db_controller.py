"""Функционал для работы с векторными вложениями и базой данных."""
import logging
from typing import List
import chromadb.errors
from fastapi import HTTPException, status
import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from resources.models.llm.chroma.collection_create import CollectionCreate
from resources.models.llm.chroma.search_query import SearchQuery
from langchain_core.documents import Document

from resources.helpers.environment_helper import EnvironmentHelper

logger = logging.basicConfig(level=logging.INFO)

class VectorDbController:
    """Класс для работы с векторной базой данных Chroma."""
    
    def __init__(self):
        """
        Инициализация клиента Chroma и модели эмбеддингов.

        Args:
            embedding_model (str): Название модели для создания эмбеддингов
        """
        self.env = EnvironmentHelper()
        self.chroma_client = chromadb.HttpClient(
            host=self.env.chroma_host,
            port=self.env.chroma_port
        )
        self.embeddings = OllamaEmbeddings(base_url = self.env.ollama_url, model=self.env.ollama_embedding_model)

    async def add_collection(self, collection_data: CollectionCreate):
        """
        Создание новой коллекции в векторной базе данных.

        Args:
            collection_data (CollectionCreate): Данные для создания коллекции

        Returns:
            tuple: Словарь с результатом операции и HTTP статус

        Raises:
            HTTPException: При ошибке создания коллекции
        """
        try:
            collection = self.chroma_client.create_collection(
                name=collection_data.name,
                metadata=collection_data.metadata
            )
            return {
                "status": "success",
                "message": f"Коллекция {collection_data.name} успешно создана"
            }, status.HTTP_201_CREATED
        except chromadb.errors.DuplicateIDError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Коллекция {collection_data.name} уже существует"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания коллекции: {str(e)}"
            )

    async def delete_collection(self, name: str):
        """
        Удаление коллекции из векторной базы данных.

        Args:
            name (str): Название коллекции для удаления

        Returns:
            tuple: Словарь с результатом операции и HTTP статус

        Raises:
            HTTPException: При ошибке удаления коллекции
        """
        try:
            self.chroma_client.delete_collection(name=name)
            return {
                "status": "success",
                "message": f"Коллекция {name} успешно удалена"
            }, status.HTTP_200_OK
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Коллекция {name} не найдена"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка удаления коллекции: {str(e)}"
            )

    async def add_to_collection(self, name: str, document_chunks: List[Document]):
        """
        Добавление документа в указанную коллекцию.

        Args:
            name (str): Название коллекции
            document_chunks (List[Document]): Документ поделенный на чанки
            оптимально: embedding_model:OllamaEmbeddings сделать выбор модели для генерации ембеддингов

        Returns:
            tuple: Словарь с результатом операции и HTTP статус

        Raises:
            HTTPException: При ошибке добавления документа
        """
        try:
            vectorstore = Chroma.from_documents(
                documents=document_chunks,
                collection_name=name,
                client=self.chroma_client,
                embedding=self.embeddings
            )
            return {
                "status": "success",
                "message": "Документ успешно добавлен",
                "test vec": f"chroma collection vectors: {self.chroma_client.get_collection(name).get()}"
            }, status.HTTP_201_CREATED
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Коллекция {name} не найдена"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка добавления документа: {str(e)}"
            )

    async def semantic_search(self, name: str, search_query: SearchQuery):
        """
        Выполнение семантического поиска в указанной коллекции.

        Args:
            name (str): Название коллекции
            search_query (SearchQuery): Параметры поискового запроса

        Returns:
            tuple: Словарь с результатами поиска и HTTP статус

        Raises:
            HTTPException: При ошибке выполнения поиска
        """
        try:
            results = Chroma(collection_name=name,
                                   client=self.chroma_client,embedding_function=self.embeddings).similarity_search(query=search_query.query,
                                                                                 k = search_query.n_results)
            return {
                "status": "success",
                "results": results
            }, status.HTTP_200_OK
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Коллекция {name} не найдена"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка выполнения поиска: {str(e)}"
            )
        