# 🤗 Hugging Face Spaces - Clip Mining Setup Guide

## Quick Start (10 minutes)

### Step 1: Create Space (2 min)

1. **Go to:** https://huggingface.co/spaces
2. **Click:** "Create new Space"
3. **Fill in:**
   - **Space name:** `clip-mining-qwen35`
   - **License:** MIT
   - **Visibility:** Public (or Private if you have Pro)
4. **Click:** "Create Space"

---

### Step 2: Enable GPU (3 min)

1. **Go to:** Settings tab
2. **Scroll to:** "Hardware" section
3. **Select:** "A10G small" (free tier with 24GB VRAM)
4. **Click:** "Save"
5. **Wait:** ~1-2 minutes for GPU to provision

**Note:** A10G is **faster than T4** and similar to P100!

---

### Step 3: Add HF Token (2 min)

1. **Go to:** Settings tab
2. **Scroll to:** "Repository secrets"
3. **Click:** "New secret"
4. **Enter:**
   - **Name:** `HF_TOKEN`
   - **Value:** `<YOUR_HF_TOKEN_HERE>` (Get from https://huggingface.co/settings/tokens)
5. **Click:** "Save"

> ⚠️ **Security Warning:** Never commit your actual HF token to version control. Always use environment variables or secret management systems.

---

### Step 4: Upload Files (3 min)

1. **Go to:** Files tab
2. **Click:** "Add file" → "Upload file"
3. **Upload:**
   - `clip_mining_hf_spaces.ipynb`
   - `chunks.json`
4. **Click:** "Commit changes to main"

---

### Step 5: Run Notebook

1. **Go to:** "Files" tab
2. **Click:** `clip_mining_hf_spaces.ipynb`
3. **Click:** "Run" button (top-right)
4. **Wait:** ~15 minutes for processing
5. **Download:** Results from Files tab

---

## File Structure

After upload, your Space should have:

```
clip-mining-qwen35/
├── clip_mining_hf_spaces.ipynb    # Notebook
├── chunks.json                     # Your transcripts
├── clip_candidates_qwen35_4b_hf_*.json  # Output (after run)
└── clip_candidates_qwen35_4b_hf_*.csv   # Output (after run)
```

---

## Download Results

### Method 1: Direct Download (Easy)

1. **Go to:** Files tab
2. **Find:** `clip_candidates_qwen35_4b_hf_*.json`
3. **Click:** Download icon (⬇️)
4. **Save:** To your computer

### Method 2: Git Clone (Advanced)

```bash
# Install git-lfs
git lfs install

# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/clip-mining-qwen35
cd clip-mining-qwen35

# Download results
git pull
ls -lh clip_candidates_*.json
```

---

## Performance

**Hugging Face Spaces A10G:**

| Metric | Value |
|--------|-------|
| **GPU** | NVIDIA A10G |
| **VRAM** | 24 GB |
| **Speed** | ~8-10 min (712 chunks) |
| **Quality** | Same as Colab/Kaggle |

**Comparison:**

| Platform | GPU | Time (712 chunks) |
|----------|-----|-------------------|
| Colab | T4 | ~12 min |
| Kaggle | P100 | ~10 min |
| **HF Spaces** | **A10G** | **~8 min** ✅ |
| Gradient | P40 | ~15 min |

---

## Troubleshooting

### Issue: "No GPU option"

**Solution:**
- Free tier A10G may be unavailable
- Try upgrading to Pro ($9/month)
- Or use Gradient.run instead

### Issue: "HF_TOKEN not found"

**Solution:**
1. Check secret name is exactly `HF_TOKEN` (case-sensitive)
2. Re-add the secret in Settings
3. Restart the Space (Settings → Factory reboot)

### Issue: "Out of memory"

**Solution:**
```python
# In model loading, use 8-bit quantization:
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    load_in_8bit=True,  # Add this
    device_map="auto"
)
```

### Issue: "Space is private"

**Solution:**
- Free tier only supports public Spaces
- Make Space public in Settings
- Or upgrade to Pro for private Spaces

---

## Tips

### 1. Keep Space Running

By default, Spaces go to sleep after 48 hours of inactivity.

**To keep it running:**
- Run the notebook periodically
- Or upgrade to Pro for persistent Spaces

### 2. Use Git for Large Files

For `chunks.json` > 10MB:

```bash
# Locally
git clone https://huggingface.co/spaces/YOUR_USERNAME/clip-mining-qwen35
cd clip-mining-qwen35
git lfs install
cp /path/to/chunks.json .
git add chunks.json
git commit -m "Add chunks"
git push
```

### 3. Delete Old Results

To save space:

```bash
# In Space terminal or via git
rm clip_candidates_*.json
rm clip_candidates_*.csv
git add -A
git commit -m "Clean old results"
git push
```

---

## Cost

**Free Tier:**
- ✅ A10G GPU (24GB)
- ✅ Public Spaces
- ✅ Limited compute hours per month
- ❌ No private Spaces

**Pro Tier ($9/month):**
- ✅ Everything in Free
- ✅ Private Spaces
- ✅ More compute hours
- ✅ Priority GPU access

---

## Alternative: Hugging Face Notebooks

If Spaces doesn't work, try **Hugging Face Notebooks**:

1. Go to: https://huggingface.co/notebooks
2. Create new notebook
3. Select GPU runtime
4. Same code works!

---

## Summary

**Hugging Face Spaces is great for:**

✅ Quick tests (8 min processing)  
✅ No phone verification  
✅ A10G faster than T4  
✅ Easy file management  
✅ Git integration  

**Not ideal for:**

❌ Private processing (need Pro)  
❌ Very large files (>10GB)  
❌ Long-running jobs (48h timeout)  

**Best use:** Quick clip mining when Colab/Kaggle at limits! 🚀

---

## Quick Commands

### Upload via Git
```bash
git clone https://huggingface.co/spaces/YOU/SPACE
cd SPACE
git lfs install
cp chunks.json .
git add .
git commit -m "Upload files"
git push
```

### Download Results
```bash
git pull
ls -lh clip_candidates_*.json
```

### Check GPU
```python
import torch
print(torch.cuda.get_device_name(0))
# Should show: NVIDIA A10G
```

---

**Ready to mine clips on Hugging Face Spaces!** 🎉
