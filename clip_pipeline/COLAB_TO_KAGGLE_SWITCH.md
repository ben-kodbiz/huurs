# 🔄 Colab → Kaggle Switch - Quick Reference

## When Colab Limit Reached

**Signs you hit Colab limit:**
- "No backend available"
- "Runtime disconnected"
- Can't enable GPU
- Quota exceeded message

**Solution:** Switch to Kaggle! ✅

---

## Quick Setup (5 minutes)

### 1. Create Kaggle Account
```
https://www.kaggle.com → Sign Up
```

### 2. Add HF Token
```
Notebook → Add secret → HF_TOKEN → hf_VqDjkCh...myCSb
```

### 3. Upload Data
```
Datasets → New Dataset → Upload chunks.json → Create
```

### 4. Enable GPU
```
Notebook → More (⋮) → Accelerator → P100 GPU
```

### 5. Run Notebook
```
Upload: clip_pipeline/clip_mining_kaggle_qwen35_4b.ipynb
Click: Run All
```

---

## File Comparison

| Task | Colab | Kaggle |
|------|-------|--------|
| **Upload** | Drag-drop | Create dataset |
| **Secrets** | Settings → Secrets | Add secret panel |
| **GPU** | Runtime → GPU | More → Accelerator |
| **Download** | Auto | Click file icons |
| **Limit** | ~10 hrs/week | **30 hrs/week** ✅ |

---

## Notebook Files

| File | Use |
|------|-----|
| `clip_mining_qwen35_4b.ipynb` | **Colab** (Google) |
| `clip_mining_kaggle_qwen35_4b.ipynb` | **Kaggle** (Alternative) |

---

## Key Differences

### Colab
```python
# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Get secrets
from google.colab import userdata
userdata.get('HF_TOKEN')
```

### Kaggle
```python
# No Drive mounting needed
# Files in /kaggle/working/

# Get secrets
from kaggle_secrets import UserSecretsClient
UserSecretsClient().get_secret('HF_TOKEN')
```

---

## Processing Speed

| Platform | GPU | Speed (chunks/min) |
|----------|-----|-------------------|
| **Colab** | T4 | ~70-100 |
| **Kaggle** | P100 | ~90-120 ✅ |
| **Kaggle** | V100 | ~100-140 ✅ |

---

## After Processing

### Download Results
**Colab:** Auto-save to Drive  
**Kaggle:** Click file icons to download

### Import Locally
```bash
# Same for both
python colab/import_results.py clip_candidates_*.json
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No GPU | Check More → Accelerator |
| HF_TOKEN error | Re-add secret (case-sensitive) |
| Upload fails | Use dataset, not direct upload |
| Download missing | Check /kaggle/working/ folder |

---

## Weekly Limits

```
Colab:  ~10 hours (resets weekly)
Kaggle: 30 hours  (resets Monday UTC) ✅
```

---

## Backup Plan

If Kaggle also at limit:

1. **Gradient.run** - Free P40 GPU
2. **Paperspace** - Free tier available
3. **Hugging Face Spaces** - Free A10G

---

## Summary

**Hit Colab limit?** → Use Kaggle!  
**Same Qwen3.5-4B**  
**Better GPU (P100)**  
**3x more hours (30/week)**  
**Worth the 5-min setup!** ✅
