"""RAG API - FastAPI web service.

Supports per-video databases with multi-video search capability.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.rag_engine import RAGEngine
from rag.hybrid_retriever import HybridRetriever

app = FastAPI(title="Video RAG API")

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Initialize RAG engine (searches all videos by default)
rag_engine = RAGEngine()


class QuestionRequest(BaseModel):
    question: str
    limit: int = 10
    video_id: str = None  # Optional: search specific video


class QuestionResponse(BaseModel):
    answer: str
    sources: list
    llm_used: bool = True
    error: str = None


@app.get("/")
async def root():
    """Root endpoint - redirect to UI."""
    return FileResponse("ui/index.html")


@app.get("/videos")
async def get_videos():
    """Get list of all available videos with stats."""
    retriever = HybridRetriever()
    videos = retriever.get_all_videos()
    retriever.close()
    return videos


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the lecture videos.

    Returns an answer based on transcript content.
    
    Args:
        question: User's question
        limit: Number of results to retrieve
        video_id: Optional. Search specific video only.
    """
    try:
        # Use video-specific retriever if video_id provided
        if request.video_id:
            retriever = HybridRetriever(video_id=request.video_id)
            chunks = retriever.search(request.question, request.limit)
            retriever.close()
        else:
            # Search all videos
            chunks = rag_engine.answer_question(
                question=request.question,
                limit=request.limit,
                return_chunks_only=True
            )

        if not chunks:
            return QuestionResponse(
                answer="No lecture content matched your question. Please try rephrasing.",
                sources=[],
                llm_used=False
            )

        # Check if LLM is available
        llm_available = rag_engine.llm.is_available()

        if llm_available:
            # Build context and get LLM answer
            context = rag_engine.prompt_builder.build_context(chunks)
            prompt = rag_engine.prompt_builder.build_prompt(request.question, context)
            answer = rag_engine.llm.ask(prompt)
            llm_used = True
        else:
            # Fallback: Return retrieved chunks without LLM
            answer = rag_engine._build_fallback_answer(chunks)
            llm_used = False

        # Prepare sources
        sources = [
            {
                "video_id": chunk.get("video_id", "Unknown"),
                "video_title": chunk.get("video_title", ""),
                "timestamp": chunk["timestamp"]
            }
            for chunk in chunks
        ]

        return QuestionResponse(
            answer=answer,
            sources=sources,
            llm_used=llm_used
        )

    except Exception as e:
        import traceback
        print(f"Error in /ask: {str(e)}")
        print(traceback.format_exc())
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
