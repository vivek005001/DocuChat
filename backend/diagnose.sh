#!/bin/bash
# DocChat diagnostics script

echo "===== DocChat Diagnostics ====="
echo "Running tests to diagnose potential issues..."

# Check Python version
echo -e "\n1. Python Version:"
python3 --version

# Check virtual environment
echo -e "\n2. Virtual Environment:"
if [[ -d "venv" ]]; then
    echo "  ✅ venv directory found"
    source venv/bin/activate
    echo "  ✅ Virtual environment activated"
else
    echo "  ❌ venv directory not found"
    echo "  💡 Create a virtual environment using: python -m venv venv"
    exit 1
fi

# Check installed packages
echo -e "\n3. Checking Required Packages:"
pip list | grep -E "fastapi|uvicorn|qdrant-client|sentence-transformers|pdfminer.six|google-generativeai|python-dotenv"

# Check environment variables
echo -e "\n4. Environment Variables:"
if [[ -f ".env" ]]; then
    echo "  ✅ .env file found"
    # Show variables without showing actual values
    echo "  Variables found in .env file:"
    grep -o "^[^=]*=" .env
else
    echo "  ❌ .env file not found"
    echo "  💡 Create a .env file with your API keys"
fi

if [[ -n "$GEMINI_API_KEY" ]]; then
    echo "  ✅ GEMINI_API_KEY is set in environment"
else
    echo "  ❌ GEMINI_API_KEY not set in environment"
    echo "  💡 Set it using: export GEMINI_API_KEY='your-key'"
fi

# Check Gemini models
echo -e "\n5. Available Gemini Models:"
echo "  Running list_gemini_models.py..."
python list_gemini_models.py

# Check vector database
echo -e "\n6. Vector Database Status:"
echo "  Using in-memory Qdrant database (data will be lost on restart)"
echo "  💡 For persistence, update vector_store.py to use a persistent path"

# Check uploads directory
echo -e "\n7. Uploads Directory:"
if [[ -d "uploads" ]]; then
    echo "  ✅ uploads directory found"
    echo "  Files in uploads directory: $(find uploads -type f | wc -l)"
else
    echo "  ❌ uploads directory not found"
    echo "  💡 Creating uploads directory..."
    mkdir -p uploads
fi

# Provide next steps
echo -e "\n===== Next Steps ====="
echo "1. Run the server: uvicorn main:app --reload"
echo "2. Upload a document: POST to http://localhost:8000/api/ingest/"
echo "3. Query documents: POST to http://localhost:8000/api/query/"
echo "4. Check status: GET http://localhost:8000/api/status"
echo -e "\nIf you encounter issues with Gemini models, try updating the model name in core/llm.py"
echo "based on the available models listed above."