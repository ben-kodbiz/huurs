# 🚀 Quick Start: Qwen3.5-4B Clip Mining

## Setup HF Token (One Time)

```bash
# Add to .zshrc permanently
echo 'export HF_TOKEN="hf_xxxxx..."' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $HF_TOKEN
```

## Use in Colab

1. **Open Notebook:** Upload `clip_mining_qwen35_4b.ipynb` to Colab
2. **Enable GPU:** Runtime → Change runtime type → GPU (T4)
3. **Add Secret:** Settings → Secrets → Add `HF_TOKEN`
4. **Run All Cells**

## Use Locally

```bash
cd /mnt/AI/dev/huurs
source .venv/bin/activate

python -m clip_pipeline.run_pipeline \
    --transcript video_pipeline/chunks.json \
    --video-id "Nouman_Ali_Khan___Studying_Surah_Al_Mulk" \
    --title "Studying Surah Al-Mulk"
```

## Files

| File | Purpose |
|------|---------|
| `clip_pipeline/clip_mining_qwen35_4b.ipynb` | Colab with Qwen3.5-4B |
| `docs/HF_TOKEN_ZSHRC_SETUP.md` | Permanent token setup |
| `docs/HF_AUTH.md` | Full HF auth guide |

## Get Help

```bash
# Setup guide
cat docs/HF_TOKEN_ZSHRC_SETUP.md

# Test authentication
python clip_pipeline/setup_hf_auth.py
```
