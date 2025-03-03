import logging
import os
import re
import mimetypes
from pathlib import Path
from typing import List, Optional
import uuid
from fastapi import HTTPException, status, UploadFile, Request
from fastapi.responses import FileResponse, JSONResponse
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, CSVLoader, \
    UnstructuredXMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.future import select
from database.connect import async_session
from resources.models.llm.chroma.document_response import DocumentResponse
from resources.models.chat.document import UploadFilesModel
from langchain.docstore.document import Document

logger = logging.getLogger(__name__)


class DocumentController:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {'.pdf', '.docx', '.csv', '.xml'}
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

        # Регистрируем MIME типы для корректной отдачи файлов
        if not mimetypes.guess_type('file.pdf')[0]:
            mimetypes.add_type('application/pdf', '.pdf')
        if not mimetypes.guess_type('file.docx')[0]:
            mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')
        if not mimetypes.guess_type('file.csv')[0]:
            mimetypes.add_type('text/csv', '.csv')
        if not mimetypes.guess_type('file.xml')[0]:
            mimetypes.add_type('application/xml', '.xml')

    async def upload_documents(self, chat_id: int, files: List[UploadFile]) -> JSONResponse:
        """
        Загрузка нескольких документов на сервер.

        Args:
            chat_id (int): ID чата, к которому привязываются документы
            files (List[UploadFile]): Список загружаемых файлов

        Returns:
            JSONResponse: Информация о загруженных документах

        Raises:
            HTTPException: При ошибке загрузки файлов
        """
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не предоставлены файлы для загрузки"
            )

        uploaded_documents = []
        errors = []

        for file in files:
            try:
                file_extension = Path(file.filename).suffix.lower()

                if file_extension not in self.allowed_extensions:
                    errors.append(f"Файл {file.filename} не поддерживается. Разрешены только PDF, DOCX, CSV, XML")
                    continue

                document_id = str(uuid.uuid4())
                saved_filename = f"{document_id}{file_extension}"
                file_path = self.upload_dir / saved_filename

                # Чтение содержимого файла
                content = await file.read()

                # Запись файла на диск
                with open(file_path, "wb") as buffer:
                    buffer.write(content)

                # Сохранение информации о файле в базе данных
                async with async_session() as db:
                    new_document = UploadFilesModel(
                        chat_id=chat_id,
                        path=str(file_path),
                        original_name=file.filename,
                    )
                    db.add(new_document)
                    await db.commit()
                    await db.refresh(new_document)  # Получаем ID созданной записи

                # Добавляем информацию о загруженном документе
                uploaded_documents.append({
                    "id": new_document.id,
                    "original_name": file.filename,
                    "file_extension": file_extension
                })

            except Exception as e:
                errors.append(f"Ошибка при загрузке файла {file.filename}: {str(e)}")

        # Формируем ответ
        response_data = {
            "status": "success" if uploaded_documents else "error",
            "message": f"Загружено {len(uploaded_documents)} файлов" if uploaded_documents else "Не удалось загрузить файлы",
            "documents": uploaded_documents
        }

        if errors:
            response_data["errors"] = errors

        status_code = status.HTTP_201_CREATED if uploaded_documents else status.HTTP_400_BAD_REQUEST

        return JSONResponse(content=response_data, status_code=status_code)

    async def get_documents_list(self,chat_id:int):
        # Поиск документов в БД
        async with async_session() as db:
            response = await db.execute(select(UploadFilesModel).where(UploadFilesModel.chat_id == chat_id))
            documents_info = response.scalars().fetchall()

        # Проверка наличия документов
        if not documents_info:
            raise HTTPException(status_code=404, detail="Documents not found")

        # Формирование списка документов с информацией
        documents = []
        for document in documents_info:
            # Получаем расширение файла для определения типа
            file_extension = Path(document.original_name).suffix.lower()

            documents.append({
                "id": document.id,
                "chat_id": document.chat_id,
                "path": document.path,
                "original_name": document.original_name,
                "file_extension": file_extension
            })

        return documents
    async def get_documents(self, chat_id: int):
        """
        Получение списка документов для указанного чата.

        Args:
            chat_id (int): ID чата

        Returns:
            JSONResponse: Список документов

        Raises:
            HTTPException: Если документы не найдены
        """
        # Поиск документов в БД
        async with async_session() as db:
            response = await db.execute(select(UploadFilesModel).where(UploadFilesModel.chat_id == chat_id))
            documents_info = response.scalars().fetchall()

        # Проверка наличия документов
        if not documents_info:
            raise HTTPException(status_code=404, detail="Documents not found")

        # Формирование списка документов с информацией
        documents = []
        for document in documents_info:
            # Получаем расширение файла для определения типа
            file_extension = Path(document.original_name).suffix.lower()

            documents.append({
                "id": document.id,
                "chat_id": document.chat_id,
                "path": document.path,
                "original_name": document.original_name,
                "file_extension": file_extension
            })

        # Возвращаем информацию о документах в формате JSON
        return JSONResponse(
            content={"documents": documents},
            status_code=status.HTTP_200_OK
        )

    async def get_document(self, chat_id: int, document_id: int):
        """
        Получение конкретного документа по его ID.

        Args:
            chat_id (int): ID чата
            document_id (int): ID документа
            request (Request, optional): Объект запроса FastAPI
            inline (bool, optional): Флаг для отображения файла в браузере (True) или скачивания (False)

        Returns:
            FileResponse: Файл для просмотра или скачивания

        Raises:
            HTTPException: Если документ не найден
        """
        # Поиск документа в БД
        async with async_session() as db:
            response = await db.execute(
                select(UploadFilesModel).where(UploadFilesModel.id == document_id).where(
                    UploadFilesModel.chat_id == chat_id)
            )
            document = response.scalars().first()

        # Проверка наличия документа
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Проверка существования файла
        file_path = Path(document.path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on server")

        # Отправляем файл клиенту
        return FileResponse(
            path=file_path,
            filename=document.original_name
        )

    async def get_document_chunks(self, document_path: str) -> List[Document]:
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
            file_path = document_path

            # for ext in self.allowed_extensions:
            #     possible_path = self.upload_dir / f"{document_id}{ext}"
            #     if possible_path.exists():
            #         file_path = possible_path
            #         break

            if not file_path:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Документ {document_path} не найден"
                )

            pattern = r'(\.[^.]+)$'
            match = re.search(pattern, file_path)
            file_extension = match.group(1)

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

    async def delete_document(self, chat_id: int, document_id: int):
        """
        Удаление документа с сервера.

        Args:
            chat_id (int): ID чата
            document_id (int): Идентификатор документа

        Returns:
            DocumentResponse: Результат удаления

        Raises:
            HTTPException: Если документ не найден или при ошибке удаления
        """
        try:
            async with async_session() as db:
                result = await db.execute(
                    select(UploadFilesModel).
                    where(UploadFilesModel.id == document_id).
                    where(UploadFilesModel.chat_id == chat_id)
                )
                document = result.scalars().first()

            # Проверка наличия документа
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            # Удаление файла с диска
            file_path = Path(document.path)
            if file_path.exists():
                os.remove(file_path)  # Удаляем файл

            # Удаление записи из базы данных
            async with async_session() as db:
                await db.delete(document)
                await db.commit()

            return {"detail": "Document deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при удалении документа: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении документа: {str(e)}"
            )