
from typing import List
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from langchain_ollama import OllamaEmbeddings
from sqlalchemy import text
from database.connect import session
from resources.controllers.chat.message_controller import MessageController
from resources.controllers.llm.llm_controller import LLMController
from resources.models.llm.chroma.collection_create import CollectionCreate
from resources.models.llm.chroma.search_query import SearchQuery
from resources.controllers.llm.vector_db_controller import VectorDbController
from resources.controllers.llm.document_controller import DocumentController
from resources.models.llm.chroma.document_response import DocumentResponse
from langchain_core.documents import Document

app = FastAPI(
    title="Neuro API",
    description="API for Neuro App",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
messages = MessageController()
chroma = VectorDbController()
document_controller = DocumentController()
llm = LLMController()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/docs")
def read_doc():
    pass

@app.get("/health")
def status():
    try:
        with session() as db:
            result = db.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            ).fetchall()

            tables = [row[0] for row in result]
            return {"db": "connected", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    pass


@app.get("/chats/{chat_id}/messages", response_model=list, summary="Получить сообщения чата")
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

@app.post("/chats/{chat_id}/messages", summary="Cоздать сообщение в чате")
def send_message(chat_id: int):
    """
    Отправление сообщения на сервер.

    :param chat_id:
    :return: Код состояния
    """

@app.get("/chats/{chat_id}/messages/{message_id}",summary="Получить сообщение чата")
def get_message_by_chat(chat_id: int, message_id: int) -> dict:
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
    return response

@app.post("/chats/{chat_id}/messages/{message_id}",summary="Обновить сообщение чата")
def update_message():
    pass

@app.delete("/chats/{chat_id}/messages/{message_id}",summary="Удалить сообщение чата")
def delete_message():
    pass


#Для ЛЛМ
@app.post("/llm/generate",
          summary="Генерация ответа")
def generate():
    pass
#  Примерчик структурированного запроса
# {
#   "prompt": "Как работает гравитация?",
#   "context": ["предыдущие сообщения"],
#   "params": {
#     "temperature": 0.7,
#     "max_tokens": 500,
#      ...
#   }
# }
# 

@app.post("/llm/switch-model",
          summary="Cменить модель")
def switch_model():
    pass

@app.get("/llm/models",summary="Список моделей")
def models_list():
    pass

#для эмбедингов
@app.post("/embeddings",
          summary="Генерация  эмбединга для сообщения")
def embeddings():
    pass
#  Примерчик структурированного запроса
# {
#   "texts": ["текст 1", "текст 2"],
#   "model": "all-MiniLM-L12-v2"
# }

@app.get("/embeddings/models",
         summary="Cписок моделей для генерации эмбеддингов")
def embedding_models_list():
    pass
#Для документов

@app.post("/files",
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

@app.get("/files/{id}/get",
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

@app.delete("/files/{id}",
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

#Для хромы
@app.post("/chroma/collections",
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

@app.delete("/chroma/collections/{name}",
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

@app.post("/chroma/collections/{name}/documents",
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

@app.post("/chroma/collections/{name}/search",
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

@app.post("/test/add-doc")
async def test():
    """Тестовый метод

    Returns:
        Возвращает добавленные в хрому документы, далее можно семантический поиск выполнить
    """    
    chunks = await get_document_chunks("лаб3трпо.pdf")
    response = await chroma.add_to_collection(name="test123",document_chunks=chunks)
    return response
