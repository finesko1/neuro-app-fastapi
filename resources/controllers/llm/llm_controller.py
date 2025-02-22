"""Класс контроллер отвечающий за работу с языковыми моделями посредствам подключения к олламе
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

import logging
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import OllamaEmbeddings
from resources.helpers.environment_helper import EnvironmentHelper

logger = logging.basicConfig(level=logging.INFO)
class LLMController:
    def __init__(self):
        self.env = EnvironmentHelper()
        self.ollama_url = self.env.ollama_url
        self.model_name = self.env.ollama_model
        self.llm = ChatOllama(model=self.model_name,base_url=self.ollama_url)
        self.llm_embenndings = OllamaEmbeddings(model=self.env.ollama_embedding_model, base_url= self.ollama_url)
    
    def get_query_prompt(self) -> PromptTemplate:
        """Геттер для промпта для поиска в векторной базе данных при использовании ее как объекта."""
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
    