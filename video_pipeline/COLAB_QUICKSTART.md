# 🚀 Quick Start: Google Colab GPU Processing

## Current Status

**Chunks to process:** 712
- Surah Al Mulk: 312 chunks
- Surah Ar-Rahman: 400 chunks

**Estimated Colab time:** ~15 minutes (FREE Tesla T4 GPU)

---

## Step 1: Export (Already Done ✅)

File ready: `/mnt/AI/dev/huurs/video_pipeline/chunks.json` (454 KB)

---

## Step 2: Open Google Colab

1. **Go to:** https://colab.research.google.com/

2. **Upload notebook:**
   - `File` → `Upload notebook`
   - Select: `video_pipeline/colab_notebook/colab_pipeline.ipynb`

3. **Enable GPU:**
   - `Runtime` → `Change runtime type` → `GPU` → `T4`
   - Click `Save`

---

## Step 3: Upload & Run

1. **Upload chunks.json:**
   - Click 📁 folder icon
   - Click ⬆️ upload
   - Select: `video_pipeline/chunks.json`

2. **Run all cells:**
   - Click `Runtime` → `Run all`
   - Wait ~15 minutes
   - Don't close browser!

3. **Download results:**
   - File downloads automatically: `processed_chunks.json`

---

## Step 4: Import Results

```bash
cd /mnt/AI/dev/huurs/video_pipeline
source ../.venv/bin/activate
python colab/import_results.py processed_chunks.json
```

---

## Step 5: Verify

```bash
python monitor_progress.py
```

Should show:
- Surah Al Mulk: 596/596 enriched ✅
- Surah Ar-Rahman: 438/438 enriched ✅

---

## Done! 🎉

Next: Generate embeddings and test RAG system.

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Export script | `colab/export_chunks.py` | Export pending chunks |
| Colab notebook | `colab_notebook/colab_pipeline.ipynb` | GPU processing |
| Import script | `colab/import_results.py` | Import results |
| Full guide | `colab/README.md` | Detailed instructions |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No GPU | Runtime → Change runtime type → GPU → T4 |
| Timeout | Notebook saves checkpoints, can resume |
| Download fails | Re-run last cell or download from Files panel |

---

**Need help?** Read full guide: `video_pipeline/colab/README.md`
