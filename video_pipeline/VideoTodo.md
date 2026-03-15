# Video Pipeline Task Plan (VideoTodo.md)

## Purpose

This document defines the **YouTube video ingestion pipeline tasks**.

The pipeline converts YouTube lectures into structured searchable knowledge.

This pipeline is **separate from the poster OCR pipeline**, but both use the same LLM backend.

LLM backend:
Qwen 3.5 9B via LMStudio API

Core tools used:

yt-dlp → retrieve metadata and subtitles
yt-fts → build searchable transcript index
Qwen → summarize knowledge segments

---

# Pipeline Architecture

```
YouTube URL
     ↓
metadata retrieval
     ↓
subtitle detection
     ↓
subtitle download
     ↓
subtitle validation
     ↓
yt-fts indexing
     ↓
subtitle parsing
     ↓
transcript chunking
     ↓
LLM summarization
     ↓
database storage
```

---

# Task Status Markers

Agent tasks must use:

```
[ ] pending
[x] completed
[!] error
```

---

# Stage 1 — Video Metadata

Retrieve video metadata using yt-dlp.

Required metadata:

```
video_id
title
channel
url
```

Checkpoint:

```
[ ] metadata retrieved
```

Failure condition:

```
[!] metadata retrieval failed
```

Pipeline must stop if metadata fails.

---

# Stage 2 — Subtitle Detection

Check if subtitles exist.

Command used internally:

```
yt-dlp --list-subs VIDEO_URL
```

Agent must check for:

English subtitles

If English subtitles do not exist:

Attempt auto subtitles.

---

# Stage 3 — Subtitle Download

Priority order:

1. human English subtitles
2. auto English subtitles

Download command:

```
yt-dlp --write-subs --sub-lang en --skip-download
```

or

```
yt-dlp --write-auto-subs --sub-lang en --skip-download
```

Checkpoint:

```
[ ] subtitles downloaded
```

---

# Stage 4 — Subtitle Validation

Verify:

subtitle file exists
subtitle file is not empty

Example expected file:

```
data/subtitles/VIDEO_ID.en.vtt
```

Failure condition:

```
[!] subtitles unavailable
[!] pipeline halted
```

Agent must stop execution.

---

# Stage 5 — yt-fts Index Creation

Create searchable transcript index using yt-fts.

Command:

```
yt-fts index subtitle_file --index-dir data/fts_index --video-id VIDEO_ID
```

Checkpoint:

```
[ ] transcript indexed
```

Failure condition:

```
[!] yt-fts indexing failed
```

Pipeline stops if indexing fails.

---

# Stage 6 — Subtitle Parsing

Parse subtitles into structured transcript.

Output example:

```
timestamp: 00:02:15
text: Allah loves those who are patient
```

Checkpoint:

```
[ ] subtitles parsed
```

---

# Stage 7 — Transcript Chunking

Chunk transcripts for LLM processing.

Recommended chunk size:

```
8 subtitle lines
```

Checkpoint:

```
[ ] transcript chunked
```

---

# Stage 8 — LLM Knowledge Extraction

Send transcript chunks to Qwen.

Goal:

Extract key Islamic insights.

Expected output structure:

```
topic
summary
keywords
timestamp
```

Checkpoint:

```
[ ] transcript summarized
```

---

# Stage 9 — Database Storage

Store processed knowledge.

Database tables:

```
videos
transcripts
```

Stored transcript fields:

```
video_id
timestamp
text
summary
```

Checkpoint:

```
[ ] knowledge stored
```

---

# Error Handling

Pipeline must halt if:

```
metadata retrieval fails
subtitles unavailable
subtitle download fails
yt-fts indexing fails
```

Error format:

```
{
 "status": "failed",
 "stage": "subtitle detection",
 "reason": "subtitles unavailable"
}
```

---

# Future Improvements

Planned upgrades:

Automatic channel ingestion

Continuous monitoring of lecture channels

Semantic search using yt-fts

Automatic clip generation

Multi-language transcript translation

Knowledge graph linking Quran, Hadith, and lectures

---

# Completion Condition

Pipeline succeeds when:

```
metadata stored
subtitles processed
transcript indexed
knowledge stored
```

Final log:

```
[✓] video pipeline completed
```

---

End of VideoTodo.md
