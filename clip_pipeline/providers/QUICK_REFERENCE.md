# 🆓 Free GPU Providers - Quick Reference

## At a Glance

| Provider | Notebook | GPU | VRAM | Phone? | Time |
|----------|----------|-----|------|--------|------|
| **Gradient** | `gradient/` | P40 | 24GB | ❌ | ∞ |
| **HF Spaces** | `huggingface/` | A10G | 24GB | ❌ | Limited |
| **Oracle** | `oracle/` | A100 | 40GB | ✅ (CC) | ∞ |
| **Lightning** | `lightning/` | A10G | 24GB | ❌ | 22h/mo |
| **SageMaker** | `sagemaker/` | T4 | 16GB | ✅ (CC) | 250h/mo |

---

## Quick Links

| Provider | Sign Up | GPU Enable | Notes |
|----------|---------|------------|-------|
| **Gradient** | https://gradient.run | Resources → GPU | **Best overall** ✅ |
| **HF Spaces** | https://huggingface.co/spaces | Create Space → GPU | Good for tests |
| **Oracle** | https://cloud.oracle.com | Create VM → A100 | **Best performance** ✅ |
| **Lightning** | https://lightning.ai | New Studio → GPU | 22h/month |
| **SageMaker** | https://studiolab.sagemaker.aws | GPU Notebook | 1-2 day approval |

---

## Setup Time

| Provider | Setup Time | First Run |
|----------|------------|-----------|
| Gradient | 5 min | 5 min |
| HF Spaces | 10 min | 15 min |
| Oracle | 30 min | 1 hour |
| Lightning | 5 min | 10 min |
| SageMaker | 5 min | 1-2 days (approval) |

---

## Performance (712 chunks)

| Provider | Time | Quality | Reliability |
|----------|------|---------|-------------|
| Gradient | 15 min | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| HF Spaces | 8 min | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Oracle | 5 min | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Lightning | 8 min | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| SageMaker | 12 min | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Best For...

| Use Case | Provider | Why |
|----------|----------|-----|
| Daily processing | **Gradient** | Unlimited, no phone |
| Best quality | **Oracle** | A100 fastest |
| Quick tests | **HF Spaces** | Fast setup |
| Backup option | **Lightning** | 22h/month reserve |
| AWS users | **SageMaker** | Integrated with AWS |

---

## Account Requirements

| Provider | Email | Phone | Credit Card |
|----------|-------|-------|-------------|
| Gradient | ✅ | ❌ | ❌ |
| HF Spaces | ✅ | ❌ | ❌ |
| Oracle | ✅ | ✅ | ✅ |
| Lightning | ✅ (GitHub) | ❌ | ❌ |
| SageMaker | ✅ | ✅ | ✅ |

---

## Monthly Limits

| Provider | Free Limit | Resets | Rollover? |
|----------|------------|--------|-----------|
| Gradient | Unlimited* | Never | N/A |
| HF Spaces | Limited credits | Monthly | ❌ |
| Oracle | Unlimited | Never | N/A |
| Lightning | 22 hours | Monthly | ❌ |
| SageMaker | 250 hours | Monthly | ❌ |

*Fair use policy applies

---

## Emergency Backup Plan

**If all else fails:**

1. **Create new Colab account** (new Gmail)
2. **Use Paperspace** (free tier)
3. **Try GitHub Codespaces** (60 hours/month)
4. **Use local CPU** (slow but works)

---

## Recommended Setup

**Tier 1 (Primary):**
- Gradient.run (daily use)
- Oracle Cloud (heavy jobs)

**Tier 2 (Backup):**
- Hugging Face Spaces (quick tests)
- Lightning AI (monthly reserve)

**Tier 3 (Emergency):**
- SageMaker (when others at limit)
- New Colab accounts

---

## Files by Provider

```
providers/
├── gradient/
│   ├── clip_mining_gradient.ipynb
│   └── README.md
├── huggingface/
│   ├── clip_mining_hf_spaces.ipynb
│   └── README.md
├── oracle/
│   ├── clip_mining_oracle.ipynb
│   └── README.md
├── lightning/
│   ├── clip_mining_lightning.ipynb
│   └── README.md
└── sagemaker/
    ├── clip_mining_sagemaker.ipynb
    └── README.md
```

---

## One-Liner Setup Commands

### Gradient
```bash
upload clip_mining_gradient.ipynb → Enable GPU → Add HF_TOKEN → Run
```

### Hugging Face
```bash
create Space → Select GPU → Upload notebook → Add secret → Run
```

### Oracle
```bash
create VM (A100) → install CUDA → upload notebook → jupyter notebook
```

### Lightning
```bash
create Studio → Select GPU → Upload notebook → Run
```

### SageMaker
```bash
request access → wait approval → start GPU notebook → upload → Run
```

---

## Troubleshooting Quick Fix

| Problem | Quick Fix |
|---------|-----------|
| No GPU option | Refresh page, check account verification |
| Out of memory | Reduce batch size, use 8-bit quantization |
| Token expired | Regenerate HF token, update secrets |
| File not found | Check path: `/notebooks/` (Gradient), `/` (HF) |
| Session timeout | Save checkpoints every 100 chunks |

---

## Total Free GPU Time Available

```
Gradient:       Unlimited
Oracle:         Unlimited
Lightning:      22 hours/month
HF Spaces:      ~20 hours/month (estimated)
SageMaker:      250 hours/month
----------------------------
TOTAL:          ~300+ hours/month!
```

**You have access to MORE than enough free GPU time!** 🚀

---

## Quick Decision Tree

```
Need GPU now?
├─ Yes, no phone verification → Gradient ✅
├─ Yes, have credit card → Oracle ✅
├─ Quick test only → Hugging Face Spaces
├─ Monthly project → Lightning AI
└─ Already using AWS → SageMaker

Hit limits?
├─ Gradient full → Try Oracle
├─ Oracle full → Try Lightning
├─ All full → Create new Colab account
└─ Emergency → Use local CPU
```

---

**Remember:** Same pipeline, different platforms. Upload `chunks.json`, run notebook, download results! 🎉
