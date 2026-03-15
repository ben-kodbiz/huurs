# Retrieval Comparison: FTS5 vs Hybrid Search

## Test Results

### Query: "What is patience?"

| Method | Results | Quality |
|--------|---------|---------|
| **FTS5 Only** | 0 results ❌ | No matches - word not in transcripts |
| **Hybrid (FTS5+Vector)** | 3 results ✅ | Finds semantically related content about guidance/perfection |

### Query: "charity in Islam"

| Method | Results | Quality |
|--------|---------|---------|
| **FTS5 Only** | 0 results ❌ | Word not in transcripts |
| **Hybrid** | 3 results ✅ | Finds content about "good deeds", "helping" |

### Query: "Surah ar-rahman"

| Method | Results | Quality |
|--------|---------|---------|
| **FTS5 Only** | 8 results ✅ | Good exact matches |
| **Hybrid** | 8 results ✅ | Same + semantic context |

### Query: "forgiveness"

| Method | Results | Quality |
|--------|---------|---------|
| **FTS5 Only** | 0 results ❌ | Word not in transcripts |
| **Hybrid** | 3 results ✅ | Finds related concepts (mercy, repentance) |

---

## Why Hybrid is Better

### FTS5 Limitations
- **Exact match only**: "charity" ≠ "sadaqah" ≠ "good deeds"
- **No synonyms**: "forgiveness" ≠ "mercy" ≠ "repentance"
- **No semantic understanding**: Can't find concepts without exact words

### Hybrid Advantages
- **Semantic matching**: "charity" → finds "good deeds", "helping others"
- **Synonym handling**: "forgiveness" → finds "mercy", "repentance"
- **Best of both**: Exact matches ranked higher + semantic fallback

---

## Implementation: Reciprocal Rank Fusion (RRF)

```
Query → [FTS5 Keyword Search] ─┬─→ RRF Scoring → Final Results
        [Vector Semantic Search] ─┘

RRF Score = Σ 1 / (60 + rank)
```

**How it works:**
1. Get top 20 keyword results (FTS5)
2. Get top 20 semantic results (vectors)
3. Combine scores: `1/(60+rank_keyword) + 1/(60+rank_semantic)`
4. Sort by combined score
5. Return top 10

---

## Performance Comparison

| Metric | FTS5 | Hybrid |
|--------|------|--------|
| **Latency** | ~5ms | ~50ms (embedding gen) |
| **Memory** | ~1MB | ~100MB (model) |
| **Precision** | High (exact match) | High (combined) |
| **Recall** | Low (exact words only) | High (semantic + exact) |
| **Scalability** | Excellent (1M+ docs) | Good (100K+ docs) |

---

## Recommendation

### For Your Pipeline: **Use Hybrid Search** ✅

**Reasons:**
1. You already have 100% embedding coverage
2. Model is loaded (`all-MiniLM-L6-v2`)
3. Minimal code change (drop-in replacement)
4. Significantly better recall for conceptual queries

**When to use FTS5 only:**
- Ultra-low latency required (<10ms)
- Memory constrained (<50MB)
- Queries are always exact keywords

**When to use Hybrid:**
- Conceptual questions ("What is patience?")
- Synonym handling needed
- Better user experience priority

---

## Next Steps

### Option 1: Replace Current Retriever
```python
# In rag_engine.py
from rag.hybrid_retriever import HybridRetriever

class RAGEngine:
    def __init__(self):
        self.retriever = HybridRetriever()  # Instead of Retriever()
```

### Option 2: Add as Alternative Endpoint
```python
@app.post("/ask/hybrid")
async def ask_hybrid(request: QuestionRequest):
    results = hybrid_retriever.search(request.question, request.limit)
    # ... process with LLM
```

### Option 3: Fallback Chain
```
Query → FTS5 → If 0 results → Hybrid → Return
```

---

## Code Location

- **Hybrid Retriever**: `video_pipeline/rag/hybrid_retriever.py`
- **Current FTS5**: `video_pipeline/rag/retriever.py`
- **RAG Engine**: `video_pipeline/rag/rag_engine.py`

---

## Test It Yourself

```bash
cd video_pipeline
source ../.venv/bin/activate
PYTHONPATH=. python rag/hybrid_retriever.py
```

Try queries:
- "What is patience?"
- "charity in Islam"
- "forgiveness"
- "best deeds"
