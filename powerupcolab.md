# colab_scaling_pipeline.md

Purpose:
Design a scalable **video AI enrichment pipeline using free Google Colab GPUs**.

The system must prioritize:

• free GPU usage
• minimal local compute
• efficient LLM inference
• automation for large video datasets

Target usage:

* 3–4 videos/day initially
* scalable to 10–20 videos/day

Worker model used in Colab:

Qwen3.5-4B

Thinker model used locally:

Qwen3.5-9B

---

# Core Philosophy

Heavy work should always run on Colab GPU.

Local machine responsibilities:

video download
subtitle extraction
chunk generation
database storage
RAG search

Colab responsibilities:

classification
summarization
embedding generation
metadata enrichment

This architecture keeps local electricity usage low.

---

# Pipeline Overview

Step 1
Download lecture videos locally.

Step 2
Extract subtitles using yt-dlp.

Step 3
Convert subtitles into transcript chunks.

Step 4
Export chunks to JSON.

Step 5
Upload JSON to Google Colab.

Step 6
Colab GPU processes chunks.

Step 7
Download enriched results.

Step 8
Import results into SQLite database.

Step 9
Use results in RAG search and clip generation.

---

# Colab Processing Strategy

Colab GPU is optimized for **batch inference**.

Important rule:

Never process chunks sequentially.

Bad design:

for each chunk → run model

Correct design:

batch of chunks → run model

Example batch sizes:

T4 GPU → 8–12 prompts
P100 GPU → 12–16 prompts

Batch inference increases throughput dramatically.

---

# Optimization Techniques

## 1 Batch Inference

Process multiple prompts simultaneously.

Example:

batch_prompts = [
"chunk1 text",
"chunk2 text",
"chunk3 text",
"chunk4 text"
]

model.generate(batch_prompts)

Batching improves GPU utilization.

---

## 2 Reduce Token Generation

Long outputs slow inference.

Use:

max_new_tokens = 20

Avoid:

max_new_tokens = 100+

Classification tasks need very few tokens.

---

## 3 Keyword Pre-Filter

Most transcript chunks do not contain useful content.

Use keyword detection before LLM.

Example keywords:

charity
zakat
sadaqah

oppression
tyrant
injustice

dua
supplication

mercy
rahmah

If keyword detected:

skip LLM classification.

Benefits:

reduces GPU workload by ~60%.

---

## 4 Selective Summarization

Summarize only important topics.

Important topics:

charity
oppression
dua
mercy
sabr
tawakkul

Skip summarization for generic content.

---

## 5 Small Prompts

Long prompts increase token processing time.

Example optimized prompt:

Topic list:

charity
oppression
dua
mercy
other

Text:

{chunk}

Answer with topic only.

---

# Clip Mining System

The pipeline must detect segments suitable for clips.

Each chunk receives a score:

score factors:

emotional impact
religious message strength
clarity of teaching

Example scoring:

1–10 scale.

Chunks with score ≥7 are marked as:

clip_candidate = true

These will later be used for:

short video generation.

---

# Semantic Embeddings

To enable advanced search, embeddings should be generated.

Use lightweight embedding model in Colab.

Example:

sentence-transformers/all-MiniLM-L6-v2

Steps:

generate embedding
store vector in database

Benefits:

semantic search
topic clustering
clip discovery

---

# Viral Segment Detection

Combine signals:

keyword match
LLM topic classification
high emotional score
short timestamp window

Chunks that match multiple signals become:

viral_segments.

These segments are prioritized for video clips.

---

# Colab Automation Strategy

Manual upload/download wastes time.

Instead use Google Drive sync.

Workflow:

local pipeline saves chunks.json

file automatically synced to Google Drive

Colab notebook reads file from Drive

Example:

/content/drive/MyDrive/video_pipeline/chunks.json

After processing:

results saved back to Drive.

Local pipeline then imports results.

---

# Multi-Video Batch Processing

Process many videos in one Colab session.

Example session:

10 lectures
≈2000 chunks

Colab processes everything in one job.

This maximizes GPU efficiency.

---

# Checkpoint Safety

Colab sessions sometimes reset.

Save checkpoints every:

20–40 chunks.

Checkpoint file:

processing_state.json

If notebook restarts:

resume from last checkpoint.

---

# Free Colab Limits

Free tier constraints:

session length ~12 hours
GPU availability varies
idle timeout possible

Recommended strategy:

run enrichment jobs immediately after loading GPU.

Avoid leaving session idle.

---

# Estimated Performance

Example dataset:

10 lectures
≈700 transcript chunks

Optimized Colab pipeline:

processing time ≈ 5–8 minutes.

Without optimization:

20–30 minutes.

---

# Future Scaling Strategy

Once the pipeline is stable:

Stage 1
10 videos/day

Stage 2
20 videos/day

Stage 3
automatic clip generation

Stage 4
automated faceless video creation

---

# Success Criteria

Pipeline is successful when:

Colab performs all LLM processing
local machine only manages data
GPU batching is implemented
clip candidate segments detected
results stored in SQLite database

The system must run entirely using free compute resources.
