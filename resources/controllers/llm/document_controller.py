"""Контроллер для управления документами через API."""
import logging
import os
from pathlib import Path
from typing import List
import uuid
from fastapi import HTTPException, status, UploadFile
from langchain_community.document_loaders import UnstructuredPDFLoader, PyPDFLoader, CSVLoader, UnstructuredWordDocumentLoader, UnstructuredXMLLoader
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
        self.allowed_extensions = {'.pdf', '.docx', '.csv', '.xml'}
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
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in self.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поддерживаются только файлы PDF, DOCX, CSV, XML"
                )

            document_id = str(uuid.uuid4())
            saved_filename = f"{document_id}{file_extension}"
            file_path = self.upload_dir / saved_filename

            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            return DocumentResponse(
                status="success",
                message="Документ успешно загружен",
                document_id=document_id,
                original_name=file.filename,
                file_extension=file_extension
            )

        except HTTPException:
            raise
        except Exception as e:
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

            # for ext in self.allowed_extensions:
            #     possible_path = self.upload_dir / f"{document_id}{ext}"
            #     if possible_path.exists():
            #         file_path = possible_path
            #         break

            if not file_path:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Документ {document_id} не найден"
                )

            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_extension == '.docx':
                loader = UnstructuredWordDocumentLoader(str(file_path))
            elif file_extension == '.csv':
                loader = CSVLoader(str(file_path))
            elif file_extension == '.xml':
                loader = UnstructuredXMLLoader(str(file_path))
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неподдерживаемый формат файла"
                )

            documents = loader.load()
            return self.splitter.split_documents(documents)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обработки документа: {str(e)}"
            )

    async def upload_collection(self, files: List[UploadFile]) -> List[DocumentResponse]:
        """
        Загрузка коллекции документов с сохранением структуры папок.

        Args:
            files (List[UploadFile]): Список загружаемых файлов

        Returns:
            List[DocumentResponse]: Список результатов загрузки для каждого файла

        Raises:
            HTTPException: При общих ошибках сервера
        """
        responses = []
        for file in files:
            try:
                if not file.filename.lower().endswith('.pdf'):
                    responses.append(DocumentResponse(
                        status="error",
                        message="Поддерживаются только PDF файлы",
                        document_id=file.filename
                    ))
                    continue

                file_path = (self.upload_dir / file.filename).resolve()

                if not file_path.is_relative_to(self.upload_dir.resolve()):
                    responses.append(DocumentResponse(
                        status="error",
                        message="Недопустимый путь файла",
                        document_id=file.filename
                    ))
                    continue

                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                responses.append(DocumentResponse(
                    status="success",
                    message="Документ успешно загружен",
                    document_id=file.filename
                ))

            except Exception as e:
                logger.error(f"Ошибка загрузки {file.filename}: {str(e)}")
                responses.append(DocumentResponse(
                    status="error",
                    message=f"Ошибка: {str(e)}",
                    document_id=file.filename
                ))
        
        return responses

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