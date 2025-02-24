
from typing import Dict
from fastapi import APIRouter, HTTPException,status
from fastapi.responses import JSONResponse

from resources.controllers.llm.llm_controller import LLMController
from resources.controllers.llm.vector_db_controller import VectorDbController
from resources.models.llm.chat.chat_request import ChatRequest
from resources.models.llm.chat.document_request import DocumentChatRequest


router = APIRouter()
llm = LLMController()

#llm генерация 
@router.post("/chat", response_model=Dict, summary="Чат на основе массива сообщений")
async def chat(request: ChatRequest):
    """
    Endpoint для чата с поддержкой контекста.

    Args:
        request (ChatRequest): Запрос с историей сообщений и опциональным системным промптом

    Returns:
        Dict: Ответ модели и обновленная история сообщений
    """
    return await llm.chat(request)
    # return await llm.chat(
    #     messages=[msg.model_dump() for msg in request.messages],
    #     system_prompt=request.system_prompt
    # )

@router.post("/chat/document", summary="Чат с RAG")
async def chat_with_document(request: DocumentChatRequest):
    """
    Endpoint для чата с контекстом из документа.

    Args:
        request (DocumentChatRequest): Запрос с вопросом и названием коллекции

    Returns:
        Dict: Ответ модели с учетом контекста документа
    """
    vector_db = VectorDbController()
    try:
        retriever = await vector_db.chroma_as_retrievers(request.collection_names)
        response = await llm.chat_with_pdf(request.question, retriever)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
#Для ЛЛМ
@router.post("/llm/generate",
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

@router.get("/llm/models",summary="Список моделей")
async def models_list():
    models = await llm.get_models()
    if models:
        # {message: "LLM models get successfully", models: [{name: "qwen2.5:3b"}, {"name: deepseek-r1:1.5b"}]}
        return JSONResponse(content={
            "message": "LLM models get successfully",
            "models": models}, status_code=200)
    else:
        return JSONResponse(content={"message": "LLM models get failed"}, status_code=404)


#для эмбедингов
@router.post("/embeddings",
          summary="Генерация  эмбединга для сообщения")
def embeddings():
   pass

@router.get("/embeddings/models",
         summary="Cписок моделей для генерации эмбеддингов")
def embedding_models_list():
    embedding_models = llm.get_embedding_models()
    if embedding_models:
        return JSONResponse(content={
            "message": "LLM embedding models get successfully",
            "models": embedding_models}, status_code=200)
    else:
        return JSONResponse(content={"message": "LLM models get failed"}, status_code=404)