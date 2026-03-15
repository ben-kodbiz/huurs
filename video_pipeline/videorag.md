# Video RAG System Specification

File: videorag.md

Purpose:
Implement a Retrieval Augmented Generation (RAG) system that allows users to ask questions about lecture videos and receive answers generated from transcript content.

This system integrates with the existing video pipeline:

video ingestion
subtitle extraction
transcript chunking
SQLite storage
FTS5 search index

The system retrieves transcript segments and sends them to the LLM to generate answers.

---

# System Architecture

User question
↓
Search engine (SQLite FTS)
↓
Retrieve relevant transcript chunks
↓
Context builder
↓
LLM reasoning
↓
Answer generation

The system does not summarize transcripts beforehand.

LLM is used only when a user asks a question.

---

# Directory Structure

Create the following structure:

project_root/

video_pipeline/

rag/

```
rag_engine.py

retriever.py

prompt_builder.py

llm_client.py

rag_api.py
```

ui/

```
index.html

app.js
```

database/

```
videos.db
```

docs/

```
videorag.md
```

---

# Database Requirements

Existing table:

transcripts

fields:

id INTEGER PRIMARY KEY
video_id TEXT
timestamp TEXT
text TEXT

FTS table:

transcript_fts

fields:

text

---

# Retriever Module

File:

rag/retriever.py

Purpose:
Search transcript chunks relevant to a user question.

Function:

search_transcripts(query, limit)

Steps:

1 connect to SQLite database

2 run FTS query

3 return best transcript chunks

Example SQL:

SELECT
transcripts.video_id,
transcripts.timestamp,
transcripts.text
FROM transcript_fts
JOIN transcripts
ON transcript_fts.rowid = transcripts.id
WHERE transcript_fts MATCH ?
LIMIT 10;

Return list of transcript segments.

---

# Context Builder

File:

rag/prompt_builder.py

Purpose:
Build context for the LLM.

Function:

build_context(chunks)

Steps:

1 combine transcript chunks
2 attach timestamps
3 produce structured context block

Example context:

Video: lecture1
Timestamp: 03:12

Transcript:
Allah loves those who give charity.

Video: lecture2
Timestamp: 08:44

Transcript:
Charity extinguishes sins.

Return formatted context string.

---

# LLM Client

File:

rag/llm_client.py

Purpose:
Send question + context to the LLM.

Model:

Qwen3.5-9B running in LM Studio.

Example prompt template:

You are an Islamic knowledge assistant.

Answer the user's question using only the lecture excerpts provided.

If the answer is not in the excerpts say:

"The lectures did not discuss this topic."

Question:

{user_question}

Lecture excerpts:

{context}

Answer clearly and cite timestamps.

---

# RAG Engine

File:

rag/rag_engine.py

Purpose:
Combine retrieval and LLM reasoning.

Function:

answer_question(question)

Steps:

1 retrieve transcript chunks
2 build context
3 call LLM
4 return answer

Pseudo workflow:

chunks = retriever.search_transcripts(question)

context = build_context(chunks)

answer = llm.ask(prompt)

return answer

---

# API Layer

File:

rag/rag_api.py

Purpose:
Expose the RAG system through a web API.

Framework:

FastAPI

Endpoints:

POST /ask

Request:

{
"question": "What does Islam say about oppression?"
}

Response:

{
"answer": "...",
"sources": [
{
"video_id": "abc123",
"timestamp": "09:18"
}
]
}

Server start command:

python rag_api.py

Default port:

8000

---

# Web UI

Create a minimal chat interface.

Directory:

ui/

Files:

index.html
app.js

---

# index.html

Simple layout:

Title: Video Knowledge Search

Components:

chat window
input box
send button

Structure:

header

chat messages area

input box

send button

---

# app.js

Functionality:

capture user question
send request to /ask API
display answer

Example flow:

User types question

JavaScript sends POST request to API

Fetch response

Display answer in chat window

---

# Example User Workflow

Step 1

User opens:

http://localhost:8000/ui/index.html

Step 2

User asks:

"What does Islam say about oppression?"

Step 3

System retrieves transcript chunks.

Example:

Video: justice_lecture
Timestamp: 09:18

Transcript:

Beware the supplication of the oppressed.

Step 4

Chunks sent to LLM.

Step 5

LLM produces answer.

Example output:

Islam strongly condemns oppression.

The Prophet warned that the supplication of the oppressed has no barrier between it and Allah.

Referenced lecture timestamp: 09:18.

---

# Error Handling

Possible errors:

No search results

LLM server unavailable

Database unavailable

Fallback behaviors:

If no chunks found:

Return message:

"No lecture content matched your question."

If LLM fails:

Return retrieved transcript segments only.

---

# Performance Notes

Typical latency:

FTS search

5–20 milliseconds

LLM generation

3–6 seconds

System remains responsive even with thousands of transcript chunks.

---

# Future Improvements

vector semantic search

automatic topic classification

highlight timestamp playback

video clip extraction

multi-language support

Arabic verse detection

---

# Completion Criteria

The RAG system is complete when:

SQLite search works

API endpoint responds

Web interface loads

Questions return lecture-based answers

Final system log:

[✓] Video RAG system ready
