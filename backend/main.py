import os
from fastapi import FastAPI, Depends
from routers import ingest, query, documents
from fastapi.middleware.cors import CORSMiddleware
from core.auth import verify_token, get_optional_token

app = FastAPI(title="DocChat Backend", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH DEBUG MODE: Authentication is completely bypassed for debugging
# Every request will receive a fake authenticated user
print("🛑 WARNING: Running in AUTH BYPASS MODE. All requests will be authenticated!")
print("🔐 A debug user will be used for all requests")

# Add all routers WITHOUT authentication dependencies for debugging
app.include_router(ingest.router, prefix="/api/ingest")
app.include_router(query.router, prefix="/api/query")
app.include_router(documents.router, prefix="/api/documents")

@app.get("/")
async def root():
    return {"message": "Welcome to DocChat Backend!"}

@app.get("/api/status")
async def status():
    try:
        from core.vector_store import client
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Check if we're using in-memory or persistent storage
        try:
            storage_type = "in-memory" if str(client._client._location) == ":memory:" else "persistent"
        except Exception:
            storage_type = "unknown"
        
        return {
            "status": "operational",
            "gemini_configured": bool(gemini_key),
            "vector_db": storage_type,
            "missing_config": [] if gemini_key else ["GEMINI_API_KEY"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Run the server when this script is executed directly
if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable or use 8000 as default
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting DocChat Backend server on port {port}...")
    print(f"API documentation will be available at http://localhost:{port}/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=port)