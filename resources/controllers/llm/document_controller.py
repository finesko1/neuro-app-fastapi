"""Контроллер для управления документами через API."""
import logging
import os
from pathlib import Path
from typing import List
from fastapi import HTTPException, status, UploadFile
from langchain_community.document_loaders import UnstructuredPDFLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from resources.models.llm.chroma.document_response import DocumentResponse

logger = logging.getLogger(__name__)

class DocumentController:
    """Контроллер для загрузки, обработки и удаления документов."""
    
    def __init__(self, upload_dir: str = "uploads"):
        """
        Инициализация контроллера.
        
        Args:
            upload_dir (str): Путь к директории для загрузки файлов
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
    
    async def upload_document(self, file: UploadFile) -> DocumentResponse:
        """
        Загрузка документа на сервер.
        
        Args:
            file (UploadFile): Загружаемый файл
            
        Returns:
            DocumentResponse: Информация о загруженном документе
            
        Raises:
            HTTPException: При ошибке загрузки файла
        """
        try:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поддерживаются только PDF файлы"
                )
            
            file_path = self.upload_dir / file.filename
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            return DocumentResponse(
                status="success",
                message="Документ успешно загружен",
                document_id=file.filename
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка загрузки документа: {str(e)}"
            )
    
    async def get_document_chunks(self, document_id: str) -> List[Document]:
        """
        Разделение документа на чанки.
        
        Args:
            document_id (str): Идентификатор документа
            
        Returns:
            List[Document]: Список чанков документа
            
        Raises:
            HTTPException: Если документ не найден или при ошибке обработки
        """
        try:
            file_path = self.upload_dir / document_id

            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Документ {document_id} не найден"
                )
            
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            
            # Делим на чанки
            chunks = self.splitter.split_documents(documents)
            
            logger.info(f"Документ {document_id} успешно разделен на {len(chunks)} чанков")
            return chunks
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при обработке документа: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при разделении документа на чанки: {str(e)}"
            )

    async def delete_document(self, document_id: str) -> DocumentResponse:
        """
        Удаление документа с сервера.
        
        Args:
            document_id (str): Идентификатор документа
            
        Returns:
            DocumentResponse: Результат удаления
            
        Raises:
            HTTPException: Если документ не найден или при ошибке удаления
        """
        try:
            file_path = self.upload_dir / document_id
            
            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Документ {document_id} не найден"
                )
            
            os.remove(file_path)
            
            return DocumentResponse(
                status="success",
                message=f"Документ {document_id} успешно удален"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при удалении документа: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении документа: {str(e)}"
            )