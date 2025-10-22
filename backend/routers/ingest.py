from fastapi import APIRouter, File, UploadFile, Form
from core.extractor import extract_text
from core.chunker import chunk_text_with_embeddings, cluster_chunks
from core.vector_store import insert_vectors
import os, uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
async def upload_document(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path, file.content_type)
    chunks_with_embeddings = chunk_text_with_embeddings(text)
    chunks = [chunk["text"] for chunk in chunks_with_embeddings]
    embeddings = [chunk["embedding"] for chunk in chunks_with_embeddings]

    # Cluster the chunks
    cluster_indices = cluster_chunks(chunks_with_embeddings)

    # Store the clusters and embeddings
    insert_vectors(chunks, embeddings, file_id)

    return {
        "message": "File processed successfully", 
        "doc_id": file_id,
        "filename": file.filename,
        "chunks": len(chunks),
        "clusters": cluster_indices.tolist(),
        "content_type": file.content_type
    }
