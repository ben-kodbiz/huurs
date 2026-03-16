# 🚀 Quick Start - Video Pipeline

**5-Minute Guide: From Video to RAG Search**

---

## Complete Workflow

### 1️⃣ Download Video
```bash
# Save to: video_pipeline/videos/
yt-dlp --write-subs --sub-lang en "VIDEO_URL"
```

### 2️⃣ Process Locally
```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate
python run_video_pipeline.py "/path/to/video.mp4"
```

### 3️⃣ Export for Colab
```bash
python colab/export_chunks.py
# Creates: chunks.json
```

### 4️⃣ Process on Colab
1. Open: https://colab.research.google.com/
2. Upload: `colab_notebook/colab_pipeline_gpu_manager.ipynb`
3. Enable GPU: Runtime → GPU → T4
4. Upload: `chunks.json`
5. Run all cells (7-10 min)
6. Download: `processed_chunks.json`

### 5️⃣ Import Results
```bash
python colab/import_results.py processed_chunks.json
```

### 6️⃣ Generate Embeddings
```bash
python add_embeddings_per_video.py
```

### 7️⃣ Start RAG Server
```bash
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
```

### 8️⃣ Use Web UI
**Open:** http://localhost:8000

---

## One-Liner Commands

```bash
# Check progress
python monitor_progress.py

# List videos
ls data/db/*.db

# Test RAG
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "test", "limit": 3}'
```

---

## File Checklist

- [ ] `videos/your_video.mp4` - Downloaded video
- [ ] `data/db/your_video.db` - Created by pipeline
- [ ] `chunks.json` - Exported for Colab
- [ ] `processed_chunks.json` - Downloaded from Colab
- [ ] RAG server running on port 8000

---

## Time Estimates

| Step | Time |
|------|------|
| Download | 5-10 min |
| Local process | 2-5 min |
| Colab processing | 7-10 min |
| Import | 30 sec |
| Embeddings | 2-3 min |
| **Total** | **~20 min** |

---

## Common Issues

| Problem | Fix |
|---------|-----|
| No GPU in Colab | Runtime → GPU → T4 |
| Import fails | Check file exists: `ls processed_chunks.json` |
| RAG not working | Rebuild FTS: `python -c "from database.per_video_db import get_all_video_dbs, PerVideoDB; [PerVideoDB(p.split('/')[-1].replace('.db','')).create_fts_index() for p in get_all_video_dbs()]"` |

---

## Full Documentation

See: `VIDEO_PIPELINE_GUIDE.md` for detailed instructions.
