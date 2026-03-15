"""RAG API - FastAPI web service."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from rag.rag_engine import RAGEngine

app = FastAPI(title="Video RAG API")

# Mount static files for UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Initialize RAG engine
rag_engine = RAGEngine()


class QuestionRequest(BaseModel):
    question: str
    limit: int = 10


class QuestionResponse(BaseModel):
    answer: str
    sources: list
    error: str = None


@app.get("/")
async def root():
    """Root endpoint - redirect to UI."""
    return FileResponse("ui/index.html")


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the lecture videos.
    
    Returns an answer based on transcript content.
    """
    try:
        result = rag_engine.answer_question(
            question=request.question,
            limit=request.limit
        )
        
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    llm_available = rag_engine.llm.is_available()
    return {
        "status": "healthy",
        "llm_available": llm_available
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    rag_engine.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
