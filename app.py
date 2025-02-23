import logging
from fastapi import FastAPI

from resources.routers.chat_router import router as chat_router
from resources.routers.files_router import get_document_chunks, router as files_router
from resources.routers.chroma_router import router as chroma_router
from resources.routers.base_router import router as base_router
from resources.routers.llm_router import router as llm_router

app = FastAPI(
    title="Neuro API",
    description="API for Neuro App",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.include_router(base_router, tags=["base"])
app.include_router(llm_router,tags=["llm"])
app.include_router(chat_router, tags=["chat"])
app.include_router(files_router,tags=["files"])
app.include_router(chroma_router,tags=["chroma"])