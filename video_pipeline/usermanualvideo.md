# Video Pipeline User Manual

**Project:** Islamic Knowledge Harvester - Video Pipeline

**Version:** 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Adding Videos](#adding-videos)
5. [Running the Pipeline](#running-the-pipeline)
6. [Searching Transcripts](#searching-transcripts)
7. [Asking Questions (RAG)](#asking-questions-rag)
8. [Database Structure](#database-structure)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Overview

The Video Pipeline processes Islamic lecture videos and makes their content searchable. It extracts subtitles, chunks the transcript, and builds a search index for fast retrieval.

### Features

- **Offline Processing**: Works entirely offline with local video files
- **Full-Text Search**: FTS5-powered search across all transcripts
- **RAG Q&A**: Ask questions and get answers from lecture content
- **Web Interface**: Browser-based chat interface
- **API Access**: RESTful API for programmatic access

### Pipeline Flow

```
Video File → Subtitle → Chunk → Store → Search Index
                                      ↓
                              User Query → Retrieve → Answer
```

---

## Installation

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Git

### Step 1: Clone Repository

```bash
cd /mnt/AI/dev/huurs/video_pipeline
```

### Step 2: Activate Virtual Environment

```bash
source /mnt/AI/dev/huurs/.venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
yt-dlp
fastapi
uvicorn
pydantic
```

---

## Quick Start

### 1. Add a Video

Place your video file in the `videos/` directory:

```bash
cp /path/to/lecture.mp4 videos/
```

### 2. Add Subtitles (Required)

Place subtitle file with the same name as the video:

```bash
# Subtitle must be .srt or .vtt format
cp /path/to/lecture.en.srt videos/lecture.en.srt
```

**Supported subtitle formats:**
- `.srt` (SubRip)
- `.vtt` (WebVTT)

### 3. Run the Pipeline

```bash
python run_video_pipeline.py
```

### 4. Search or Ask Questions

**Option A: Web Interface**
```bash
python rag/rag_api.py
# Open browser: http://localhost:8000/ui/index.html
```

**Option B: Command Line Search**
```bash
python search_cli.py
```

---

## Adding Videos

### Directory Structure

```
video_pipeline/
├── videos/              # Place videos here
│   ├── lecture1.mp4
│   ├── lecture1.en.srt  # Subtitle (required)
│   └── lecture2.mp4
│   └── lecture2.en.srt
├── data/
│   ├── subtitles/       # Auto-created
│   └── fts_index/       # Auto-created search index
└── video_knowledge.db   # SQLite database
```

### Subtitle Requirements

**Format:** SRT or VTT

**Example SRT:**
```srt
1
00:00:01,000 --> 00:00:05,000
In the name of Allah, the Most Gracious, the Most Merciful.

2
00:00:06,000 --> 00:00:10,000
All praise is due to Allah, Lord of the worlds.
```

**Naming Convention:**
```
<video_name>.mp4
<video_name>.en.srt    # English subtitles
```

### Getting Subtitles

**Option 1: Download from YouTube**
```bash
yt-dlp --write-subs --sub-lang en --skip-download VIDEO_URL
```

**Option 2: Generate with Whisper**
```bash
whisper video.mp4 --language en --output_dir videos/
```

**Option 3: Manual Creation**
- Use Aegisub or Subtitle Edit
- Ensure timestamps are accurate

---

## Running the Pipeline

### Basic Usage

```bash
# Auto-detect videos in videos/ directory
python run_video_pipeline.py
```

### Output

```
[INFO] Found local video: videos/lecture1.mp4
[INFO] fetching metadata
[INFO] Video: lecture1
[INFO] Channel: Local Video
[INFO] downloading subtitles
[INFO] Found subtitle: videos/lecture1.en.srt
[INFO] Subtitle file: videos/lecture1.en.srt
[INFO] indexing subtitles
[INFO] Created offline index: data/fts_index/lecture1.db
[INFO] parsing subtitles
[INFO] processing 219 transcript chunks
  Storing chunk 1/219...
  Storing chunk 2/219...
  ...
  Storing chunk 219/219...
[INFO] building search index
[✓] pipeline completed
```

### Processing Time

| Video Length | Processing Time |
|--------------|-----------------|
| 30 minutes   | ~5 seconds      |
| 1 hour       | ~10 seconds     |
| 2 hours      | ~20 seconds     |

---

## Searching Transcripts

### Interactive CLI

```bash
python search_cli.py
```

**Commands:**

| Command | Description |
|---------|-------------|
| `search <query>` | Keyword search |
| `videos` | List all videos |
| `video <id>` | Show transcripts for video |
| `quit` | Exit |

**Example Session:**
```
> search Allah
Found 5 result(s):

[1] Video: lecture1
    Timestamp: 13.27
    Text: Look, we believe the word of Allah is perfect...

[2] Video: lecture1
    Timestamp: 55.67
    Text: ...the mercy of Allah upon us...

> videos
Videos (1):
  - lecture1: Islamic Lecture Series

> quit
Goodbye!
```

### Programmatic Search

```python
from modules.search.video_search import VideoSearch

search = VideoSearch()

# Keyword search
results = search.search("charity", limit=10)
for r in results:
    print(f"{r['video_id']} @ {r['timestamp']}: {r['text'][:100]}")

# Get all videos
videos = search.get_all_videos()

# Get video transcripts
transcripts = search.get_video_transcripts("lecture1")

search.close()
```

---

## Asking Questions (RAG)

### Web Interface

**1. Start the API server:**
```bash
python rag/rag_api.py
```

**2. Open in browser:**
```
http://localhost:8000/ui/index.html
```

**3. Ask questions:**
```
"What does Islam say about charity?"
"How can sins be forgiven?"
"What is the importance of patience?"
```

### API Usage

**Endpoint:** `POST /ask`

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does Islam say about charity?", "limit": 10}'
```

**Response (LLM Available):**
```json
{
  "answer": "Islam places great emphasis on charity...",
  "sources": [
    {"video_id": "lecture1", "timestamp": "13:27"},
    {"video_id": "lecture1", "timestamp": "45:12"}
  ],
  "llm_used": true
}
```

**Response (LLM Unavailable - Fallback):**
```json
{
  "answer": "[LLM unavailable - Showing retrieved transcript excerpts]\n\n[1] lecture1 @ 13:27\n    \"Charity is one of the most important deeds...\"\n\n[2] lecture1 @ 45:12\n    \"The Prophet said...\"",
  "sources": [...],
  "llm_used": false
}
```

### LLM Configuration

The RAG system uses LM Studio for LLM inference.

**Default Settings:**
- Base URL: `http://localhost:1234/v1`
- Model: `qwen/qwen3.5-9b`
- Timeout: 120 seconds

**Configure in `configs/settings.py`:**
```python
LMSTUDIO_BASE_URL = "http://localhost:1234/v1"
MODEL_NAME = "qwen/qwen3.5-9b"
TIMEOUT = 120
```

**Fallback Mode:**
If LM Studio is not running, the system automatically falls back to showing raw transcript excerpts.

---

## Database Structure

### SQLite Tables

**videos:**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| video_id | TEXT | Unique video identifier |
| title | TEXT | Video title |
| channel | TEXT | Channel/source name |
| url | TEXT | File path or URL |

**transcripts:**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| video_id | TEXT | Reference to video |
| timestamp | TEXT | Timestamp in video |
| text | TEXT | Transcript text |

**transcript_fts (FTS5 virtual table):**
| Column | Type | Description |
|--------|------|-------------|
| rowid | INTEGER | Reference to transcripts.id |
| text | TEXT | Indexed transcript text |

### Database Location

```
video_pipeline/video_knowledge.db
```

### Backup Database

```bash
# Backup
cp video_knowledge.db video_knowledge.db.backup

# Restore
cp video_knowledge.db.backup video_knowledge.db
```

---

## Troubleshooting

### No Subtitles Found

**Error:**
```
[!] No subtitles available. Pipeline halted.
```

**Solution:**
1. Ensure subtitle file exists next to video
2. Check file extension (.srt or .vtt)
3. Verify filename matches video (except extension)

```
✓ Correct:
  videos/lecture.mp4
  videos/lecture.en.srt

✗ Wrong:
  videos/lecture.mp4
  videos/subtitles.srt
```

### FTS5 Syntax Error

**Error:**
```
sqlite3.OperationalError: fts5: syntax error
```

**Solution:**
- Avoid special characters in search queries
- Use simple keywords: `charity` not `"charity"`

### LLM Timeout

**Error:**
```
Error: LLM request timed out
```

**Solution:**
1. Check if LM Studio is running
2. Increase timeout in `configs/settings.py`
3. Use fallback mode (automatic)

### Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
1. Close other processes using the database
2. Remove lock file: `rm video_knowledge.db-journal`

### No Search Results

**Possible causes:**
1. No videos processed yet
2. Query terms not in transcripts
3. FTS index needs rebuild

**Solution:**
```bash
# Check videos in database
python -c "from modules.search.video_search import VideoSearch; s = VideoSearch(); print(s.get_all_videos())"

# Re-run pipeline to rebuild index
python run_video_pipeline.py
```

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Redirect to UI |
| GET | `/ui/` | Web interface |
| POST | `/ask` | Ask a question |
| GET | `/health` | Health check |

### POST /ask

**Request Body:**
```json
{
  "question": "string (required)",
  "limit": "integer (optional, default: 10)"
}
```

**Response:**
```json
{
  "answer": "string",
  "sources": [
    {
      "video_id": "string",
      "timestamp": "string"
    }
  ],
  "llm_used": "boolean"
}
```

### GET /health

**Response:**
```json
{
  "status": "healthy",
  "llm_available": true
}
```

---

## Commands Summary

| Command | Description |
|---------|-------------|
| `python run_video_pipeline.py` | Process videos |
| `python search_cli.py` | Interactive search |
| `python rag/rag_api.py` | Start API server |
| `python test_search.py` | Test search |
| `python test_rag.py` | Test RAG |

---

## Support

For issues or questions:
1. Check this manual
2. Review error messages
3. Check logs in console output

---

**End of User Manual**
