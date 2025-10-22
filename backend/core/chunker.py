import spacy
from sklearn.neighbors import NearestNeighbors
import numpy as np
from core.embedder import generate_combined_embedding

def chunk_text(text, max_words=200, overlap=20):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_words:
            chunks.append(" ".join(current_chunk))
            # Start a new chunk with overlap
            current_chunk = current_chunk[-overlap:] if overlap > 0 else []
            current_length = len(" ".join(current_chunk).split())
        current_chunk.append(sentence)
        current_length += sentence_length

    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def chunk_text_with_embeddings(text, max_words=200, overlap=20):
    """
    Chunk text into segments and generate embeddings for each chunk.

    Args:
        text (str): The input text to chunk.
        max_words (int): Maximum number of words per chunk.
        overlap (int): Number of overlapping words between chunks.

    Returns:
        List[dict]: List of chunks with their embeddings.
    """
    from spacy.lang.en import English
    nlp = English()
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_words:
            chunk_text = " ".join(current_chunk)
            chunk_embedding = generate_combined_embedding(chunk_text)
            chunks.append({"text": chunk_text, "embedding": chunk_embedding})
            # Start a new chunk with overlap
            current_chunk = current_chunk[-overlap:] if overlap > 0 else []
            current_length = len(" ".join(current_chunk).split())
        current_chunk.append(sentence)
        current_length += sentence_length

    # Add the last chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunk_embedding = generate_combined_embedding(chunk_text)
        chunks.append({"text": chunk_text, "embedding": chunk_embedding})

    return chunks

def cluster_chunks(chunks, n_neighbors=2):
    """
    Cluster chunks using KNN.

    Args:
        chunks (List[dict]): List of chunks with their embeddings.
        n_neighbors (int): Number of neighbors for KNN.

    Returns:
        List[List[int]]: Indices of nearest neighbors for each chunk.
    """
    embeddings = np.array([chunk["embedding"] for chunk in chunks])
    knn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine").fit(embeddings)
    distances, indices = knn.kneighbors(embeddings)
    return indices
