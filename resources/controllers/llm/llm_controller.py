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
from typing import Any, Dict, List, Optional
from langchain.retrievers.multi_query import MultiQueryRetriever
from fastapi import HTTPException, status
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import OllamaEmbeddings
import ollama
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain.retrievers import EnsembleRetriever

from starlette.responses import JSONResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from resources.helpers.environment_helper import EnvironmentHelper
import requests

from resources.models.llm.chat.chat_request import ChatRequest

EXITING_EMBEDDINGS_MODELS = [
   "nomic-embed-text",
    "mxbai-embed-large",
    "snowflake-arctic-embed",
    "bge-m3",
    "all-minilm",
    "bge-large",
    "paraphrase-multilingual",
    "snowflake-arctic-embed2",
    "granite-embedding"
]

QUERY_PROMPT=PromptTemplate(
            input_variables=["question"],
            template="""Вы - ассистент языковой модели искусственного интеллекта.
            Ваша задача - сгенерировать 2 различные версии заданного пользователем вопроса, чтобы извлечь соответствующие этому вопросу документы из векторной базы данных.
            Генерируя несколько вариантов вопроса пользователя, вы должны помочь ему преодолеть некоторые ограничения поиска по сходству на основе расстояния.
            Предоставьте эти альтернативные вопросы, разделенные новыми строками. 
            Оригинальный вопрос: {question}""",
        )

RAG_TEMPLATE= """Ответьте на вопрос, основываясь ТОЛЬКО на следующем контексте:
{context}
Вопрос: {question}
"""


