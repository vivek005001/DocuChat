#!/usr/bin/env python
"""
DocChat Diagnostic Tool - Helps identify issues with document processing and querying
"""

import os
import sys
import logging
import json
from importlib.util import find_spec

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('docchat_diagnostic')

# Check for required modules
def check_modules():
    required_modules = [
        'fastapi', 'uvicorn', 'pdfminer.six', 'sentence_transformers', 
        'qdrant_client', 'python-dotenv'
    ]
    optional_modules = ['google.generativeai']
    
    print("\n=== Package Check ===")
    for module in required_modules:
        if find_spec(module.split('.')[0]):
            print(f"✓ {module} installed")
        else:
            print(f"✗ {module} NOT installed (required)")
    
    for module in optional_modules:
        module_name = module.split('.')[0]
        if find_spec(module_name):
            print(f"✓ {module} installed")
        else:
            print(f"⚠ {module} NOT installed (optional but recommended)")
    
    # Check for GEMINI_API_KEY
    if os.getenv("GEMINI_API_KEY"):
        print("✓ GEMINI_API_KEY environment variable set")
    else:
        print("⚠ GEMINI_API_KEY environment variable not set")

# Test PDF extraction
def test_pdf_extraction(pdf_path=None):
    print("\n=== PDF Extraction Test ===")
    
    if not pdf_path:
        # Look for PDFs in the uploads directory
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        if os.path.exists(uploads_dir):
            pdfs = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
            if pdfs:
                pdf_path = os.path.join(uploads_dir, pdfs[0])
                print(f"Found PDF: {pdfs[0]}")
            else:
                print("No PDFs found in uploads directory")
                return
        else:
            print("Uploads directory not found")
            return
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    try:
        from core.extractor import extract_text
        
        text = extract_text(pdf_path, "application/pdf")
        
        # Print statistics and sample
        words = text.split()
        word_count = len(words)
        chars = len(text)
        
        print(f"Extracted {word_count} words ({chars} characters)")
        
        if word_count == 0:
            print("⚠ Warning: No text extracted from PDF!")
            print("The PDF might be scanned images without OCR or have content protection")
        else:
            sample = " ".join(words[:30]) + "..." if word_count > 30 else text
            print(f"\nSample text: {sample}")
            
            # Test chunking
            from core.chunker import chunk_text_with_embeddings
            chunks = chunk_text_with_embeddings(text)
            print(f"\nText divided into {len(chunks)} chunks")
            print(f"First chunk ({len(chunks[0].split())} words): {chunks[0][:100]}...")
        
    except Exception as e:
        print(f"Error extracting text: {e}")

# Test vector storage
def test_vector_storage():
    print("\n=== Vector Storage Test ===")
    
    try:
        from core.vector_store import client, COLLECTION_NAME, init_collection, search_vectors
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME in collection_names:
            print(f"✓ Collection '{COLLECTION_NAME}' exists")
            
            # Get collection info
            collection_info = client.get_collection(COLLECTION_NAME)
            points_count = client.count(COLLECTION_NAME).count
            print(f"Collection has {points_count} points")
            
            if points_count == 0:
                print("⚠ Warning: No vectors stored in collection!")
                print("Try uploading a document first")
            else:
                # Try a simple search
                from core.embedder import model
                test_query = "When is the academic year starting?"
                query_embedding = model.encode(test_query)
                
                results = search_vectors(query_embedding, limit=2)
                
                if results:
                    print(f"✓ Search returned {len(results)} results")
                    for i, r in enumerate(results):
                        print(f"\nResult {i+1}: {r['text'][:100]}...")
                else:
                    print("⚠ Search returned no results")
        else:
            print(f"⚠ Collection '{COLLECTION_NAME}' does not exist")
            print("It will be created automatically when you upload a document")
            
    except Exception as e:
        print(f"Error testing vector storage: {e}")

# Test LLM module
def test_llm():
    print("\n=== LLM Module Test ===")
    
    try:
        from core.llm import ask_llm, has_genai
        
        if has_genai:
            print("✓ Google Generative AI package is installed")
            
            if os.getenv("GEMINI_API_KEY"):
                print("✓ GEMINI_API_KEY is set")
            else:
                print("⚠ GEMINI_API_KEY is not set")
                
        else:
            print("⚠ Google Generative AI package is not installed")
            print("Install it with: pip install google-generativeai")
        
        # Test with mock data
        mock_contexts = [
            {"text": "The academic year starts on September 1, 2025."},
            {"text": "Final exams will be held from December 10-20, 2025."}
        ]
        
        print("\nTesting LLM with mock data...")
        response = ask_llm("When does the academic year start?", mock_contexts)
        
        print(f"\nLLM Response Sample:\n{response[:200]}...")
        
    except Exception as e:
        print(f"Error testing LLM: {e}")

# Main function
def main():
    print("DocChat Diagnostic Tool")
    print("======================")
    
    # Check modules
    check_modules()
    
    # Test PDF extraction
    test_pdf_extraction()
    
    # Test vector storage
    test_vector_storage()
    
    # Test LLM module
    test_llm()
    
    print("\n=== Summary ===")
    print("If you're having issues with your academic calendar PDF:")
    print("1. Make sure the PDF text is extractable (not scanned images)")
    print("2. Check that documents are being properly chunked")
    print("3. Verify that vectors are being stored in the collection")
    print("4. Ensure your query is semantically related to content in the PDF")
    print("5. Check that Gemini API is properly configured")
    
    print("\nTo test uploading a document and querying it:")
    print("1. Run the server: uvicorn main:app --reload")
    print("2. Upload PDF: POST http://localhost:8000/api/ingest/ (multipart form with file)")
    print("3. Query: POST http://localhost:8000/api/query/ with JSON body: {\"query\": \"When is the academic year starting?\"}")

if __name__ == "__main__":
    main()