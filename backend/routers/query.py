import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.embedder import generate_combined_embedding
from core.vector_store import search_vectors
from core.llm import ask_llm
from fastapi.responses import JSONResponse

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    doc_id: Optional[str] = None

@router.post("")
async def query_docs(req: QueryRequest):
    try:
        print(f"Received query request: query='{req.query}', doc_id={req.doc_id}")
        
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY environment variable is not set."
            )
            
        query_embedding = generate_combined_embedding(req.query)
        
        # Search vectors (clusters can be used here if stored in the vector database)
        results = search_vectors(query_embedding, doc_id=req.doc_id)
        
        if not results:
            message = "No relevant documents found for your query."
            if req.doc_id:
                message = f"No relevant content found for your query in document {req.doc_id}."
            return JSONResponse(content={"answer": message, "sources": []}, status_code=200)
        
        answer = ask_llm(req.query, results)
        return JSONResponse(content={"answer": answer, "sources": results}, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error processing query: {e}")
        return JSONResponse(content={"detail": "Internal Server Error", "error": str(e)}, status_code=500)
