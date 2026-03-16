# 📚 Video Pipeline Documentation Index

**Complete documentation for Islamic Knowledge Harvester**

---

## 🚀 Getting Started

| Document | Purpose | Who Should Read |
|----------|---------|-----------------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute quick reference | Everyone (start here!) |
| **[VIDEO_PIPELINE_GUIDE.md](VIDEO_PIPELINE_GUIDE.md)** | Complete step-by-step guide | New users |

---

## 📖 User Guides

### For End Users

| Document | Description |
|----------|-------------|
| `QUICKSTART.md` | Quick reference for common tasks |
| `VIDEO_PIPELINE_GUIDE.md` | Complete workflow from download to RAG |
| `colab/README.md` | Google Colab usage guide |
| `COLAB_QUICKSTART.md` | Colab quick reference |

### For Developers

| Document | Description |
|----------|-------------|
| `GPU_MANAGER_IMPLEMENTATION.md` | GPU manager features & usage |
| `OPTIMIZED_PIPELINE_SUMMARY.md` | Optimizations implemented |
| `RETRIEVAL_COMPARISON.md` | FTS5 vs Hybrid search comparison |

---

## 🎯 Task-Based Navigation

### I want to...

| Task | Document | Section |
|------|----------|---------|
| **Process a new video** | `VIDEO_PIPELINE_GUIDE.md` | Steps 1-3 |
| **Use Google Colab** | `colab/README.md` | Full guide |
| **Resume Colab processing** | `VIDEO_PIPELINE_GUIDE.md` | Step 4.6 |
| **Import results** | `VIDEO_PIPELINE_GUIDE.md` | Step 5 |
| **Generate embeddings** | `VIDEO_PIPELINE_GUIDE.md` | Step 6 |
| **Start RAG server** | `VIDEO_PIPELINE_GUIDE.md` | Step 7 |
| **Use web UI** | `VIDEO_PIPELINE_GUIDE.md` | Step 8 |
| **Troubleshoot** | `VIDEO_PIPELINE_GUIDE.md` | Troubleshooting |

---

## 📁 File Reference

### Documentation Files

```
video_pipeline/
├── README.md                      ← This file (index)
├── QUICKSTART.md                  ← Quick reference
├── VIDEO_PIPELINE_GUIDE.md        ← Complete guide
├── COLAB_QUICKSTART.md            ← Colab quick ref
├── GPU_MANAGER_IMPLEMENTATION.md  ← GPU manager docs
├── OPTIMIZED_PIPELINE_SUMMARY.md  ← Optimizations
└── RETRIEVAL_COMPARISON.md        ← Search comparison
```

### Code Files

```
video_pipeline/
├── run_video_pipeline.py          ← Main pipeline
├── enrich_per_video.py            ← Enrichment script
├── add_embeddings_per_video.py    ← Embedding generator
├── monitor_progress.py            ← Progress checker
├── colab/
│   ├── export_chunks.py           ← Export for Colab
│   ├── import_results.py          ← Import results
│   └── gpu_manager.py             ← GPU management
└── colab_notebook/
    ├── colab_pipeline_gpu_manager.ipynb  ← Recommended
    ├── colab_pipeline_optimized.ipynb    ← Optimized
    └── colab_embeddings.ipynb            ← Embeddings
```

---

## 🔧 Quick Commands

### Processing

```bash
# Process video
python run_video_pipeline.py "/path/to/video.mp4"

# Export for Colab
python colab/export_chunks.py

# Import results
python colab/import_results.py processed_chunks.json

# Generate embeddings
python add_embeddings_per_video.py

# Check progress
python monitor_progress.py
```

### RAG Server

```bash
# Start server
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000

# Test API
curl http://localhost:8000/health
```

---

## 🎓 Learning Path

### Beginner

1. Read: `QUICKSTART.md`
2. Follow: `VIDEO_PIPELINE_GUIDE.md` (all 8 steps)
3. Reference: `colab/README.md` for Colab questions

### Intermediate

1. Read: `GPU_MANAGER_IMPLEMENTATION.md`
2. Read: `OPTIMIZED_PIPELINE_SUMMARY.md`
3. Understand: Checkpoint & resume workflow

### Advanced

1. Read: `RETRIEVAL_COMPARISON.md`
2. Customize: Batch sizes, prompts, keywords
3. Extend: Add new features to pipeline

---

## 📊 Performance Benchmarks

| Dataset | Chunks | Processing Time | Embeddings | Total |
|---------|--------|-----------------|------------|-------|
| Surah Al Mulk | 596 | 7 min (Colab) | 0.2 min | ~10 min |
| Surah Ar-Rahman | 438 | 5 min (Colab) | 0.1 min | ~8 min |
| Combined | 1034 | 12 min (Colab) | 0.3 min | ~18 min |

**Note:** Times vary based on GPU availability and network speed.

---

## 🆘 Support

### Troubleshooting

See: `VIDEO_PIPELINE_GUIDE.md` → [Troubleshooting](VIDEO_PIPELINE_GUIDE.md#troubleshooting)

### Common Issues

| Issue | Solution |
|-------|----------|
| Colab disconnects | Auto-resume from checkpoint |
| No GPU available | Runtime → GPU → T4 |
| Import fails | Check file exists, rebuild FTS |
| RAG returns no results | Rebuild FTS index, restart server |

---

## 📈 Feature Status

| Feature | Status | Documented |
|---------|--------|------------|
| Per-video databases | ✅ Complete | `VIDEO_PIPELINE_GUIDE.md` |
| Google Colab GPU | ✅ Complete | `colab/README.md` |
| Auto-checkpointing | ✅ Complete | `GPU_MANAGER_IMPLEMENTATION.md` |
| Hybrid search | ✅ Complete | `RETRIEVAL_COMPARISON.md` |
| Clip scoring | ✅ Complete | `OPTIMIZED_PIPELINE_SUMMARY.md` |
| Embeddings | ✅ Complete | `VIDEO_PIPELINE_GUIDE.md` |
| Google Drive sync | ⏳ Planned | - |

---

## 🎬 Example Workflow

```bash
# 1. Download
yt-dlp --write-subs --sub-lang en "VIDEO_URL"

# 2. Process locally
python run_video_pipeline.py "video.mp4"

# 3. Export
python colab/export_chunks.py

# 4. [Colab] Process on GPU
# Upload notebook + chunks.json, run all cells

# 5. Import
python colab/import_results.py processed_chunks.json

# 6. Embeddings
python add_embeddings_per_video.py

# 7. Verify
python monitor_progress.py

# 8. Start RAG
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
```

---

## 📚 Additional Resources

| Resource | Link |
|----------|------|
| Google Colab | https://colab.research.google.com/ |
| RAG Web UI | http://localhost:8000 |
| Main Project | `/mnt/AI/dev/huurs/` |
| Video Pipeline | `/mnt/AI/dev/huurs/video_pipeline/` |

---

## 📝 Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-16 | 2.0 | GPU manager, checkpoints, per-video DBs |
| 2026-03-15 | 1.0 | Initial pipeline implementation |

---

**Last Updated:** 2026-03-16

**Maintained by:** Video Pipeline Team

---

**🎉 Ready to start? Open [QUICKSTART.md](QUICKSTART.md)!**
