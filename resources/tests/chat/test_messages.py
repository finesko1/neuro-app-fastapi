import pytest
from fastapi.testclient import TestClient
from app import app
import logging

client = TestClient(app)
logging.basicConfig(level=logging.INFO)

def test_chat_history():
    """
    Тестирует эндпоинт /messages/chat/{chat_id} для проверки его работы.
    """
    # Предполагаем, что chat_id 1 существует и возвращает ожидаемые данные
    response = client.get("/messages/chat/1")
    assert response.status_code == 200
    #logging.info("Testing chat history endpoint")
    logging.info(f"Response JSON: {response.json()}")
    #assert response.json() == {"message": "Expected message content"}  # Замените на ожидаемый результат

    # Тестируем случай, когда chat_id не существует
    #response = client.get("/messages/chat/9999")
    #assert response.status_code == 404
    #assert response.json() == {"detail": "Chat not found"}

if __name__ == "__main__":
    pytest.main(["-v", "test_messages.py"])