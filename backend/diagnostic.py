#!/usr/bin/env python
"""
DocChat Diagnostic Tool

This script tests each component of the DocChat pipeline to identify issues
with document processing, embedding generation, vector storage, and LLM responses.
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dochat-diagnostics")

# Try to import the required modules
try:
    from core.extractor import extract_text
    from core.chunker import chunk_text_with_embeddings
    from core.embedder import generate_combined_embedding
    from core.vector_store import search_vectors, insert_vectors, client as qdrant_client
    from core.llm import ask_llm
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're running this script from the backend directory")
    sys.exit(1)

def test_api_keys():
    """Test if required API keys are set"""
    logger.info("Checking API keys...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        logger.info("✓ GEMINI_API_KEY is set")
    else:
        logger.error("✗ GEMINI_API_KEY is not set")
        logger.info("  Set it using: export GEMINI_API_KEY='your-api-key'")
        logger.info("  Or add it to a .env file in the backend directory")

def test_pdf_extraction(pdf_path):
    """Test PDF text extraction"""
    logger.info(f"Testing PDF extraction from {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        logger.error(f"✗ File not found: {pdf_path}")
        return None
    
    try:
        content_type = "application/pdf"  # Assuming PDF
        text = extract_text(pdf_path, content_type)
        
        if not text or len(text) < 10:
            logger.error(f"✗ Extracted text is empty or very short: '{text[:100]}'")
            return None
        
        text_preview = text[:100].replace('\n', ' ') + "..." if len(text) > 100 else text
        logger.info(f"✓ Successfully extracted text: '{text_preview}'")
        logger.info(f"  Extracted {len(text)} characters")
        
        return text
    except Exception as e:
        logger.error(f"✗ Error extracting text: {e}")
        return None

def test_chunking(text):
    """Test text chunking"""
    logger.info("Testing text chunking...")
    
    if text is None:
        logger.error("✗ No text provided for chunking")
        return None
    
    try:
        chunks = chunk_text_with_embeddings(text)
        
        if not chunks:
            logger.error("✗ No chunks generated")
            return None
        
        logger.info(f"✓ Generated {len(chunks)} chunks")
        logger.info(f"  First chunk: '{chunks[0]['text'][:100]}...'")
        logger.info(f"  Average chunk size: {sum(len(c['text']) for c in chunks) // len(chunks)} characters")
        
        return chunks
    except Exception as e:
        logger.error(f"✗ Error during chunking: {e}")
        return None

def test_embedding(chunks):
    """Test embedding generation"""
    logger.info("Testing embedding generation...")
    
    if not chunks:
        logger.error("✗ No chunks provided for embedding")
        return None
    
    try:
        embeddings = [c['embedding'] for c in chunks]
        
        if not embeddings or len(embeddings) != len(chunks):
            logger.error(f"✗ Embedding generation failed or incomplete: got {len(embeddings)} for {len(chunks)} chunks")
            return None
        
        logger.info(f"✓ Generated {len(embeddings)} embeddings")
        logger.info(f"  Embedding dimensions: {len(embeddings[0])}")
        
        return embeddings
    except Exception as e:
        logger.error(f"✗ Error generating embeddings: {e}")
        return None

def test_vector_storage(chunks, embeddings):
    """Test vector storage"""
    logger.info("Testing vector storage...")
    
    if chunks is None or embeddings is None:
        logger.error("✗ Missing chunks or embeddings for vector storage test")
        return False
    
    try:
        # Use a test document ID
        test_id = "test-diagnostic-doc"
        insert_vectors(chunks, embeddings, test_id)
        logger.info(f"✓ Successfully inserted vectors into Qdrant")
        return True
    except Exception as e:
        logger.error(f"✗ Error inserting vectors: {e}")
        return False

def test_vector_search(query):
    """Test vector searching"""
    logger.info(f"Testing vector search with query: '{query}'...")
    
    try:
        # Convert query to embedding
        query_embedding = generate_combined_embedding([query])
        
        # Search for similar chunks
        results = search_vectors(query_embedding, limit=3)
        
        if not results:
            logger.warning("⚠️ No results found for query")
            return None
        
        logger.info(f"✓ Found {len(results)} results")
        for i, result in enumerate(results):
            text_preview = result.get('text', '')[:100].replace('\n', ' ')
            logger.info(f"  Result {i+1}: '{text_preview}...'")
        
        return results
    except Exception as e:
        logger.error(f"✗ Error during vector search: {e}")
        return None

def test_llm(query, results):
    """Test LLM response generation"""
    logger.info("Testing LLM response generation...")
    
    if not results:
        logger.error("✗ No search results to send to LLM")
        return None
    
    try:
        answer = ask_llm(query, results)
        
        if not answer:
            logger.error("✗ LLM returned empty answer")
            return None
        
        logger.info(f"✓ LLM response: '{answer[:200]}...'")
        return answer
    except Exception as e:
        logger.error(f"✗ Error getting LLM response: {e}")
        return None

def run_full_pipeline(pdf_path, query):
    """Run the full pipeline from PDF to answer"""
    logger.info("=" * 50)
    logger.info("STARTING FULL PIPELINE TEST")
    logger.info("=" * 50)
    
    # Step 1: API Keys
    test_api_keys()
    
    # Step 2: Extract text from PDF
    text = test_pdf_extraction(pdf_path)
    if text is None:
        logger.error("Pipeline stopped at text extraction stage")
        return
    
    # Step 3: Chunk the text
    chunks = test_chunking(text)
    if chunks is None:
        logger.error("Pipeline stopped at text chunking stage")
        return
    
    # Step 4: Generate embeddings
    embeddings = test_embedding(chunks)
    if embeddings is None:
        logger.error("Pipeline stopped at embedding generation stage")
        return
    
    # Step 5: Store vectors
    if not test_vector_storage(chunks, embeddings):
        logger.error("Pipeline stopped at vector storage stage")
        return
    
    # Step 6: Search vectors
    results = test_vector_search(query)
    if results is None:
        logger.warning("Pipeline yielded no search results, but continuing...")
    
    # Step 7: Generate LLM response
    answer = test_llm(query, results or [])
    if answer is None:
        logger.error("Pipeline stopped at LLM response stage")
        return
    
    logger.info("=" * 50)
    logger.info("PIPELINE TEST COMPLETED")
    logger.info("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <pdf_path> <query>")
        print(f"Example: {sys.argv[0]} ./uploads/academic_calendar.pdf 'When does the fall semester begin?'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    query = sys.argv[2]
    
    run_full_pipeline(pdf_path, query)