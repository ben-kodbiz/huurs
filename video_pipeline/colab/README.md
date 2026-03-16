# 🚀 Google Colab GPU Processing Guide

## Overview

Use **FREE Google Colab Tesla T4 GPU** to process transcript chunks 10x faster than CPU.

**What Colab does:**
- ✅ Summarize each chunk (1-2 sentences)
- ✅ Classify into Islamic topics
- ✅ Generate confidence scores

**What you do locally:**
- ✅ Export chunks
- ✅ Upload to Colab
- ✅ Run notebook
- ✅ Download results
- ✅ Import to database

---

## Step-by-Step Guide

### Step 1: Export Chunks from Database

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Export all pending chunks
python colab/export_chunks.py

# OR export from specific video
python colab/export_chunks.py --video "Al Mulk"
```

**Output:** `chunks.json` (ready for upload)

---

### Step 2: Open Google Colab

1. **Go to:** https://colab.research.google.com/

2. **Upload the notebook:**
   - Click `File` → `Upload notebook`
   - Select: `colab_notebook/colab_pipeline.ipynb`
   - Click `Upload`

3. **Enable GPU (IMPORTANT!):**
   - Click `Runtime` → `Change runtime type`
   - Select `GPU` → `T4` (free tier)
   - Click `Save`

   > ⚠️ **Without GPU, processing will be very slow!**

---

### Step 3: Upload Chunks to Colab

1. **In Colab notebook, click the folder icon** 📁 on the left sidebar

2. **Click the upload icon** ⬆️

3. **Select `chunks.json`** from your computer

4. **Wait for upload to complete** (file will appear in `/content/`)

---

### Step 4: Run the Notebook

**Execute cells in order:**

1. **Cell 1:** Install dependencies (~30 seconds)
   - Click `▶️` button
   - Wait for "✓ Dependencies installed"

2. **Cell 2:** Verify GPU (~5 seconds)
   - Should show: `GPU Available: True`
   - Should show: `GPU Name: Tesla T4`

3. **Cell 3:** Load files (~10 seconds)
   - Shows number of chunks loaded
   - Confirms file upload successful

4. **Cell 4:** Load AI model (~60 seconds)
   - Downloads Qwen2.5-3B model
   - Loads onto GPU
   - Wait for "✓ Model loaded on GPU"

5. **Cell 5:** Process all chunks (⏰ **5-30 minutes**)
   - This is the main processing step
   - Shows progress: `Processing batch 1/10...`
   - Shows each chunk's topic
   - Saves checkpoint every 5 batches
   - **Don't close the browser!**

6. **Cell 6:** Save results (~10 seconds)
   - Saves to `processed_chunks.json`
   - Shows topic distribution

7. **Cell 7:** Download results
   - **File downloads automatically**
   - Save to same location as `chunks.json`

---

### Step 5: Import Results Back to Database

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate

# Import processed chunks
python colab/import_results.py processed_chunks.json
```

**Output:** Database updated with summaries and topics!

---

### Step 6: Verify & Generate Embeddings

```bash
# Check progress
python monitor_progress.py

# Generate embeddings (if needed)
python add_embeddings_per_video.py
```

---

## Processing Time Estimates

| Chunks | GPU Time | CPU Time (for comparison) |
|--------|----------|---------------------------|
| 100    | ~2 min   | ~20 min                   |
| 500    | ~10 min  | ~100 min                  |
| 899    | ~18 min  | ~180 min                  |
| 1000   | ~20 min  | ~200 min                  |

**Speedup:** ~10x faster with GPU!

---

## Troubleshooting

### ❌ "GPU not available"

**Solution:**
1. Click `Runtime` → `Change runtime type`
2. Select `GPU` → `T4`
3. Save and refresh page
4. Re-run cells from start

---

### ❌ "Runtime disconnected"

Colab free tier has timeouts (~90 minutes max session).

**Solution:**
- Notebook saves checkpoints every 5 batches
- If disconnected, re-run from last checkpoint
- Or re-upload `processed_chunks_checkpoint.json`

---

### ❌ "File not found: chunks.json"

**Solution:**
1. Click folder icon 📁 on left
2. Verify file is uploaded
3. File should be in `/content/` directory
4. Re-upload if needed

---

### ❌ "Out of memory"

Rare on T4, but can happen with large batches.

**Solution:**
- Edit Cell 5, change `batch_size=8` to `batch_size=4`
- Re-run notebook

---

### ❌ "Model download failed"

**Solution:**
- Colab needs internet access
- Re-run the model loading cell
- Model caches after first download

---

## Tips for Best Results

1. **Use GPU runtime** - 10x faster!
2. **Don't close browser** during processing
3. **Wait for download** after processing completes
4. **Keep checkpoints** - useful if disconnected
5. **Process in batches** - export 500 chunks at a time for large datasets

---

## Complete Workflow Example

```bash
# 1. Export chunks
python colab/export_chunks.py
# Output: chunks.json (899 chunks)

# 2. [In Colab]
# - Upload notebook + chunks.json
# - Run all cells
# - Download processed_chunks.json

# 3. Import results
python colab/import_results.py processed_chunks.json

# 4. Verify
python monitor_progress.py
# Should show: 899/899 enriched

# 5. Generate embeddings
python add_embeddings_per_video.py

# 6. Start RAG server
python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
```

---

## File Locations

```
video_pipeline/
├── colab/
│   ├── export_chunks.py          # Run locally to export
│   └── import_results.py         # Run locally to import
├── colab_notebook/
│   └── colab_pipeline.ipynb      # Upload to Colab
├── chunks.json                   # Exported (upload to Colab)
└── processed_chunks.json         # Downloaded from Colab
```

---

## Cost

**Google Colab Free Tier:**
- ✅ FREE Tesla T4 GPU
- ✅ Up to 12 hours per session
- ✅ 15 GB RAM
- ⚠️ Session timeout after ~90 minutes of inactivity

**For our use:**
- Processing 899 chunks: ~20 minutes
- Well within free tier limits!
- No credit card required

---

## Next Steps After Processing

1. **Verify enrichment:**
   ```bash
   python monitor_progress.py
   ```

2. **Generate embeddings** (optional but recommended):
   ```bash
   python add_embeddings_per_video.py
   ```

3. **Test RAG system:**
   ```bash
   python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000
   ```

4. **Ask questions:**
   - Open: http://localhost:8000
   - Try: "What is Surah Al Mulk about?"

---

## Support

If you encounter issues:
1. Check error message in Colab output
2. Verify GPU is enabled
3. Ensure chunks.json uploaded correctly
4. Try smaller batch sizes if memory issues

**Common fix:** Re-upload notebook and restart runtime.
