from fastapi import APIRouter, HTTPException
from resources.controllers.llm.vector_db_controller import VectorDbController
from resources.routers.files_router import get_document_chunks
from sqlalchemy import text
from database.connect import session

router = APIRouter()

@router.get("/")
def read_root():
    return {"I have": "nothing!!!"}

@router.get("/docs")
def read_doc():
    pass

@router.get("/health", summary="Проверка состояния подключения к БД")
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

@router.get("/metrics")
def metrics():
    pass


#тест
chroma = VectorDbController()
@router.post("/test/add-doc")
async def test():
    """Тестовый метод

    Returns:
        Возвращает добавленные в хрому документы, далее можно семантический поиск выполнить
    """    
    chunks = await get_document_chunks("___ __1.pdf")
    response = await chroma.add_to_collection(name="test123",document_chunks=chunks)
    return response