"""Vector embeddings and database functionality."""
import logging
from typing import List
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from resources.helpers.environment_helper import EnvironmentHelper

logger = logging.basicConfig(level=logging.INFO)

class VectorStore:
    """Хрома."""
    
    def __init__(self, collection_name: str, embedding_model: str = "nomic-embed-text:latest"):
        self.env = EnvironmentHelper()
        self.embeddings = OllamaEmbeddings(model=embedding_model) or OllamaEmbeddings(model=self.env.ollama_embedding_model)
        self.collection_name = collection_name
        self.vector_db = None
    
    def create_vector_db(self, documents: List, collection_name: str = "local-rag") -> Chroma:
        """Создангие векторной коллекции."""
        try:
            logger.info("Creating vector database")
            self.vector_db = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name
            )
            return self.vector_db
        except Exception as e:
            logger.error(f"Error creating vector database: {e}")
            raise
    
    def delete_collection(self) -> None:
        """Удалить коллекцию."""
        if self.vector_db:
            try:
                logger.info("Deleting vector database collection")
                self.vector_db.delete_collection()
                self.vector_db = None
            except Exception as e:
                logger.error(f"Error deleting collection: {e}")
                raise 