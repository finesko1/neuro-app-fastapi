from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connect import get_db

# Импорт моделей из существующих файлов
# Предполагается, что моделей Chat и Message (как в Snippet #1 и #2) вы уже создали
from resources.models.chat.chat import Chat
from resources.models.chat.message import Message
from resources.controllers.chat.message_controller import get_chat_messages

app = FastAPI()

@app.get("/docs")
def read_doc():
    pass 
@app.get("/health")
def status():
    pass
@app.get("/metrics")
def metrics():
    pass
#для сообщений
@app.post("/messages") #создать сообщение
def read_doc():
    pass 
#  Примерчик структурированного запроса
# {
#   "chat_id": "uuid",
#   "content": "Привет! Как дела?",
#   "sender"/"role": "user",
#   "metadata": {}
# }
@app.get("/messages/{message_id}") #получить сообщение
def read_doc():
    pass 

@app.get("/messages/chat/{chat_id}", response_model=list) # получение сообщений чата
def get_messages_by_chat(chat_id: int):
    """
    Получение списка сообщений по chat_id.
    """
    response = get_chat_messages(chat_id)
    return response

@app.put("/messages/{message_id}") #обновить сообщение
def update_message():
    pass

@app.delete("/messages/{message_id}") #удалить сообщение
def delete_message():
    pass


#Для ЛЛМ
@app.post("/llm/generate") #генерация ответа
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

@app.post("/llm/switch-model") #сменить модель
def switch_model():
    pass

@app.get("/llm/models") #список моделей
def models_list():
    pass

#для эмбедингов
@app.post("/embeddings") #генерация  эмбединга для сообщения
def embeddings():
    pass
#  Примерчик структурированного запроса
# {
#   "texts": ["текст 1", "текст 2"],
#   "model": "all-MiniLM-L12-v2"
# }

@app.get("/embeddings/models") #список моделей для генерации эмбеддингов
def embedding_models_list():
    pass

#Для хромы
@app.post("/chroma/collections") #cоздать коллекцию
def add_collection():
    pass
#  Примерчик структурированного запроса
# {
#   "name": "science_articles",
#   "metadata": {
#     "description": "Научные статьи по физике",
#     "embedding_model": "all-MiniLM-L6-v2"
#   }
# }
@app.delete("/chroma/collections/{name}") #удалить коллекцию
def delete_collection():
    pass
@app.post("/chroma/collections/{name}/documents") #добавить документ в коллекцию
def add_to_collection():
    pass
@app.get("/chroma/collections/{name}/search") #семантический поиск по коллекции
def semantic_search():
    pass

#Редис
@app.get("/cache/{key}") #получить значение по ключу
def get_value():
    pass
@app.post("/cache/{key}") #установить значение
def add_value():
    pass
@app.delete("/cache/{key}") #удалить значене
def delete_value():
    pass
@app.delete("/cache/invalidate") #инвалидатор кеша (по шаблону или ключу)
def invalidate_cache():
    pass

@app.get("/cache/stats") #статистика по кешу
def statistic_cache():
    pass