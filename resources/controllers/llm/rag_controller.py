"""Контроллер для генерации пайплайна RAG."""
import logging
from typing import Any, Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from resources.controllers.llm import LLMController

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Manages the RAG (Retrieval Augmented Generation) pipeline."""
    
    def __init__(self, vector_db: Any, llm_controller: LLMController):
        self.vector_db = vector_db
        self.llm_manager = llm_controller
        self.retriever = self._setup_retriever()
        self.chain = self._setup_chain()
    
    def _setup_retriever(self) -> MultiQueryRetriever:
        """Set up the multi-query retriever."""
        try:
            return MultiQueryRetriever.from_llm(
                retriever=self.vector_db.as_retriever(),
                llm=self.llm_controller.llm,
                prompt=self.llm_controller.get_query_prompt()
            )
        except Exception as e:
            logger.error(f"Error setting up retriever: {e}")
            raise
    
    def _setup_chain(self) -> Any:
        """Set up the RAG chain."""
        try:
            return (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.llm_controller.get_rag_prompt()
                | self.llm_controller.llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Error setting up chain: {e}")
            raise
    
    def get_response(self, question: str) -> str:
        """Get response for a question using the RAG pipeline."""
        try:
            logger.info(f"Getting response for question: {question}")
            return self.chain.invoke(question)
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            raise 