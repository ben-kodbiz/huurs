# Transcript Search Engine (yt-fts)

The system integrates yt-fts to create a searchable index of video transcripts.

Purpose:

Allow fast searching across lecture transcripts.

Example queries:

```
charity in islam
conditions of jihad
meaning of sabr
riba prohibition
```

Search results include:

video id
timestamp
transcript text

Example output:

```
Video: abc123
Timestamp: 00:12:14
Text: Interest (riba) is clearly prohibited in Islam...
```

This allows the system to:

Locate knowledge inside long lectures instantly.

The transcript index is stored in:

```
data/fts_index/
```

The index is automatically created during pipeline execution.

No manual steps are required.

---

# Testing Search (Optional)

If yt-fts CLI is installed, test search manually:

```
yt-fts search "charity" --index-dir data/fts_index
```

Expected result:

Matching transcript lines with timestamps.

---

End of yt-fts documentation
