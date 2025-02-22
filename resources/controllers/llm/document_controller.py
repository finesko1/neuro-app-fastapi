"""Управление документом."""
import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Загружаем документ и делим на чанки."""
    
    def __init__(self, chunk_size: int = 7500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def load_pdf(self, file_path: Path) -> List:
        """Load PDF document."""
        try:
            logger.info(f"Загрузка ПДФ из: {file_path}")
            loader = UnstructuredPDFLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Oшибка загрузки ПДФ: {e}")
            raise
    
    def split_documents(self, documents: List) -> List:
        """Делитель на чанки."""
        try:
            logger.info("Деление на чанки документов")
            return self.splitter.split_documents(documents)
        except Exception as e:
            logger.error(f"Oшибка при делении на чанки: {e}")
            raise 