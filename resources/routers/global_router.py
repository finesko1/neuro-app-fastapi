from fastapi import APIRouter, File, UploadFile, Form, HTTPException
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
    files: List[UploadFile] = File(...),
    collection_name: str = Form(...),
    metadata: Optional[str] = Form(None),
):
    try:
        upload_response = await document_controller.upload_collection(files)
        
        metadata_dict = json.loads(metadata) if metadata else None
        collection_data = CollectionCreate(name=collection_name, metadata=metadata_dict)
        collection_response = await chroma.add_collection(collection_data)
        
        document_ids = []
        for document in upload_response:
            chunks = await document_controller.get_document_chunks(document.document_id)
            if not chunks:
                raise HTTPException(500, f"No chunks found for document {document.document_id}")
            
            add_response = await chroma.add_to_collection(
                name=collection_name, 
                document_chunks=chunks
            )
            
            document_ids.append(document.document_id)
        
        return {
            "status": "success",
            "collection": collection_name,
            "document_ids": document_ids 
        }
    
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid metadata format")
    except Exception as e:
        raise HTTPException(500, str(e))