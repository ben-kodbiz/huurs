# Video Search System Specification

File: videosearch.md

## Purpose

This document defines the search system for lecture transcripts processed by the video pipeline.

The search system allows users to retrieve knowledge from lecture transcripts using:

keyword search
topic filtering
semantic similarity search

The system integrates with the existing video pipeline components:

subtitle ingestion
transcript chunking
LLM summarization
LLM classification

Search operates on transcript chunks stored in the SQLite database.

---

# Search Architecture Overview

The system supports two search engines.

Primary search:

SQLite FTS5 keyword search

Optional advanced search:

vector semantic search

Both systems may run simultaneously.

Pipeline architecture:

video ingestion
↓
subtitle parsing
↓
transcript chunking
↓
LLM classification
↓
LLM summarization
↓
database storage
↓
search indexing

---

# Database Schema

Existing table: transcripts

Required fields:

id INTEGER PRIMARY KEY
video_id TEXT
timestamp TEXT
text TEXT
summary TEXT
primary_topic TEXT
secondary_topics TEXT
confidence REAL

---

# FTS5 Search Index

Create a full-text search virtual table.

Schema:

CREATE VIRTUAL TABLE transcript_fts USING fts5(
text,
summary,
primary_topic,
content='transcripts',
content_rowid='id'
);

Index population command:

INSERT INTO transcript_fts(rowid,text,summary,primary_topic)
SELECT id,text,summary,primary_topic
FROM transcripts;

This creates a searchable index for transcript segments.

---

# Keyword Search Operation

User query example:

charity

Search command:

SELECT
transcripts.video_id,
transcripts.timestamp,
transcripts.text,
transcripts.summary
FROM transcript_fts
JOIN transcripts
ON transcript_fts.rowid = transcripts.id
WHERE transcript_fts MATCH 'charity'
LIMIT 20;

Result:

video id
timestamp
transcript segment
summary

---

# Topic Filter Search

Users may filter results by topic classification.

Example query:

topic = charity

SQL query:

SELECT
video_id,
timestamp,
summary
FROM transcripts
WHERE primary_topic = 'charity'
LIMIT 20;

This enables topic browsing without keyword search.

---

# Hybrid Search

Combine keyword search with topic filter.

Example:

keyword = charity
topic = dua

SQL query:

SELECT
transcripts.video_id,
transcripts.timestamp,
transcripts.summary
FROM transcript_fts
JOIN transcripts
ON transcript_fts.rowid = transcripts.id
WHERE transcript_fts MATCH 'charity'
AND transcripts.primary_topic = 'dua';

---

# Semantic Vector Search (Optional)

Vector search enables meaning-based search.

Example:

User query:

How can sins be forgiven?

Transcript may contain:

Charity extinguishes sins like water extinguishes fire.

Vector search will match these even without shared keywords.

---

# Embedding Model

Recommended local embedding models:

BAAI bge-small-en-v1.5
sentence-transformers all-MiniLM-L6-v2

Embeddings are generated for each transcript chunk.

Vector generation pipeline:

chunk text
↓
embedding model
↓
store vector

---

# Vector Database Options

Supported vector databases:

FAISS
Chroma
Qdrant

For lightweight local deployments FAISS is recommended.

---

# Embedding Storage Schema

Example table:

transcript_vectors

fields:

chunk_id INTEGER
embedding BLOB

chunk_id references transcripts.id

---

# Vector Search Workflow

User query:

oppression

Search pipeline:

query text
↓
generate embedding
↓
vector similarity search
↓
retrieve top N transcript chunks
↓
return results

Similarity metric:

cosine similarity

Typical top results:

5 to 10 transcript segments.

---

# Hybrid Retrieval Pipeline

Best search performance uses hybrid retrieval.

Example pipeline:

user query
↓
FTS keyword search
↓
vector similarity search
↓
merge results
↓
rank results
↓
return final list

Ranking factors:

keyword match strength
vector similarity score
classification confidence

---

# LLM Assisted Answer Generation

After retrieving transcript segments, the system may call the LLM.

LLM: Qwen3.5-9B

Example workflow:

user query
↓
retrieve transcript segments
↓
send segments to LLM
↓
generate explanation

Example prompt:

User question:

What does Islam say about oppression?

Context:

{retrieved transcript chunks}

Instruction:

Answer using the lecture content only.

---

# Example Search Response

User query:

oppression

Result:

Video: Justice in Islam
Timestamp: 09:18

Transcript:

Beware the supplication of the oppressed, for there is no barrier between it and Allah.

Summary:

Islam strongly condemns oppression and warns of divine justice.

Topic:

oppression

---

# Performance Considerations

FTS search latency:

less than 20 milliseconds for tens of thousands of chunks.

Vector search latency:

typically 5–30 milliseconds depending on vector database.

---

# Error Handling

Possible failures:

FTS index missing
vector database unavailable
embedding model not loaded

Fallback procedure:

If vector search fails, use FTS search only.

System must log:

[!] vector search unavailable

---

# Completion Criteria

Search system considered operational when:

FTS index built
transcripts searchable
topic filter operational
optional vector search functional

Final log entry:

[✓] video search system ready
