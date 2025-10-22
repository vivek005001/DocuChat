# DocChat

A document question-answering app that uses Gemini AI to answer questions about your documents.

## Setup

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Set Gemini API key
```bash
# Option 1: Set as environment variable
export GEMINI_API_KEY="your-gemini-api-key"

# Option 2: Create .env file
echo "GEMINI_API_KEY=your-gemini-api-key" > .env
```

3. Start the server
```bash
uvicorn main:app --reload
```

## API Endpoints

- `POST /api/ingest/`: Upload a document
- `POST /api/query/`: Ask a question (JSON body: `{"query": "your question"}`)
- `GET /api/status`: Check system status