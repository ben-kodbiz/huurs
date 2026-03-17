# 🚀 Kaggle GPU Setup Guide - Qwen3.5-4B Clip Mining

## Why Kaggle?

When you hit **Colab's free limit**, Kaggle is the best alternative:

| Feature | Colab Free | Kaggle Free |
|---------|------------|-------------|
| **GPU** | T4 (16GB) | P100/V100 (16GB) |
| **Weekly Limit** | ~10-12 hours | **30 hours** |
| **Session Length** | 12 hours | 12 hours |
| **RAM** | 12 GB | 16 GB |
| **Internet** | ✓ | ✓ |

---

## Step-by-Step Setup

### Step 1: Create Kaggle Account

1. Visit: https://www.kaggle.com
2. Click **"Sign Up"**
3. Use Google account (recommended) or email

---

### Step 2: Enable GPU

1. **Create new notebook:**
   - Click **"Code"** → **"New Notebook"**

2. **Enable GPU:**
   - Click **"More"** (⋮) in top-right
   - Select **"Accelerator"**
   - Choose **"P100 GPU"** or **"GPU T4 x2"**

---

### Step 3: Add Hugging Face Token

1. **Get HF Token:**
   - Visit: https://huggingface.co/settings/tokens
   - Create new token (Read access)
   - Copy token (`hf_xxxxx...`)

