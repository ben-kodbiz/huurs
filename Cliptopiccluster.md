# topic_cluster_mining.md

Branch: `feature/topic-cluster-mining`

Purpose:
Extend the clip mining pipeline by automatically **discovering themes across many lectures** and grouping similar segments together.

This allows the system to:

• detect recurring Islamic topics
• group similar lecture moments from different scholars
• generate multiple clip ideas automatically
• improve RAG search relevance

All heavy processing must use **free Google Colab GPU** when possible.

---

# System Overview

Current pipeline:

video
↓
transcript
↓
chunk
↓
LLM classification
↓
clip candidates

New pipeline adds:

embedding generation
↓
semantic clustering
↓
topic cluster discovery
↓
clip set generation

---

# Why Topic Clustering Matters

Example:

The system processes 100 lectures.

It may find:

* 80 segments about charity
* 45 segments about oppression
* 30 segments about dua

Instead of isolated clips, the system now builds **topic collections**.

Example output:

Topic: Charity

clips:

lecture12 03:22
lecture18 11:40
lecture33 22:10
lecture45 05:05

These clusters allow automated content generation.

---

# Embedding Generation

Each transcript chunk must be converted into a vector.

Model used:

sentence-transformers/all-MiniLM-L6-v2

Reason:

• lightweight
• fast on Colab GPU
• widely used in semantic search

Process:

text → embedding vector.

Example vector length:

384 dimensions.

Example:

```json id="vector_example"
{
"chunk_id": 42,
"text": "Charity purifies wealth",
"embedding": [0.21, -0.44, 0.33 ...]
}
```

---

# Embedding Storage

Embeddings should be stored in SQLite.

Table: chunk_embeddings

Fields:

chunk_id
video_id
embedding_vector
topic
timestamp_start

Vectors can be stored as serialized arrays.

---

# Clustering Algorithm

The agent must implement clustering to group similar segments.

Recommended algorithms:

Primary:

HDBSCAN

Fallback:

KMeans

Reason:

HDBSCAN works well for unknown topic counts.

Workflow:

load embeddings
run clustering
assign cluster_id to each chunk.

Example:

```json id="cluster_example"
{
"chunk_id": 42,
"cluster_id": 7
}
```

---

# Cluster Interpretation

After clusters are created, assign a human-readable label.

Process:

Collect sample chunks from cluster
Send to LLM for labeling.

Prompt example:

```
These lecture segments belong to the same topic.

Segment 1:
{text}

Segment 2:
{text}

Segment 3:
{text}

What is the main Islamic topic?

Answer with short phrase.
```

Output example:

Topic label:

"Virtue of Charity".

---

# Cluster Clip Generation

Once clusters exist:

Select highest emotional score segments.

Example rule:

top 5 segments per cluster.

These become **cluster clips**.

Example:

Cluster: Charity

clips:

lecture03 03:12
lecture07 21:45
lecture12 12:33
lecture21 08:10
lecture30 17:44

---

# Clip Set Creation

Clusters can automatically generate content sets.

Example:

Set title:

"5 Powerful Reminders About Charity"

Clip order determined by:

emotion score.

---

# Colab GPU Processing

Embedding generation must run in Colab.

Workflow:

load transcript chunks
generate embeddings in batches
save vectors to JSON
download results locally.

Batch example:

32 chunks per batch.

This ensures efficient GPU usage.

---

# Integration with Existing Pipelines

This branch extends:

video classification pipeline
clip mining pipeline
RAG system.

New pipeline stage:

clip detection
↓
embedding generation
↓
cluster discovery
↓
topic clip sets.

---

# Testing Strategy

Agentic code must implement tests.

---

Test 1 — Embedding Generation

Input:

10 transcript segments.

Expected:

10 embedding vectors generated.

---

Test 2 — Clustering

Input:

segments about charity and oppression.

Expected:

two clusters formed.

---

Test 3 — Cluster Labeling

Input:

cluster with charity segments.

Expected:

label includes word "charity".

---

Test 4 — Clip Set Creation

Input:

cluster with multiple segments.

Expected:

top segments selected.

---

Test 5 — RAG Integration

Query:

"show lectures about charity"

Expected:

results include cluster clips.

---

# Performance Targets

Example dataset:

100 lectures
≈7000 transcript chunks.

Processing time on Colab:

embedding generation:

10–15 minutes.

Clustering:

<1 minute.

---

# Future Expansion Tasks

Agentic code must prepare architecture for the following future modules.

---

1. Automatic Clip Title Generation

Use LLM to generate titles for clips.

Example:

Input:

clip transcript.

Output:

"Charity Erases Sins – Powerful Reminder".

---

2. Subtitle Styling Engine

Automatically generate styled subtitles.

Example:

bold keywords
highlight Quran words.

---

3. Vertical Video Formatter

Convert clips to:

9:16 aspect ratio.

Use ffmpeg cropping.

---

4. Social Media Export

Automatically prepare clips for:

YouTube Shorts
TikTok
Instagram Reels.

---

5. Topic Series Generator

Automatically produce themed clip series.

Example:

"7 Lessons About Tawakkul".

---

# Success Criteria

The topic cluster mining system is complete when:

embeddings generated
clusters discovered automatically
clusters labeled with topics
clip sets generated
results stored in database
RAG search supports cluster results.

All heavy processing must remain compatible with **free Google Colab GPU environments**.
