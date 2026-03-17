# 🎬 Clip Mining Pipeline

**Automatically extract viral clips from Islamic lectures using AI**

This pipeline transforms long lecture videos into short, shareable clips suitable for social media platforms like YouTube Shorts, TikTok, and Instagram Reels.

---

## Features

- ✅ **Topic Classification** - Automatically categorizes segments (Charity, Dua, Mercy, etc.)
- ✅ **Emotional Impact Scoring** - Rates segments 1-10 for viral potential
- ✅ **Keyword Detection** - Pre-filters content to reduce processing time
- ✅ **GPU Acceleration** - Runs on free Google Colab GPU (Tesla T4)
- ✅ **Adjacent Segment Merging** - Combines related clips into coherent segments
- ✅ **FFmpeg Extraction** - Auto-cuts video clips from source files
- ✅ **Database Integration** - Stores clip metadata in SQLite
- ✅ **RAG Integration** - Search and discover clips via semantic search

---

## Architecture

```
YouTube Lecture
     ↓
Subtitle Extraction
     ↓
Transcript Chunking
     ↓
AI Classification (Colab GPU)
     ↓
Clip Candidate Detection
     ↓
Timestamp Merging
     ↓
FFmpeg Clip Extraction
     ↓
Database Storage
```

---

## Directory Structure

```
clip_pipeline/
├── __init__.py           # Package exports
├── detect_clips.py       # Clip detection logic
├── extract_clips.py      # FFmpeg-based extraction
├── clips_db.py           # Database management
├── clip_retriever.py     # RAG integration
├── run_pipeline.py       # Main pipeline runner
└── clip_mining_gpu.ipynb # Google Colab notebook
```

---

## Quick Start

### Option 1: Local Pipeline (Recommended)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the pipeline
python -m clip_pipeline.run_pipeline \
    --transcript data/chunks.json \
    --video-id lecture_001 \
    --title "The Power of Charity" \
    --min-score 7
```

### Option 2: Google Colab (GPU Accelerated)

1. Open `clip_pipeline/clip_mining_gpu.ipynb` in Google Colab
2. Enable GPU runtime: **Runtime → Change runtime type → GPU**
3. Upload your `chunks.json` file
4. Run all cells
5. Download `clip_candidates_*.json`
6. Use ffmpeg commands to extract clips locally

---

## Usage Examples

### Detect Clip Candidates

```python
from clip_pipeline import ClipDetector

detector = ClipDetector(emotion_threshold=7)

# Load transcripts
chunks = detector.load_transcripts("data/chunks.json")

# Process chunks
processed = detector.process_batch(chunks)

# Filter candidates
candidates = [c for c in processed if c.get("clip_candidate")]

print(f"Found {len(candidates)} clip candidates")
```

### Extract Video Clips

```python
from clip_pipeline import ClipExtractor

extractor = ClipExtractor(output_dir="clips")

# Extract single clip
clip_path = extractor.extract_clip(
    video_path="videos/lecture.mp4",
    start_time="02:30",
    end_time="03:15",
    output_name="charity_clip"
)

# Extract multiple clips from moments
moments = [
    {"timestamp_start": "02:30", "timestamp_end": "03:15", "topic": "Charity"},
    {"timestamp_start": "05:00", "timestamp_end": "05:45", "topic": "Dua"}
]

clip_paths = extractor.extract_clips_from_moments(
    video_path="videos/lecture.mp4",
    moments=moments
)
```

### Store Clips in Database

```python
from clip_pipeline import ClipsDB

with ClipsDB("database/clips.db") as db:
    # Insert single clip
    clip_id = db.insert_clip(
        video_id="lecture_001",
        video_title="The Power of Charity",
        start_time="02:30",
        end_time="03:15",
        start_seconds=150,
        end_seconds=195,
        duration=45,
        topic="Charity",
        emotion_score=8,
        file_path="clips/lecture_001_clip_001_Charity.mp4"
    )
    
    # Get top clips
    top_clips = db.get_top_clips(limit=10)
    
    # Search by topic
    charity_clips = db.get_clips_by_topic("Charity", limit=20)
    
    # Get statistics
    stats = db.get_stats()
    print(f"Total clips: {stats['total_clips']}")
```

### RAG Search with Clips

```python
from clip_pipeline import ClipRetriever

retriever = ClipRetriever()

# Search with clip integration
results = retriever.search_with_clips(
    query="charity in Islam",
    limit=10,
    clip_limit=5
)

print(f"Found {len(results['clips'])} relevant clips")
print(f"Found {len(results['chunks'])} transcript chunks")

