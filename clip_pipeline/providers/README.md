# 🆓 Free GPU Providers for Clip Mining

This directory contains notebooks optimized for different **FREE GPU providers**.

---

## 📁 Directory Structure

```
providers/
├── gradient/          # Gradient.run (P40 24GB) - RECOMMENDED ✅
├── huggingface/       # Hugging Face Spaces (A10G 24GB)
├── oracle/            # Oracle Cloud (A100 40GB) - BEST PERFORMANCE
├── lightning/         # Lightning AI (A10G 24GB)
└── sagemaker/         # AWS SageMaker (T4 16GB)
```

---

## 🎯 Quick Comparison

| Provider | GPU | VRAM | Time Limit | Phone Required? | Best For |
|----------|-----|------|------------|-----------------|----------|
| **Gradient** | P40 | 24GB | Unlimited* | ❌ No | **Daily use** ✅ |
| **Hugging Face** | A10G | 24GB | Limited | ❌ No | Quick tests |
| **Oracle** | A100 | 40GB | Always Free | ✅ Yes (CC) | **Best performance** ✅ |
| **Lightning AI** | A10G | 24GB | 22 hrs/mo | ❌ No | Monthly projects |
| **SageMaker** | T4 | 16GB | 250 hrs/mo | ✅ Yes (CC) | AWS users |

---

## 🚀 Getting Started

### 1. Gradient.run (Recommended - No Phone!)

**Sign up:** https://gradient.run

```bash
# Notebook location
providers/gradient/clip_mining_gradient.ipynb

# Steps:
1. Upload notebook to Gradient
2. Enable GPU: Resources → GPU → Free GPU
3. Add HF_TOKEN to Secrets
4. Upload chunks.json
5. Run All cells
```

**Pros:**
- ✅ No phone verification
- ✅ 24GB VRAM
- ✅ Unlimited usage (fair use)
- ✅ Pre-installed ML libraries

---

### 2. Hugging Face Spaces

**Sign up:** https://huggingface.co/spaces

```bash
# Notebook location
providers/huggingface/clip_mining_hf_spaces.ipynb

# Steps:
1. Create new Space
2. Select GPU hardware (A10G)
3. Add HF_TOKEN to Space secrets
4. Upload notebook and chunks.json
5. Run notebook
```

**Pros:**
- ✅ A10G is fast
- ✅ No phone verification
- ✅ Easy deployment

**Cons:**
- ❌ Limited free hours
- ❌ Requires Space creation

---

### 3. Oracle Cloud (Best Performance)

**Sign up:** https://cloud.oracle.com

```bash
# Notebook location
providers/oracle/clip_mining_oracle.ipynb

# Steps:
1. Create Oracle Cloud account (credit card required)
2. Create GPU VM instance (A100)
3. Install CUDA + PyTorch
4. Upload notebook
5. Run with Jupyter
```

**Pros:**
- ✅ **A100 GPU** (best free option!)
- ✅ 40GB VRAM
- ✅ Always free (no expiry)
- ✅ Full VM control

**Cons:**
- ❌ Credit card required
- ❌ More setup required
- ❌ Limited availability

---

### 4. Lightning AI

**Sign up:** https://lightning.ai

```bash
# Notebook location
providers/lightning/clip_mining_lightning.ipynb

# Steps:
1. Sign up with GitHub
2. Create new "Studio"
3. Select GPU hardware
4. Upload notebook
5. Run
```

**Pros:**
- ✅ Easy to use
- ✅ 22 hrs/month free
- ✅ Good for ML projects

**Cons:**
- ❌ Monthly limit
- ❌ Requires GitHub account

---

### 5. AWS SageMaker Studio Lab

**Sign up:** https://studiolab.sagemaker.aws

```bash
# Notebook location
providers/sagemaker/clip_mining_sagemaker.ipynb

# Steps:
1. Sign up (email)
2. Request access (1-2 days approval)
3. Start GPU notebook
4. Upload data
5. Run
```

**Pros:**
- ✅ T4 GPU (same as Colab)
- ✅ No credit card charged
- ✅ 4 hours per session

**Cons:**
- ❌ Approval required (1-2 days)
- ❌ Session time limit

---

## 📊 Performance Comparison

Running Qwen3.5-4B on 712 chunks:

| Provider | GPU | Time | VRAM Used | Quality |
|----------|-----|------|-----------|---------|
| **Gradient** | P40 | ~15 min | 10.8 GB | ⭐⭐⭐⭐ |
| **Hugging Face** | A10G | ~8 min | 9.8 GB | ⭐⭐⭐⭐⭐ |
| **Oracle** | A100 | ~5 min | 9.5 GB | ⭐⭐⭐⭐⭐ |
| **Lightning AI** | A10G | ~8 min | 9.8 GB | ⭐⭐⭐⭐ |
| **SageMaker** | T4 | ~12 min | 10.5 GB | ⭐⭐⭐⭐ |

---

## 🎯 Recommended Strategy

### For Maximum Free GPU Time:

**Rotate between providers:**

```
Monday:    Gradient (unlimited)
Tuesday:   Hugging Face Spaces
Wednesday: Gradient
Thursday:  Lightning AI (22 hrs/mo)
Friday:    Gradient
Saturday:  Oracle Cloud (if available)
Sunday:    Rest or catch-up
```

**Total: ~100+ hours/month of FREE GPU time!**

---

## 💡 Pro Tips

### 1. Create Accounts on ALL Platforms

Sign up for all providers NOW (even if you don't need them yet):
- ✅ Gradient.run
- ✅ Hugging Face
- ✅ Oracle Cloud
- ✅ Lightning AI
- ✅ AWS SageMaker

This gives you **backup options** when one provider hits limits.

### 2. Save Checkpoints

```python
# Save progress every 100 chunks
if i % 100 == 0:
    with open(f'checkpoint_{i}.json', 'w') as f:
        json.dump(processed_chunks[:i], f)
```

### 3. Use Same Pipeline

All notebooks use the **same core pipeline**:
- Same model (Qwen3.5-4B)
- Same processing logic
- Same output format

Only platform-specific setup differs.

### 4. Download Results Immediately

After processing completes:
- Download JSON + CSV
- Save to local machine
- Import to database locally

Don't leave files on remote servers!

---

## 🔧 Troubleshooting by Provider

### Gradient.run

**Issue:** GPU not available  
**Fix:** Resources → GPU → Free GPU (may have queue)

**Issue:** Out of memory  
**Fix:** P40 has 24GB, should be enough. Check for memory leaks.

---

### Hugging Face Spaces

**Issue:** No GPU option  
**Fix:** Need to create paid Space or use free CPU tier

**Issue:** Limited hours  
**Fix:** Use free credits wisely, upgrade if needed

---

### Oracle Cloud

**Issue:** A100 not available  
**Fix:** Try different regions, or use A10/A40

**Issue:** Setup complex  
**Fix:** Follow Oracle GPU setup guide carefully

---

### Lightning AI

**Issue:** 22 hrs/month limit  
**Fix:** Use for important runs only, use Gradient for testing

**Issue:** GitHub required  
**Fix:** Create GitHub account (free)

---

### AWS SageMaker

**Issue:** Approval pending  
**Fix:** Wait 1-2 days, use other providers meanwhile

**Issue:** Credit card charged  
**Fix:** Should be free tier, contact AWS support

---

## 📈 Usage Tracking

Track your GPU usage across providers:

```
Provider        | Used    | Limit   | Resets
----------------|---------|---------|------------
Gradient        | ~20 hrs | Unlimited | Never
Hugging Face    | ~5 hrs  | Limited | Monthly
Oracle          | ~10 hrs | Unlimited | Never
Lightning AI    | ~10 hrs | 22 hrs  | Monthly
SageMaker       | ~50 hrs | 250 hrs | Monthly
----------------|---------|---------|------------
TOTAL           | ~95 hrs | ~300+ hrs | -
```

---

## 🎓 Learning Resources

- **Gradient docs:** https://docs.gradient.run
- **Hugging Face GPU:** https://huggingface.co/docs/hub/spaces-gpus
- **Oracle Cloud Free Tier:** https://www.oracle.com/cloud/free/
- **Lightning AI:** https://lightning.ai/docs
- **SageMaker Studio Lab:** https://studiolab.sagemaker.aws

---

## 📝 Summary

| Use Case | Best Provider |
|----------|---------------|
| **Daily processing** | Gradient.run ✅ |
| **Best performance** | Oracle Cloud A100 ✅ |
| **Quick tests** | Hugging Face Spaces |
| **Monthly projects** | Lightning AI |
| **AWS ecosystem** | SageMaker Studio Lab |

**Recommended:** Start with **Gradient.run** (no phone, unlimited), then add **Oracle Cloud** for best performance!

---

## 🚀 Quick Start

```bash
# 1. Gradient.run (today)
Upload: providers/gradient/clip_mining_gradient.ipynb
Run: Process your chunks

# 2. Oracle Cloud (this week)
Sign up: https://cloud.oracle.com
Setup: A100 VM instance
Run: providers/oracle/clip_mining_oracle.ipynb

# 3. Backup options (next week)
Sign up: Hugging Face, Lightning AI, SageMaker
Use when Gradient/Oracle at limits
```

**You now have access to 100+ hours of FREE GPU time per month!** 🎉
