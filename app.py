from fastapi import FastAPI

app = FastAPI()

@app.get("/docs")
def read_doc():
    pass 
@app.get("/health")
def status():
    pass
@app.get("/metrics")
def metrics():
    return {"metrics":"none"}

#для сообщений
@app.post("/messages",
          summary="Cоздать сообщение")
def read_doc():
    pass 
#  Примерчик структурированного запроса
# {
#   "chat_id": "uuid",
#   "content": "Привет! Как дела?",
#   "sender"/"role": "user",
#   "metadata": {}
# }
@app.get("/messages/{message_id}",summary="Получить сообщение") 
def read_doc():
    pass 

@app.get("/messages/chat/{chat_id}",summary="Получить сообщения чата")
def chat_history():
    pass

@app.put("/messages/{message_id}",summary="обновить сообщение")
def update_message():
    pass

@app.delete("/messages/{message_id}",summary="Удалить сообщение") 
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

#Для хромы
@app.post("/chroma/collections",
          summary="Создать коллекцию")
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
@app.delete("/chroma/collections/{name}",
            summary="Удалить коллекцию")
def delete_collection():
    pass
@app.post("/chroma/collections/{name}/documents",
          summary="Добавить документ в коллекцию")
def add_to_collection():
    pass
@app.get("/chroma/collections/{name}/search",
         summary="Cемантический поиск по коллекции")
def semantic_search():
    pass

#Редис
@app.get("/cache/{key}",
         summary="Получить значение по ключу")
def get_value():
    pass
@app.post("/cache/{key}",
          summary="Установить значение")
def add_value():
    pass
@app.delete("/cache/{key}",
            summary="Удалить значене")
def delete_value():
    pass
@app.delete("/cache/invalidate",
            summary="Инвалидатор кеша (по шаблону или ключу)")
def invalidate_cache():
    pass

@app.get("/cache/stats",
         summary="Cтатистика по кешу")
def statistic_cache():
    pass