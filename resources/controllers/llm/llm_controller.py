"""Класс контроллер отвечающий за работу с языковыми моделями посредством подключения к олламе
    TODO:
        Реализовать логику работы с чатами в формате получения сообщений в виде:
            {
                {
                    "role": "user/assistant/system",
                    "content": "...",
                    "...": "..."
                }
            }
"""
from typing import Dict, List

from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import OllamaEmbeddings
from starlette.responses import JSONResponse

from resources.helpers.environment_helper import EnvironmentHelper
import requests

class LLMController:
    def __init__(self):
        self.env = EnvironmentHelper()
        self.ollama_url = self.env.ollama_url
        self.model_name = self.env.ollama_model
        self.llm = ChatOllama(model=self.model_name,base_url=self.ollama_url)
        self.llm_embenndings = OllamaEmbeddings(model=self.env.ollama_embedding_model, base_url= self.ollama_url)
    
    def get_query_prompt(self) -> PromptTemplate:
        """Геттер для получения промпта при поиске в векторной базе данных."""
        return PromptTemplate(
            input_variables=["question"],
            template="""Вы - ассистент языковой модели искусственного интеллекта.
            Ваша задача - сгенерировать 2 различные версии заданного пользователем вопроса, чтобы извлечь соответствующие этому вопросу документы из векторной базы данных.
            Генерируя несколько вариантов вопроса пользователя, вы должны помочь ему преодолеть некоторые ограничения поиска по сходству на основе расстояния.
            Предоставьте эти альтернативные вопросы, разделенные новыми строками. 
            Оригинальный вопрос: {question}""",
        )
    
    def get_rag_prompt(self) -> ChatPromptTemplate:
        """Геттер для промпта раг запроса."""
        template = """Ответьте на вопрос, основываясь ТОЛЬКО на следующем контексте:
        {context}
        Вопрос: {question}
        """
        return ChatPromptTemplate.from_template(template) 

    def get_models(self) -> List:
        """
        Поиск моделей для генерации ответа

        :return: Список моделей для генерации ответа
        """
        url = self.env.ollama_url + '/api/tags'  # URL для запроса
        try:
            response = requests.get(url)  # Выполняем GET-запрос
            response.raise_for_status()  # Проверяем на наличие ошибок
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=404, detail=f"Ошибка при выполнении запроса: {e}")

        # Отбор названий моделей
        models = response.json()
        model_names = []
        for model in models['models']:
            if model['name'] != 'nomic-embed-text:latest':
                model_names.append({"name": model['name']})
        # Проверка наличия моделей
        if not model_names:
            raise HTTPException(status_code=404, detail="Модели не загружены")
        return model_names

    def get_embedding_models(self):
        """
        Поиск моделей для генерации embeddings

        :return: Список моделей для генерации embeddings
        """
        url = self.env.ollama_url + '/api/tags'  # URL для запроса
        try:
            response = requests.get(url)  # Выполняем GET-запрос
            response.raise_for_status()  # Проверяем на наличие ошибок
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=404, detail=f"Ошибка при выполнении запроса: {e}")

        # Список существующих моделей
        existing_embedding_models = [
            "mxbai-embed-large",
            "nomic-embed-text",
            "all-minilm"
        ]

        # Отбор существующих моделей для генерации
        models = response.json()
        embedding_models = []
        # Проверяем каждую полученную модель
        for model in models['models']:
            # Проверяем, начинается ли имя модели с любого из ожидаемых
            for existing_model in existing_embedding_models:
                if model['name'].startswith(existing_model):
                    embedding_models.append({"name": model['name']})
                    break

        # Проверка наличия моделей
        if not embedding_models:
            raise HTTPException(status_code=404, detail="Модели для генерации embeddings не найдены")

        return embedding_models