retriever.close()
```

---

## Clip Detection Strategy

Clips are detected using **three signals**:

### 1. Topic Classification

Valid topics:
- Charity
- Oppression
- Dua (Supplication)
- Mercy
- Death
- Tawakkul (Trust in Allah)
- Sabr (Patience)
- Afterlife
- Faith
- Prayer
- Quran
- Hadith
- Other

### 2. Emotional Impact Scoring

Score range: **1-10**

Factors:
- Emotional keywords (+2)
- Religious content (+1)
- Teaching indicators (+1)
- Important topics (+1)

**Threshold:** Score ≥7 → Clip candidate

### 3. Keyword Detection

Pre-filtering keywords:
- `allah`, `prophet`, `quran`, `hadith`
- `zakat`, `sadaqah`, `charity`
- `dua`, `supplication`, `mercy`
- `paradise`, `hellfire`, `afterlife`

Chunks without keywords skip LLM processing (saves GPU time).

---

## Clip Merging Rules

Adjacent clips are merged when:

1. **Time gap ≤ 10 seconds** between segments
2. **Duration within limits** (15-60 seconds)
3. **Same video source**

Merged clip properties:
- **Topic:** Most common topic from merged segments
- **Emotion Score:** Maximum score from merged segments
- **Duration:** Sum of merged segment durations

---

## Colab GPU Processing

### Model Configuration

- **Model:** Qwen2.5-3B-Instruct (available on Hugging Face)
- **Batch Size:** 8-12 chunks (T4 GPU)
- **Precision:** Float16
- **VRAM Usage:** ~6-8 GB on Tesla T4
- **Processing Speed:** ~70-100 chunks/minute

### Performance Targets

| Dataset Size | Processing Time | Clip Candidates |
|--------------|-----------------|-----------------|
| 100 chunks   | 1-2 min         | 10-20           |
| 500 chunks   | 5-7 min         | 40-80           |
| 700 chunks   | 7-10 min        | 60-100          |

---

## Database Schema

### clips Table

```sql
CREATE TABLE clips(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    video_title TEXT,
    start_time TEXT,        -- MM:SS format
    end_time TEXT,          -- MM:SS format
    start_seconds REAL,
    end_seconds REAL,
    duration REAL,
    topic TEXT,
    all_topics TEXT,        -- Comma-separated for merged clips
    emotion_score INTEGER,  -- 1-10
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Indexes

- `idx_clips_topic` - Fast topic searches
- `idx_clips_video` - Fast video-specific queries
- `idx_clips_score` - Top clips ordering

---

## FFmpeg Commands

### Basic Clip Extraction

```bash
ffmpeg -ss 02:30 -to 03:15 -i lecture.mp4 clip_001.mp4
```

### With Subtitle Overlay

```bash
ffmpeg -i lecture.mp4 -ss 02:30 -to 03:15 \
    -vf "subtitles=subs.srt" clip_001.mp4
```

### Vertical Format (9:16 for Shorts/Reels)

```bash
ffmpeg -i lecture.mp4 -ss 02:30 -to 03:15 \
    -vf "crop=ih*(9/16):ih" clip_001_vertical.mp4
```

---

## API Reference

### ClipDetector

```python
ClipDetector(emotion_threshold=7)
  .has_important_content(text) → bool
  .calculate_emotion_score(text, topic, summary) → int
  .detect_keywords(text) → list[str]
  .classify_topic(text) → str
  .process_chunk(chunk, use_llm=False, llm_client=None) → dict
  .process_batch(chunks, use_llm=False, llm_client=None) → list[dict]
  .merge_adjacent_clips(candidates, max_duration=60, min_duration=15) → list[dict]
  .load_transcripts(filepath) → list[dict]
  .save_candidates(candidates, filepath) → None
```

### ClipExtractor

```python
ClipExtractor(output_dir="clips")
  .extract_clip(video_path, start_time, end_time, output_name) → str
  .extract_clips_from_moments(video_path, moments, clip_duration=60) → list[str]
  .create_vertical_clip(video_path, start_time, end_time, output_name) → str
  .get_video_duration(video_path) → float
  .format_timestamp(seconds) → str
  .format_timestamp_hms(seconds) → str
```

### ClipsDB

```python
ClipsDB(db_path="database/clips.db")
  .insert_clip(...) → int
  .insert_clips_batch(clips) → int
  .get_clip(clip_id) → Row
  .get_clips_by_topic(topic, limit=20) → list[Row]
  .get_clips_by_video(video_id, limit=50) → list[Row]
  .get_top_clips(limit=20) → list[Row]
  .search_clips(query, limit=20) → list[Row]
  .get_candidate_clips(min_score=7, limit=100) → list[Row]
  .update_clip_file(clip_id, file_path) → None
  .delete_clip(clip_id) → None
  .get_stats() → dict
  .close() → None
```

---

## Testing

Run module tests:

```bash
# Test ClipDetector
python -m clip_pipeline.detect_clips

# Test ClipExtractor
python -m clip_pipeline.extract_clips

# Test ClipsDB
python -m clip_pipeline.clips_db

# Test ClipRetriever
python -m clip_pipeline.clip_retriever
```

---

## Troubleshooting

### No GPU Detected in Colab

1. Go to **Runtime → Change runtime type**
2. Select **GPU** → **T4**
3. Click **Save**
4. Restart the notebook

### FFmpeg Not Found

Install FFmpeg:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Clip Extraction Fails

Check:
1. Video file exists at specified path
2. Timestamps are valid (start < end)
3. FFmpeg is installed and in PATH

### No Clip Candidates Found

Try:
1. Lower `min_score` threshold (e.g., 6 instead of 7)
2. Check transcript quality (may need better subtitles)
3. Verify transcript contains Islamic keywords

---

## Future Enhancements

Phase 2 features:

- [ ] Semantic embeddings for clip clustering
- [ ] Automatic title generation for clips
- [ ] Vertical video formatting automation
- [ ] Auto subtitle styling
- [ ] Auto social media posting integration
- [ ] Clip thumbnail generation
- [ ] A/B testing for clip performance

---

## Related Documentation

- [Clip Mining Pipeline Spec](../Clippipeline.md)
- [Topic Cluster Mining](../Cliptopiccluster.md)
- [Video Pipeline Guide](../video_pipeline/VIDEO_PIPELINE_GUIDE.md)

---

## License

Part of the Islamic Knowledge Harvester project.
