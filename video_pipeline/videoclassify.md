# Video Classification Specification

File: videoclassification.md

## Purpose

This document defines how the video pipeline performs **topic classification of transcript segments** using a local LLM.

The goal is to convert lecture transcripts into structured knowledge tags such as:

* charity
* dua
* patience
* oppression
* repentance
* anxiety

These tags enable:

search
topic exploration
knowledge grouping
content generation

The classification system works together with:

yt-dlp (subtitle retrieval)
yt-fts (transcript search index)
Qwen3.5-9B (LLM reasoning)

---

# Pipeline Context

Existing pipeline:

YouTube video
↓
subtitle download
↓
subtitle validation
↓
yt-fts indexing
↓
transcript parsing
↓
transcript chunking
↓
LLM summarization
↓
database storage

New pipeline with classification:

YouTube video
↓
subtitle download
↓
subtitle validation
↓
yt-fts indexing
↓
transcript parsing
↓
transcript chunking
↓
LLM classification
↓
LLM summarization
↓
database storage

---

# Classification Unit

Classification operates on **transcript chunks**.

Definition:

A chunk is a group of subtitle lines.

Recommended chunk size:

8 subtitle lines

Example chunk:

timestamp: 00:04:12

Text:

Allah loves those who give charity.
Even small charity protects a believer from punishment.
The Prophet encouraged giving daily.

---

# Classification Goals

For each chunk the system must determine:

primary topic
secondary topics
confidence score

Example output:

{
"primary_topic": "charity",
"secondary_topics": ["sadaqah","good deeds"],
"confidence": 0.92
}

---

# Topic Taxonomy

Initial topic categories:

faith
tawhid
dua
charity
patience
repentance
anxiety
oppression
marriage
family
akhlaq
death
jannah
jahannam
quran_reflection
hadith_explanation
knowledge
dawah

Topics may expand later.

Agent must classify **only within the taxonomy list**.

If no category fits:

topic = "general"

---

# LLM Prompt Design

The system sends transcript chunks to Qwen.

Prompt template:

SYSTEM:

You classify Islamic lecture text into topics.

Use only the provided taxonomy.

Return JSON output.

USER:

Transcript:

{chunk_text}

Available topics:

faith
tawhid
dua
charity
patience
repentance
anxiety
oppression
marriage
family
akhlaq
death
jannah
jahannam
quran_reflection
hadith_explanation
knowledge
dawah

Output format:

{
"primary_topic":"",
"secondary_topics":[],
"confidence":0.0
}

---

# Classification Workflow

Step 1 — Receive transcript chunk

Step 2 — Send chunk text to Qwen

Step 3 — Parse JSON response

Step 4 — Validate response structure

Step 5 — Store classification

---

# Database Schema Changes

Existing table: transcripts

Add columns:

primary_topic TEXT
secondary_topics TEXT
confidence REAL

Example stored record:

video_id: abcd123
timestamp: 00:04:12
text: Allah loves those who give charity
summary: Charity purifies wealth
primary_topic: charity
secondary_topics: sadaqah,good deeds
confidence: 0.91

---

# Classification Failure Handling

Possible failures:

LLM response not JSON
LLM timeout
invalid topic returned

Recovery procedure:

Retry classification once.

If failure persists:

primary_topic = "general"

confidence = 0.0

Agent logs:

[!] classification failed

---

# Performance Optimization

To reduce LLM usage:

Perform keyword prefilter.

Example keywords:

charity
sadaqah
dua
patience
oppression
fear
hope
repent

If chunk contains none of the keywords:

classification optional.

Agent may skip classification.

---

# Search Integration

Classification enhances search results.

Example query:

topic = charity

System retrieves:

all transcript segments where primary_topic = charity

User sees:

video title
timestamp
summary

---

# Future Extensions

Planned upgrades:

multi-label classification
topic hierarchy
semantic search integration
knowledge graph linking
automatic clip generation

Example clip generation:

topic search = charity

system extracts matching timestamps

generates short clips

---

# Completion Criteria

Classification considered successful when:

LLM classification executed
JSON output parsed
topics stored in database

Final pipeline log:

[✓] classification completed
