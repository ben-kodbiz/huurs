# 🚀 Video Pipeline - Complete User Guide

**Islamic Knowledge Harvester - From Video to RAG Search**

This guide covers the complete workflow: downloading videos → processing with Google Colab GPU → importing results → using RAG search.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Download Video](#step-1-download-video)
4. [Step 2: Process Video Locally](#step-2-process-video-locally)
5. [Step 3: Export for Colab](#step-3-export-for-colab)
6. [Step 4: Process on Google Colab](#step-4-process-on-google-colab)
7. [Step 5: Import Results](#step-5-import-results)
8. [Step 6: Generate Embeddings](#step-6-generate-embeddings)
9. [Step 7: Start RAG Server](#step-7-start-rag-server)
10. [Step 8: Use Web UI](#step-8-use-web-ui)
11. [Troubleshooting](#troubleshooting)
12. [Quick Reference](#quick-reference)

---

## Overview

### Pipeline Flow

```
Download Video → Extract Subtitles → Chunk Transcripts → Export to Colab
                                                              ↓
Use RAG Search ← Import to Database ← Download Results ← GPU Process
```

### What Each Step Does

| Step | Location | Time | Purpose |
|------|----------|------|---------|
| Download | Local | 5-10 min | Get video file |
| Process locally | Local | 2-5 min | Extract subtitles, chunk transcripts |
| Export | Local | 10 sec | Create JSON for Colab |
| GPU Process | Colab | 7-10 min | Summarize & classify with AI |
| Import | Local | 30 sec | Save to database |
| Embeddings | Local | 2-5 min | Generate vector embeddings |
| RAG Server | Local | - | Start search interface |

---

## Prerequisites

### Local Setup

**1. Virtual Environment:**
```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate
```

**2. Required Packages:**
```bash
pip install transformers accelerate sentencepiece torch pytesseract pillow beautifulsoup4 requests yt-dlp
```

**3. Directory Structure:**
```
video_pipeline/
├── videos/              # Place downloaded videos here
├── data/
│   ├── db/             # Per-video databases (auto-created)
│   ├── subtitles/      # Extracted subtitles
│   └── fts_index/      # Search indexes
├── colab/              # Colab scripts
└── colab_notebook/     # Colab notebooks
```

### Google Colab Requirements

- Google account (free)
- Internet connection
- Modern web browser (Chrome/Firefox)

---

## Step 1: Download Video

### Option A: Manual Download (Recommended)

1. **Download video from YouTube or other source**
   - Use your preferred method
   - Save to: `video_pipeline/videos/`

2. **Ensure subtitles are available:**
   - YouTube videos usually have auto-generated subtitles
   - Preferred: English subtitles (manual or auto)

### Option B: Using yt-dlp (Command Line)

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Download video with subtitles
yt-dlp --write-subs --sub-lang en --skip-download "VIDEO_URL"

# Or download full video with subtitles
yt-dlp --write-subs --sub-lang en "VIDEO_URL"
```

**Output:**
- `video_title.mp4` - Video file
- `video_title.en.vtt` or `video_title.en.srt` - Subtitles

### Supported Formats

- **Video:** MP4, MKV, AVI, MOV
- **Subtitles:** SRT, VTT
- **Location:** `video_pipeline/videos/`

---

## Step 2: Process Video Locally

### Run Video Pipeline

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Process specific video
python run_video_pipeline.py "/path/to/your/video.mp4"

# Or process first video in videos/ directory
python run_video_pipeline.py
```

### What Happens

1. **Metadata extraction** - Video ID, title, channel
2. **Subtitle detection** - Finds or downloads subtitles
3. **Transcript chunking** - Splits into ~8-line segments
4. **Database creation** - Creates per-video database
5. **FTS index** - Builds search index

### Output

```
[INFO] fetching metadata
[INFO] Video: Your Video Title
[INFO] Channel: Channel Name
[INFO] Database: data/db/Your_Video_Title.db
[INFO] downloading subtitles
[INFO] Subtitle file: /path/to/subtitle.srt
[INFO] indexing subtitles
[INFO] parsing subtitles
[INFO] processing 596 transcript chunks
  Storing chunk 1/596...
  ...
[✓] pipeline completed
[INFO] Database location: data/db/Your_Video_Title.db
```

### Verify Processing

```bash
# Check database created
ls -lh data/db/

# Should see: Your_Video_Title.db
```

---

## Step 3: Export for Colab

### Export Pending Chunks

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Export all pending chunks
python colab/export_chunks.py

# Or export from specific video
python colab/export_chunks.py --video "Your Video Title"
```

### Output

```
======================================================================
EXPORTING PENDING CHUNKS FOR COLAB PROCESSING
======================================================================

✓ Your_Video_Title...
    Total: 596, Processed: 0, Pending: 596

TOTAL CHUNKS TO PROCESS: 596

✓ Exported to: chunks.json
  File size: 380.5 KB

======================================================================
NEXT STEPS:
======================================================================
1. Open Google Colab: https://colab.research.google.com/
2. Upload the notebook: colab_notebook/colab_pipeline_gpu_manager.ipynb
3. Upload this file: chunks.json
4. Run all cells (GPU will process the chunks)
5. Download: processed_chunks.json
6. Run: python colab/import_results.py processed_chunks.json
======================================================================
```

### Files Created

- `chunks.json` - Ready for upload to Colab

---

## Step 4: Process on Google Colab

### 4.1 Open Colab

1. **Go to:** https://colab.research.google.com/

2. **Upload Notebook:**
   - Click `File` → `Upload notebook`
   - Select: `video_pipeline/colab_notebook/colab_pipeline_gpu_manager.ipynb`
   - Click `Upload`

### 4.2 Enable GPU (CRITICAL!)

1. Click `Runtime` → `Change runtime type`

2. Settings:
   - **Hardware accelerator:** GPU
   - **GPU type:** T4 (free tier)
   - Click `Save`

> ⚠️ **Without GPU, processing takes 10x longer!**

### 4.3 Upload chunks.json

1. Click the **📁 folder icon** on left sidebar

2. Click the **⬆️ upload icon**

3. Select: `video_pipeline/chunks.json`

4. Wait for upload (file appears in `/content/`)

### 4.4 Run All Cells

**Execute cells in order** (click ▶️ on each):

| Cell | Name | Time | What It Does |
|------|------|------|--------------|
| 1 | Install Dependencies | 30 sec | Installs AI libraries |
| 2 | Initialize GPU Manager | 5 sec | Detects T4 GPU, mounts Drive |
| 3 | Load Files | 10 sec | Loads chunks.json |
| 4 | Load AI Model | 60 sec | Downloads Qwen2.5-3B |
| 5 | Process with Checkpointing | 7-10 min | **Main processing** |
| 6 | Save & Download | 10 sec | Saves results |
| 7 | Download Results | Auto | Downloads file |

### 4.5 Processing Details

**Cell 5 shows progress:**
```
Processing Configuration:
  Total chunks: 596
  Starting from: 0
  Batch size: 8
  Checkpoint interval: every 5 batches

Processing batch 1/75...
  ⏭️ Chunk 1/596 - Skipped (generic)
  ✓ Chunk 2/596 - 🎬 Topic: Knowledge/Wisdom (Score: 8)
  ✓ Chunk 3/596 - Topic: Quran/Sunnah (Score: 5)
  ...
  💾 Checkpoint saved: 40/596 chunks
  📊 Progress: 6.7% | ETA: 8.5 min
```

### 4.6 If Disconnected

**Don't worry!** Checkpoints are saved to Google Drive.

1. **Re-open notebook**
2. **Run all cells from start**
3. **When prompted:**
   ```
   CHECKPOINT FOUND - MANUAL RESUME
   Progress: 250/596 chunks (42.0%)
   
   [R] Resume from checkpoint
   [N] Start fresh
   
   Your choice (R/N): R
   ```
4. **Type `R`** to resume from checkpoint
5. **Continues processing** from where it stopped

### 4.7 Download Results

**Automatic download** after Cell 7:
- File: `processed_chunks.json`
- Size: ~500 KB for 596 chunks

**Save to:** `video_pipeline/` directory

---

## Step 5: Import Results

### Import to Database

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Import processed chunks
python colab/import_results.py processed_chunks.json
```

### Output

```
======================================================================
IMPORTING COLAB PROCESSING RESULTS
======================================================================

✓ Loaded 596 processed chunks
⚠ No embeddings - will need to generate locally

Chunks by database:
  Your_Video_Title: 596 chunks

Processing: Your_Video_Title
  Imported 50/596...
  Imported 100/596...
  ...
  Rebuilding search index...
  ✓ Imported: 596, Failed: 0

======================================================================
IMPORT COMPLETE
======================================================================
  Total processed: 596
  Successfully imported: 596
  Failed: 0

✓ All chunks imported successfully!

NEXT STEPS:
  1. Run: python add_embeddings_per_video.py (generate embeddings)
  2. Run: python monitor_progress.py (to see updated stats)
  3. Start RAG server: python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
======================================================================
```

### Verify Import

```bash
# Check progress
python monitor_progress.py
```

---

## Step 6: Generate Embeddings

### Run Embedding Generator

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Generate embeddings for all videos
python add_embeddings_per_video.py
```

### Output

```
======================================================================
VECTOR EMBEDDING GENERATOR (Per-Video)
======================================================================

[1] Finding video databases...
    Found 2 video database(s)
      - Your_Video_Title.db
      - Another_Video.db

[2] Total pending embeddings: 596
    Estimated time: 33 minutes

Starting embedding generation...
======================================================================

Video: Your_Video_Title
Database: data/db/Your_Video_Title.db
======================================================================
Pending embeddings: 596

  [20/596] 3.4% | Elapsed: 0.1m | ETA: 2 minutes
  [40/596] 6.7% | Elapsed: 0.1m | ETA: 1 minutes
  ...
  [596/596] 100.0% | Elapsed: 0.2m

✓ Generated 596 embeddings in 0.2 minutes

======================================================================
[3] EMBEDDING COMPLETE!
    Total embedded: 596 chunks
    Total time: 0.2 minutes
======================================================================
```

### Verify Embeddings

```bash
python monitor_progress.py
```

**Expected output:**
```
Your_Video_Title...
  📄 Transcripts: 596
  ✨ Enriched: 596/596 (100.0%)
  🔢 Embeddings: 596/596 (100.0%)
```

---

## Step 7: Start RAG Server

### Start Server

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Start RAG server
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
```

### Output

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Verify Server

Open new terminal:
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"healthy","llm_available":true}
```

### Stop Server

Press `Ctrl+C` in the terminal running the server.

---

## Step 8: Use Web UI

### Access Web Interface

**Open browser:** http://localhost:8000

### Features

1. **Chat Interface**
   - Type questions in the input box
   - Click "Send" or press Enter

2. **Example Questions**
   - Click preset questions to try quickly

3. **Sources**
   - Each answer shows source timestamps
   - Click to see which video segments were used

### Example Questions

```
# Surah Al Mulk content
"who is better in deed"
"protection from hellfire"
"understanding vs memorization"

# Surah Ar-Rahman content
"What is the best?"
"Tell me about Surah Ar-Rahman"
"What does Allah say about parents?"

# General Islamic questions
"charity in Islam"
"patience and gratitude"
"day of judgment"
```

### Response Format

```
✨ AI-generated answer

[Answer text generated by LLM]

📖 Sources
  Video 1: Video Title @ timestamp
  Video 2: Another Title @ timestamp
```

---

## Troubleshooting

### Problem: "No GPU available" in Colab

**Solution:**
1. Runtime → Change runtime type
2. Select GPU → T4
3. Save and refresh page

---

### Problem: "chunks.json not found"

**Solution:**
```bash
# Re-export chunks
python colab/export_chunks.py

# Verify file exists
ls -lh chunks.json
```

---

### Problem: Colab disconnected

**Solution:**
1. Re-open notebook
2. Run all cells
3. When prompted, type `R` to resume from checkpoint
4. Continue processing

---

### Problem: Import fails

**Solution:**
```bash
# Check file exists
ls -lh processed_chunks.json

# Verify JSON is valid
python -c "import json; json.load(open('processed_chunks.json'))"

# Re-import
python colab/import_results.py processed_chunks.json
```

---

### Problem: "No lecture content matched"

**Causes:**
1. Question not in transcripts
2. FTS index not rebuilt

**Solution:**
```bash
# Rebuild FTS index
python -c "
from database.per_video_db import get_all_video_dbs, PerVideoDB
for db_path in get_all_video_dbs():
    video_id = db_path.split('/')[-1].replace('.db', '').replace('_', ' ')
    db = PerVideoDB(video_id)
    db.create_fts_index()
    db.close()
print('FTS indexes rebuilt!')
"

# Restart server
pkill -f uvicorn
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
```

---

### Problem: RAG server won't start

**Solution:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f uvicorn

# Restart
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
```

---

## Quick Reference

### Complete Workflow (One Command Each)

```bash
# 1. Download video (manual or yt-dlp)
yt-dlp --write-subs --sub-lang en "VIDEO_URL"

# 2. Process locally
python run_video_pipeline.py "/path/to/video.mp4"

# 3. Export for Colab
python colab/export_chunks.py

# 4. [In Colab] Process on GPU
# Upload colab_pipeline_gpu_manager.ipynb + chunks.json
# Run all cells, download processed_chunks.json

# 5. Import results
python colab/import_results.py processed_chunks.json

# 6. Generate embeddings
python add_embeddings_per_video.py

# 7. Check progress
python monitor_progress.py

# 8. Start RAG server
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000

# 9. Open browser: http://localhost:8000
```

### File Locations

| File | Location | Purpose |
|------|----------|---------|
| Videos | `videos/` | Downloaded videos |
| Databases | `data/db/` | Per-video databases |
| Export | `chunks.json` | For Colab upload |
| Import | `processed_chunks.json` | From Colab download |
| Notebooks | `colab_notebook/` | Colab notebooks |

### Colab Notebooks

| Notebook | Use Case |
|----------|----------|
| `colab_pipeline_gpu_manager.ipynb` | **Recommended** - Auto GPU detection, checkpoints |
| `colab_pipeline_optimized.ipynb` | Basic processing (no GPU manager) |
| `colab_embeddings.ipynb` | Generate embeddings in Colab (optional) |

### Common Commands

```bash
# Check progress
python monitor_progress.py

# List videos
ls data/db/*.db

# Rebuild FTS index
python -c "from database.per_video_db import PerVideoDB; db = PerVideoDB('video_name'); db.create_fts_index()"

# Test RAG API
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "your question", "limit": 5}'
```

---

## Performance Estimates

| Task | Time (500 chunks) | Time (1000 chunks) |
|------|-------------------|--------------------|
| Local processing | 2-5 min | 5-10 min |
| Colab GPU processing | 5-7 min | 10-15 min |
| Import | 30 sec | 1 min |
| Embeddings | 2-3 min | 5-6 min |
| **Total** | **~10-15 min** | **~20-30 min** |

---

## Support Files

| Document | Location |
|----------|----------|
| This Guide | `VIDEO_PIPELINE_GUIDE.md` |
| Colab Quick Start | `colab/README.md` |
| GPU Manager | `GPU_MANAGER_IMPLEMENTATION.md` |
| Optimized Pipeline | `OPTIMIZED_PIPELINE_SUMMARY.md` |
| Retrieval Comparison | `RETRIEVAL_COMPARISON.md` |

---

## Next Steps

After mastering the basic workflow:

1. **Batch Processing** - Process multiple videos at once
2. **Clip Generation** - Use `clip_candidate` scores for video clips
3. **Semantic Search** - Leverage embeddings for advanced queries
4. **Automation** - Script the entire pipeline

---

**🎉 You're ready to harvest Islamic knowledge from videos!**

For questions or issues, check the Troubleshooting section or review the specific step documentation.
