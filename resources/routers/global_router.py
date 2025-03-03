from fastapi import APIRouter, UploadFile, Form, HTTPException
from typing import List, Optional, Dict
import json
from resources.controllers.llm.vector_db_controller import VectorDbController
from resources.controllers.llm.document_controller import DocumentController
from resources.models.llm.chroma.collection_create import CollectionCreate

router = APIRouter()
chroma = VectorDbController()
document_controller = DocumentController()

@router.post("/global/collection")
async def global_collection_upload(
    chat_id: int, 
):
    try:
        collection_name = f"collection-{chat_id}"
        collection_data = CollectionCreate(name=collection_name)
        collection_response = await chroma.add_collection(collection_data)
        documents = await document_controller.get_documents_list(chat_id=chat_id)

        for document in documents:
            chunks = await document_controller.get_document_chunks(document["path"])
            if not chunks:
                raise HTTPException(500, f"No chunks found for document {document["original_name"]}")
            
            add_response = await chroma.add_to_collection(
                name=collection_name, 
                document_chunks=chunks
            )
        
        return {
            "status": "success",
            "collection": collection_name,
        }
    
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid metadata format")
    except Exception as e:
        raise HTTPException(500, str(e))
    