class LLMController:
    def __init__(self):
        self.env = EnvironmentHelper()
        self.ollama_url = self.env.ollama_url
        self.model_name = self.env.ollama_model
        self.ollama_client = ollama.Client(host=self.ollama_url)
        self.llm = ChatOllama(model=self.model_name,base_url=self.ollama_url)
        self.llm_embenndings = OllamaEmbeddings(model=self.env.ollama_embedding_model, base_url= self.ollama_url)
    

    async def unified_chat(self, request: ChatRequest, vector_retrievers: Optional[List[Any]] = None) -> Dict:
        """
        Унифицированный метод чата с опциональной поддержкой RAG.
    
        Args:
            request (ChatRequest): Запрос чата с сообщениями и настройками
            vector_retrievers (Optional[List[Any]]): Список ретриверов для RAG (если используется)
    
        Returns:
            Dict: Ответ модели с сохранением контекста
    
        Raises:
            HTTPException: При ошибке генерации ответа
        """
        try:
            # Устанавливаем модель из последнего сообщения пользователя
            self.model_name = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    self.model_name = msg.model
                    break
            if self.model_name:
                self.llm = ChatOllama(model=self.model_name, base_url=self.ollama_url)
            
            # Получаем последний вопрос пользователя
            last_user_message = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
                
            if not last_user_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не найдено сообщение пользователя"
                )
            
            # Преобразуем сообщения в формат langchain
            formatted_messages: List[BaseMessage] = []
            
            # Добавляем системный промпт если есть
            if request.system_prompt:
                formatted_messages.append(SystemMessage(content=request.system_prompt))
            
            for message in request.messages:
                if message.role == "user":
                    formatted_messages.append(HumanMessage(content=message.content))
                elif message.role == "assistant":
                    formatted_messages.append(AIMessage(content=message.content))
            
            # Определяем, нужно ли использовать RAG
            use_rag = vector_retrievers is not None and len(vector_retrievers) > 0
            
            if use_rag:
                # Создаем ретривер в зависимости от количества источников
                if len(vector_retrievers) == 1:
                    retriever = MultiQueryRetriever.from_llm(
                        vector_retrievers[0],
                        self.llm,
                        prompt=QUERY_PROMPT
                    )
                else:
                    retriever = EnsembleRetriever(retrievers=vector_retrievers)
                
                # Получаем контекст из документов
                retrieved_docs = await retriever.ainvoke(last_user_message)
                context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                
                # Добавляем контекст к последнему сообщению пользователя
                enhanced_messages = formatted_messages.copy()
                
                # Заменяем последнее сообщение пользователя на сообщение с контекстом
                for i in range(len(enhanced_messages) - 1, -1, -1):
                    if isinstance(enhanced_messages[i], HumanMessage):
                        enhanced_messages[i] = HumanMessage(content=RAG_TEMPLATE.format(
                            context=context,
                            question=enhanced_messages[i].content
                        ))
                        break
                    
                # Генерируем ответ с учетом контекста из документов
                response = await self.llm.agenerate([enhanced_messages])
            else:
                # Обычный чат без RAG
                response = await self.llm.agenerate([formatted_messages])
            
            return {
                "response": response.generations[0][0].text,
                "model": self.model_name,
                "messages": request.messages + [{"role": "assistant", "content": response.generations[0][0].text}]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка генерации ответа: {str(e)}"
            )
    
        # Сохраняем старые методы для обратной совместимости
    async def chat(self, request: ChatRequest) -> Dict:
        """
        Метод чата с поддержкой контекста предыдущих сообщений.
        
        Args:
            request (ChatRequest): Запрос чата с сообщениями и настройками
        
        Returns:
            Dict: Ответ модели с сохранением контекста
        """
        return await self.unified_chat(request)
    
    async def chat_with_pdf(self, question: str, vector_retrievers: List[Any]) -> str:
       """
       Метод чата с контекстом из нескольких PDF документов.

       Args:
           question (str): Вопрос пользователя
           vector_retrievers (List[Any]): Список ретриверов для поиска в документах

       Returns:
           str: Ответ модели
       """
       # Создаем ChatRequest из вопроса
       request = ChatRequest(
           messages=[{"role": "user", "content": question}],
           system_prompt=None
       )
       
       # Используем унифицированный метод
       response = await self.unified_chat(request, vector_retrievers)
       return response["response"]
    #messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    # async def chat(self, request: ChatRequest) -> Dict:
    #     """
    #     Метод чата с поддержкой контекста предыдущих сообщений.
    
    #     Args:
    #         messages (List[Dict[str, str]]): Список сообщений в формате [{"role": "user/assistant", "content": "text"}]
    #         system_prompt (Optional[str]): Системный промпт
    
    #     Returns:
    #         Dict: Ответ модели с сохранением контекста
    
    #     Raises:
    #         HTTPException: При ошибке генерации ответа
    #     """
    #     try:
    #         formatted_messages: List[BaseMessage] = []

    #         # Устанавливаем модель
    #         self.model_name = None
    #         for msg in reversed(request.messages):
    #             if msg.role == "user":
    #                 self.model_name = msg.model
    #                 break
    #         if self.model_name:
    #             self.llm = ChatOllama(model=self.model_name, base_url=self.ollama_url)

    #         # Добавляем системный промпт если есть
    #         if request.system_prompt:
    #             formatted_messages.append(SystemMessage(content=request.system_prompt))

    #         # Преобразуем сообщения в формат langchain
    #         for message in request.messages:
    #             if message.role == "user":
    #                 formatted_messages.append(HumanMessage(content=message.content))
    #             elif message.role == "assistant":
    #                 formatted_messages.append(AIMessage(content=message.content))
            
    #         # Генерируем ответ с учетом всего контекста
    #         response = await self.llm.agenerate([formatted_messages])
            
    #         return {
    #             "response": response.generations[0][0].text,
    #             "model": self.model_name,
    #             "messages": request.messages + [{"role": "assistant", "content": response.generations[0][0].text}]
    #         }
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Ошибка генерации ответа: {str(e)}"
    #         )
    

    # async def chat_with_pdf(self, question: str, vector_retrievers: List[Any]) -> str:
    #     """
    #     Метод чата с контекстом из нескольких PDF документов.

    #     Args:
    #         question (str): Вопрос пользователя
    #         vector_retrievers (List[Any]): Список ретриверов для поиска в документах

    #     Returns:
    #         str: Ответ модели

    #     Raises:
    #         HTTPException: При ошибке генерации ответа
    #     """
    #     try:
    #         if len(vector_retrievers) == 1:
    #             retriever = MultiQueryRetriever.from_llm(
    #                 vector_retrievers[0],
    #                 self.llm,
    #                 prompt=QUERY_PROMPT
    #             )
    #         else:
    #             retriever = EnsembleRetriever(retrievers=vector_retrievers)
    #         prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
    #         chain = (
    #             {"context": retriever, "question": RunnablePassthrough()}
    #             | prompt
    #             | self.llm
    #             | StrOutputParser()
    #         )
    #         return await chain.ainvoke(question)
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Ошибка при обработке документа: {str(e)}"
    #         )

    async def get_models(self) -> List:
        """
        Поиск моделей для генерации ответа

        :return: Список моделей для генерации ответа
        """
        try:
            response = self.ollama_client.list()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=404, detail=f"Ошибка при выполнении запроса: {e}")

        # Отбор названий моделей
        model_names = []
        for model in response["models"]:
                if model["model"] != "nomic-embed-text:latest":
                    model_names.append({"name": model["model"]})
        # Проверка наличия моделей
        if not model_names:
            raise HTTPException(status_code=404, detail="Модели не загружены")
        return model_names

    def get_embedding_models(self):
        """
        Поиск моделей для генерации embeddings

        :return: Список моделей для генерации embeddings
        """
        try:
            response = self.ollama_client.list()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=404, detail=f"Ошибка при выполнении запроса: {e}")
        
        embedding_models = []
        # Проверяем каждую полученную модель
        for model in response["models"]:
            # Проверяем, начинается ли имя модели с любого из ожидаемых
            for existing_model in EXITING_EMBEDDINGS_MODELS:
                if model["model"].startswith(existing_model):
                    embedding_models.append({"name": model["model"]})
                    break

        # Проверка наличия моделей
        if not embedding_models:
            raise HTTPException(status_code=404, detail="Модели для генерации embeddings не найдены")

        return embedding_models