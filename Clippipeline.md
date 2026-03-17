# clip_mining_pipeline.md

Branch: `feature/clip-mining`

Purpose:
Implement an **AI-assisted lecture clip mining system** that automatically finds powerful moments from long lectures and generates short clips suitable for social media.

This system must:

• use **free Google Colab GPU** for heavy AI processing
• reuse the **existing video pipeline**
• integrate with the **SQLite + RAG database**
• produce **timestamped clip candidates**
• optionally auto-cut clips using ffmpeg

The goal is to transform long lectures into **short viral clips** efficiently.

---

# System Architecture

The clip mining pipeline extends the existing system.

Pipeline flow:

video download (local)
↓
subtitle extraction (local)
↓
transcript chunking (local)
↓
upload chunks to Colab
↓
AI classification + scoring (Colab GPU)
↓
clip candidate detection (Colab GPU)
↓
return clip timestamps
↓
local ffmpeg clip extraction
↓
store metadata in database

Colab GPU performs all heavy AI analysis.

---

# Directory Structure

Add new directories:

project_root/

clip_pipeline/

```
detect_clips.py  
extract_clips.py  
```

colab_notebooks/

```
clip_mining_gpu.ipynb  
```

database/

```
clips.db  
```

docs/

```
clip_mining_pipeline.md  
```

---

# Transcript Chunk Format

Input format:

```json
{
"video_id": "lecture_001",
"timestamp_start": "12:30",
"timestamp_end": "12:38",
"text": "The Prophet said charity extinguishes sins like water extinguishes fire."
}
```

Chunk size recommendation:

6–10 subtitle lines.

Average chunk length:

5–15 seconds.

---

# Clip Detection Strategy

Clip candidates are detected using **three signals**.

Signal 1 — Topic classification
Signal 2 — Emotional impact scoring
Signal 3 — Keyword detection

Only segments passing thresholds become clip candidates.

---

# Topic Classification

Performed on Colab GPU using:

Qwen3.5-4B.

Possible topics:

charity
oppression
dua
mercy
death
tawakkul
sabr
other

Prompt example:

```
Classify the topic of this Islamic lecture segment.

Topics:
charity
oppression
dua
mercy
death
tawakkul
sabr
other

Text:
{chunk}

Return topic only.
```

---

# Emotional Impact Scoring

The model assigns a score from 1–10.

Prompt example:

```
Score the emotional impact of this lecture segment.

Scale:
1 = weak
10 = extremely powerful reminder

Text:
{chunk}

Return number only.
```

Segments scoring:

≥7 → strong candidate.

---

# Keyword Detection

Before LLM inference, run keyword detection locally.

Example keywords:

charity → zakat, sadaqah, donate
oppression → tyrant, injustice, oppressed
dua → supplication, ask Allah
mercy → rahmah, forgiveness

If keywords detected:

skip LLM classification.

This reduces GPU usage significantly.

---

# Clip Candidate Logic

Clip candidate rules:

topic ≠ other
AND
emotion_score ≥ 7

Then mark:

clip_candidate = true.

Example result:

```json
{
"video_id": "lecture_001",
"start": "12:25",
"end": "12:45",
"topic": "charity",
"emotion_score": 8,
"clip_candidate": true
}
```

---

# Segment Merging

Adjacent candidate chunks should merge.

Example:

chunk1: 12:10–12:18
chunk2: 12:18–12:25
chunk3: 12:25–12:35

Merged clip:

12:10–12:35.

Maximum clip duration:

60 seconds.

Minimum duration:

15 seconds.

---

# Colab GPU Processing

All LLM tasks must run on Colab.

Model:

Qwen3.5-4B.

Runtime setup:

enable GPU
install transformers
install bitsandbytes

Batch inference must be used.

Example batch size:

T4 GPU → 8–12 chunks.

---

# Batch Processing Example

Pseudocode:

```
for batch in transcript_chunks:

    prompts = build_prompts(batch)

    responses = model.generate(prompts)

    parse results
```

Never run sequential inference.

Batching maximizes GPU throughput.

---

# Clip Extraction

Once timestamps are detected, clips are extracted locally.

Tool:

ffmpeg.

Example:

```
ffmpeg -ss 12:10 -to 12:35 -i lecture.mp4 clip_01.mp4
```

Optional enhancements:

subtitle overlay
vertical crop for Shorts

---

# Database Schema

Create new table:

clips

Fields:

id
video_id
start_time
end_time
topic
emotion_score
file_path
created_at

Example row:

```
video_id: lecture_001
start_time: 12:10
end_time: 12:35
topic: charity
emotion_score: 8
file_path: clips/lecture001_clip01.mp4
```

---

# Integration with RAG

Clip candidates must also enter the RAG system.

Benefits:

users can search clips by topic
LLM can reference clip timestamps
automated clip discovery

Example query:

"What did the scholar say about charity?"

RAG returns:

lecture timestamp + clip.

---

# Automation with Google Drive

Colab should read transcript files from Drive.

Example path:

/content/drive/MyDrive/video_pipeline/chunks.json

Results written to:

clip_candidates.json.

Local pipeline downloads and processes results.

---

# Testing Strategy

Agentic code must implement the following tests.

---

Test 1 — Transcript Parsing

Input:

sample transcript with timestamps.

Expected output:

correct chunk segmentation.

---

Test 2 — Topic Classification

Use 10 known segments.

Example:

text about charity.

Expected result:

topic = charity.

Accuracy target:

≥80%.

---

Test 3 — Emotion Scoring

Use known emotional segments.

Expected:

score ≥7.

---

Test 4 — Clip Candidate Detection

Input:

mixed transcript chunks.

Expected:

only high-impact segments flagged.

---

Test 5 — Timestamp Merging

Input:

adjacent candidate chunks.

Expected:

single merged clip.

---

Test 6 — ffmpeg Extraction

Input:

sample lecture video.

Expected:

generated clip file.

Verify:

correct duration.

---

Test 7 — Colab GPU Processing

Upload:

200 transcript chunks.

Expected:

GPU inference completes successfully.

Processing target:

under 3 minutes.

---

# Performance Targets

Example dataset:

10 lectures
≈700 transcript chunks.

Processing time:

5–8 minutes on free Colab GPU.

Output:

20–80 clip candidates.

---

# Future Enhancements

Phase 2 improvements:

semantic embeddings for clip clustering
automatic title generation
vertical video formatting
auto subtitle styling
auto social media posting

---

# Completion Criteria

Pipeline considered complete when:

clip timestamps detected automatically
Colab GPU performs all AI processing
clips extracted successfully
metadata stored in database
RAG system can reference clips

This enables scalable **lecture → clip content mining** using only free compute resources.
