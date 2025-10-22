from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue, FilterSelector
import uuid
import logging
import os

logger = logging.getLogger(__name__)

# Use persistent storage in data directory instead of in-memory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Try to connect to local storage, fall back to in-memory if local storage is locked
try:
    client = QdrantClient(path=DATA_DIR)
    logger.info(f"Successfully connected to persistent storage at {DATA_DIR}")
except RuntimeError as e:
    if "already accessed by another instance" in str(e):
        logger.warning(f"Storage folder {DATA_DIR} is locked. Falling back to in-memory storage.")
        client = QdrantClient(":memory:")
    else:
        raise
COLLECTION_NAME = "documents"

def init_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def insert_vectors(chunks, embeddings, doc_id):
    points = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={"text": chunk, "doc_id": doc_id, "chunk_idx": i, "date_added": str(uuid.uuid1().time)},
            )
        )

    try:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
    except ValueError as exc:
        if f"Collection {COLLECTION_NAME} not found" in str(exc):
            init_collection()
            client.upsert(collection_name=COLLECTION_NAME, points=points)
        else:
            raise

def search_vectors(query_embedding, limit=3, doc_id=None):
    try:
        # If doc_id is provided, filter results to only that document
        filter_condition = None
        if doc_id:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            )

        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            query_filter=filter_condition
        )
    except ValueError as exc:
        if f"Collection {COLLECTION_NAME} not found" in str(exc):
            init_collection()
            try:
                results = client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_embedding,
                    limit=limit,
                    query_filter=filter_condition
                )
            except Exception:
                return []
        else:
            raise

    return [r.payload for r in results]

def list_documents():
    try:
        results = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        # Extract unique document IDs and metadata
        doc_ids = {}
        for point, _ in results[0]:
            payload = point.payload
            doc_id = payload.get("doc_id")
            if doc_id and doc_id not in doc_ids:
                doc_ids[doc_id] = {
                    "doc_id": doc_id,
                    "chunks": 1
                }
            elif doc_id:
                doc_ids[doc_id]["chunks"] = doc_ids[doc_id]["chunks"] + 1
                
        return list(doc_ids.values())
        
    except ValueError as exc:
        if f"Collection {COLLECTION_NAME} not found" in str(exc):
            init_collection()
            return []
        else:
            raise
            
def delete_document(doc_id):
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                )
            )
        )
        return True
    except ValueError as exc:
        if f"Collection {COLLECTION_NAME} not found" in str(exc):
            return False
        else:
            raise
