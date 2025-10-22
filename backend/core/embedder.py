from sentence_transformers import SentenceTransformer
import numpy as np

# Load multiple Sentence Transformers models
model1 = SentenceTransformer("all-MiniLM-L6-v2")
model2 = SentenceTransformer("paraphrase-MiniLM-L12-v2")

def generate_combined_embedding(text):
    """
    Generate embeddings using multiple models and combine them by averaging.
    
    Args:
        text (str): The input text to embed.

    Returns:
        np.ndarray: Combined embedding vector.
    """
    embedding1 = model1.encode(text)
    embedding2 = model2.encode(text)
    # Combine embeddings by averaging
    combined_embedding = np.mean([embedding1, embedding2], axis=0)
    return combined_embedding

def generate_embeddings_for_documents(documents):
    """
    Generate embeddings for a list of documents.

    Args:
        documents (List[str]): List of document texts.

    Returns:
        np.ndarray: Array of combined embeddings for all documents.
    """
    return np.array([generate_combined_embedding(doc) for doc in documents])