2. **Add to Kaggle:**
   - In notebook, click **"Add secret"** (left panel)
   - Name: `HF_TOKEN`
   - Value: `<YOUR_HF_TOKEN_HERE>` (Get from https://huggingface.co/settings/tokens)
   - Click **"Save"**

> ⚠️ **Security Warning:** Never commit your actual HF token to version control. Always use environment variables or secret management systems.

---

### Step 4: Upload chunks.json

**Method 1: Create Dataset (Recommended)**

1. Go to **Datasets** → **New Dataset**
2. Upload `chunks.json`
3. Set visibility: **Public** or **Private**
4. Click **"Create"**

5. In notebook:
   - Click **"Add data"** (right panel)
   - Select your dataset
   - Click **"Add"**

**Method 2: Direct Upload**

1. In notebook, click **"Upload"** (left panel)
2. Select `chunks.json`
3. Wait for upload to complete

---

### Step 5: Upload Notebook

1. **Upload notebook:**
   - Click **"Upload"** (top-right)
   - Select: `clip_pipeline/clip_mining_kaggle_qwen35_4b.ipynb`

2. **Or copy-paste:**
   - Create new notebook
   - Copy all cells from the notebook

---

### Step 6: Run Notebook

1. **Click "Run All"** (top menu)

2. **Wait for processing:**
   - Step 1: Install dependencies (~2 min)
   - Step 2: HF auth (~10 sec)
   - Step 3: GPU check (~5 sec)
   - Step 4: Load model (~3 min)
   - Step 5-7: Process chunks (~10-15 min for 700 chunks)

3. **Download results:**
   - Files appear in `/kaggle/working/`
   - Click file icons (left panel) to download
   - Or use download links in output

---

## File Locations

### Input
```
/kaggle/input/your-dataset/chunks.json
```

### Output
```
/kaggle/working/clip_candidates_qwen35_4b_TIMESTAMP.json
/kaggle/working/clip_candidates_qwen35_4b_TIMESTAMP.csv
```

---

## Expected Output

```
============================================================
PROCESSING COMPLETE
============================================================
Total: 712, Skipped: 443
Clip candidates (≥7): 87
High priority (≥8): 45
============================================================

✓ Merged 87 candidates into 14 clips

Top clips:
   1. [Death      ] 46:10-46:26 | Score: 9 | 16s
   2. [Death      ] 65:16-65:35 | Score: 9 | 19s
   3. [Mercy      ] 66:21-66:39 | Score: 9 | 18s
   ...

✓ Saved JSON: /kaggle/working/clip_candidates_qwen35_4b_20260316_123456.json
  Size: 45.3 KB
✓ Saved CSV: /kaggle/working/clip_candidates_qwen35_4b_20260316_123456.csv

============================================================
DOWNLOAD FILES
============================================================
Click on the file icons (left panel) to download!
```

---

## Download Results

### Method 1: Click to Download

1. Look at **left panel** → **Output** section
2. Find files:
   - `clip_candidates_qwen35_4b_*.json`
   - `clip_candidates_qwen35_4b_*.csv`
3. Click **⬇️** icon next to each file

### Method 2: Download All

```python
# Run this cell to download all results
from IPython.display import FileLink

FileLink('/kaggle/working/clip_candidates_qwen35_4b_TIMESTAMP.json')
FileLink('/kaggle/working/clip_candidates_qwen35_4b_TIMESTAMP.csv')
```

---

## Import Results Locally

After downloading:

```bash
cd /mnt/AI/dev/huurs/video_pipeline

# Import results to database
python colab/import_results.py clip_candidates_qwen35_4b_TIMESTAMP.json

# Or use clip pipeline
python -m clip_pipeline.run_pipeline \
    --transcript ../clip_candidates_qwen35_4b_TIMESTAMP.json \
    --video-id your_video_id \
    --title "Your Video Title"
```

---

## Troubleshooting

### Issue: "HF_TOKEN not found"

**Solution:**
1. Check secret name is exactly `HF_TOKEN` (case-sensitive)
2. Re-add the secret: Add secret → HF_TOKEN → paste token
3. Restart notebook session

### Issue: "GPU not available"

**Solution:**
1. Check accelerator: More (⋮) → Accelerator → GPU
2. Wait for GPU to initialize (~30 sec)
3. Check weekly quota: Profile → Settings → GPU usage

### Issue: "Out of memory"

**Solution:**
```python
# In model loading, reduce precision:
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    load_in_8bit=True,  # Add this for 8-bit quantization
    device_map="auto"
)
```

### Issue: "Model loading fails"

**Solution:**
1. Check HF token is valid
2. Accept model license: https://huggingface.co/Qwen/Qwen3.5-4B
3. Check internet connection in notebook (Settings → Internet → On)

---

## Kaggle vs Colab Comparison

| Aspect | Colab | Kaggle |
|--------|-------|--------|
| **Setup Time** | 2 min | 5 min |
| **GPU Speed** | Good (T4) | Better (P100) |
| **Weekly Limit** | ~10 hrs | **30 hrs** |
| **File Upload** | Easy | Requires dataset |
| **Download** | Automatic | Manual click |
| **Internet** | Always on | Need to enable |
| **Secrets** | Settings → Secrets | Add secret panel |

---

## Tips for Maximum Efficiency

### 1. Batch Processing
Process multiple videos in one session:
```python
# Upload multiple chunks.json files
# Process all in one notebook run
```

### 2. Save Checkpoints
```python
# Save progress every 100 chunks
if (i + 1) % 100 == 0:
    with open(f'/kaggle/working/checkpoint_{i}.json', 'w') as f:
        json.dump(processed_chunks[:i], f)
```

### 3. Use Datasets
Create a dataset with all your chunks:
```
My Islamic Lectures Dataset/
├── video1_chunks.json
├── video2_chunks.json
└── video3_chunks.json
```

---

## Weekly Limits

**Kaggle GPU Quota:**
- **30 hours/week** of GPU time
- Resets every **Monday 00:00 UTC**
- Check usage: Profile → Settings → GPU usage

**Maximize your quota:**
- Process in batches (don't run all at once)
- Use efficient models (Qwen3.5-4B is perfect)
- Save results frequently

---

## Quick Reference

```bash
# Upload to Kaggle
1. Create dataset with chunks.json
2. Add dataset to notebook
3. Run notebook
4. Download results

# Import locally
python colab/import_results.py clip_candidates_*.json
```

---

## Summary

✅ **30 hours/week** free GPU (vs Colab's ~10 hrs)  
✅ **P100/V100** GPUs (faster than T4)  
✅ **Same Qwen3.5-4B** support  
✅ **Easy setup** with HF authentication  
✅ **Direct download** of results  

Perfect backup when you hit Colab's limit! 🚀
