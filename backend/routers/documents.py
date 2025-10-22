from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

from core.vector_store import list_documents, delete_document

router = APIRouter(
    tags=["documents"],
)

class DocumentInfo(BaseModel):
    doc_id: str
    chunks: int


@router.get("", response_model=List[DocumentInfo])
async def get_all_documents():
    """
    List all documents stored in the vector database.
    Returns a list of document IDs and the number of chunks per document.
    """
    try:
        documents = list_documents()
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    """
    Delete a document from the vector database by its ID.
    """
    try:
        success = delete_document(doc_id)
        if success:
            return {"status": "success", "message": f"Document {doc_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found or collection doesn't exist"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )