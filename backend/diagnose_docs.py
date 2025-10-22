#!/usr/bin/env python
"""
Diagnostic script to check document management functionality
"""
import sys
import os
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the core modules
    print("Importing core modules...")
    from core.vector_store import list_documents, delete_document
    print("✅ Successfully imported vector_store functions")

    # Check if Qdrant client is working
    print("\nChecking Qdrant client...")
    from core.vector_store import client
    print(f"✅ Client location: {getattr(client._client, '_location', 'unknown')}")

    # List documents
    print("\nListing documents...")
    try:
        docs = list_documents()
        print(f"✅ Found {len(docs)} documents")
        print(json.dumps(docs, indent=2))
    except Exception as e:
        print(f"❌ Error listing documents: {str(e)}")

    # Check if the routers are working
    print("\nImporting router modules...")
    from routers.documents import router as docs_router
    print("✅ Successfully imported documents router")

    # Check FastAPI app
    print("\nChecking FastAPI app...")
    from main import app
    print("✅ Successfully imported FastAPI app")
    
    # Check routes
    print("\nApp routes:")
    for route in app.routes:
        print(f"  {route.path} [{', '.join(route.methods)}]")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nDiagnostic completed")