
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
async def unified_chat(request: ChatRequest):
    """
    Унифицированный endpoint для чата с опциональной поддержкой RAG.
    
    Если в запросе указаны флаги use_global_collection или use_local_collection,
    будет использован механизм RAG с соответствующими коллекциями.
    Args:
        request (ChatRequest): Запрос с историей сообщений, системным промптом
                              и опциональными параметрами для RAG
    
    Returns:
        Dict: Ответ модели и обновленная история сообщений
    """
# тест
# {
#           "messages": [
#             {
#                 "id": 1,
#                 "role": "user",
#                 "chat_id": 1,
#                 "content": "Ты кто?",
#                 "global_collection": null,
#                 "local_collection": null
#             },
#             {
#                 "id": 2,
#                 "role": "assistant",
#                 "chat_id": 1,
#                 "content": "Я виртуальный ассистент, созданный для помощи в ответах на вопросы и выполнения различных задач. Могу ли я чем-то помочь вам сегодня?",
#                 "global_collection": null,
#                 "local_collection": null
#             },
#             {
#                 "id": 3,
#                 "role": "user",
#                 "chat_id": 1,
#                 "content": "Какие лабораторные есть в коллекциях? ответь кратко",
#                 "global_collection": "global123",
#                 "local_collection": "test123"
#             }
#           ],
#           "system_prompt": "string",
#           "use_local_collection": true,
#           "use_global_collection": true,
#           "global_collection": "global123",
#           "local_collection": "test123"
#         }

    if request.use_global_collection or request.use_local_collection:
        vector_db = VectorDbController()
        try:
            collection_names = []
            
            if request.use_global_collection and request.global_collection:
                collection_names.append(request.global_collection)
                
            if request.use_local_collection and request.local_collection:
                collection_names.append(request.local_collection)
            
            if collection_names:
                retrievers = await vector_db.chroma_as_retrievers(collection_names)
                return await llm.unified_chat(request, retrievers)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при работе с векторной базой данных: {str(e)}"
            )
        
    return await llm.unified_chat(request)

# @router.post("/chat/document", summary="Чат с RAG")
# async def chat_with_document(request: DocumentChatRequest):
#     """
#     Endpoint для чата с контекстом из документа.

#     Args:
#         request (DocumentChatRequest): Запрос с вопросом и названием коллекции

#     Returns:
#         Dict: Ответ модели с учетом контекста документа
#     """
#     vector_db = VectorDbController()
#     try:
#         retriever = await vector_db.chroma_as_retrievers(request.collection_names)
#         response = await llm.chat_with_pdf(request.question, retriever)
#         return {"response": response}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
    

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