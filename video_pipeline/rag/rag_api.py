"""RAG API - FastAPI web service."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from rag.rag_engine import RAGEngine
from modules.search.enriched_search import EnrichedSearch

app = FastAPI(title="Video RAG API")

# Mount static files for UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Initialize RAG engine
rag_engine = RAGEngine()
enriched_search = EnrichedSearch()


class QuestionRequest(BaseModel):
    question: str
    limit: int = 10


class QuestionResponse(BaseModel):
    answer: str
    sources: list
    llm_used: bool = True
    error: str = None


@app.get("/")
async def root():
    """Root endpoint - redirect to UI."""
    return FileResponse("ui/index.html")


@app.get("/enriched")
async def enriched_ui():
    """Enriched transcripts UI."""
    return FileResponse("ui/enriched.html")


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


@app.get("/api/topics")
async def get_topics():
    """Get all topics with counts."""
    return enriched_search.get_all_topics()


@app.get("/api/enriched")
async def get_enriched(
    topic: str = Query(None),
    search: str = Query(None),
    semantic: str = Query(None),
    limit: int = Query(50)
):
    """Get enriched transcripts."""
    try:
        if semantic:
            # Semantic search
            results = enriched_search.semantic_search(semantic, limit)
        elif topic:
            results = enriched_search.search_by_topic(topic, limit)
        elif search:
            results = enriched_search.search_summary(search, limit)
        else:
            # Get all
            conn = enriched_search.conn
            cur = conn.cursor()
            cur.execute("SELECT * FROM enriched_transcripts LIMIT ?", (limit,))
            results = [dict(row) for row in cur.fetchall()]
        
        return results
        
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
    enriched_search.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
