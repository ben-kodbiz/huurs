# 🔐 HF Authentication Implementation Summary

## What Was Implemented

Hugging Face authentication support has been added to the clip mining pipeline, enabling the use of **private** and **gated** models.

---

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `clip_pipeline/hf_auth.py` | Core authentication module |
| `clip_pipeline/setup_hf_auth.py` | Interactive setup script |
| `docs/HF_AUTH.md` | Complete documentation |

### Modified Files

| File | Changes |
|------|---------|
| `clip_pipeline/clip_mining_gpu_FIXED.ipynb` | Added HF auth cell, token passed to model loading |
| `clip_pipeline/run_pipeline.py` | Added `--hf-token` option, auth check |
| `clip_pipeline/__init__.py` | Export `check_hf_auth` |

---

## Features

### 1. Multiple Authentication Methods

- ✅ Environment variable (`HF_TOKEN`)
- ✅ Token file (`~/.huggingface/token`)
- ✅ Interactive prompt
- ✅ Command line argument (`--hf-token`)
- ✅ Colab Secrets integration

### 2. Automatic Token Detection

The pipeline automatically checks for tokens in this order:
1. Command line argument
2. Environment variable
3. Token file
4. Hugging Face cache
5. Interactive prompt

### 3. Token Validation

- Verifies token validity before processing
- Shows logged-in username
- Lists accessible private models
- Checks model-specific access

### 4. Private Model Support

Models can now be loaded with authentication:

```python
# Colab
MODEL_NAME = "your-org/your-private-model"
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=hf_token
)

# Local
python -m clip_pipeline.run_pipeline \
    --transcript chunks.json \
    --hf-token hf_xxxxx...
```

---

## Usage Examples

### Local Pipeline with HF Auth

**Method 1: Environment Variable**
```bash
export HF_TOKEN="hf_xxxxx..."
python -m clip_pipeline.run_pipeline \
    --transcript chunks.json \
    --video-id lecture_001
```

**Method 2: Command Line**
```bash
python -m clip_pipeline.run_pipeline \
    --transcript chunks.json \
    --video-id lecture_001 \
    --hf-token hf_xxxxx...
```

**Method 3: Interactive Setup**
```bash
python clip_pipeline/setup_hf_auth.py
# Follow prompts to enter token
```

### Colab with HF Auth

1. **Add Secret:**
   - Colab → Settings → Secrets
   - Name: `HF_TOKEN`
   - Value: `hf_xxxxx...`

2. **Run Notebook:**
   - Open `clip_pipeline/clip_mining_gpu_FIXED.ipynb`
   - Run all cells
   - Authentication happens automatically

---

## Authentication Flow

```
┌─────────────────────────────────┐
│  Start Pipeline                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Check for HF_TOKEN             │
│  1. CLI argument                │
│  2. Environment variable        │
│  3. Token file                  │
│  4. Interactive prompt          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Validate Token                 │
│  - Call HfApi.whoami()          │
│  - Get username                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Load Model with Token          │
│  - AutoTokenizer.from_pretrained│
│  - AutoModel.from_pretrained    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Process Clips                  │
└─────────────────────────────────┘
```

---

## Security Features

✅ **Token Encryption:**
- Tokens stored with `600` permissions (owner read/write only)
- Never logged or printed in full

✅ **Multiple Storage Options:**
- Environment variables (session-only)
- Token file (persistent)
- Colab Secrets (encrypted)

✅ **No Token Exposure:**
- Tokens not shown in output
- Not committed to git (add to `.gitignore`)
- Command line option warns about history

---

## Testing Authentication

### Test Token Validity
```bash
python clip_pipeline/hf_auth.py
```

### Check Model Access
```bash
python -c "
from huggingface_hub import HfApi
import os

api = HfApi()
token = os.environ.get('HF_TOKEN')

# Test access to a model
model_id = 'meta-llama/Llama-2-7b'
try:
    api.model_info(model_id, token=token)
    print(f'✓ Access granted: {model_id}')
except Exception as e:
    print(f'❌ No access: {e}')
"
```

### List Private Models
```bash
python -c "
from huggingface_hub import HfApi
import os

api = HfApi()
token = os.environ.get('HF_TOKEN')

if token:
    user = api.whoami(token=token)
    models = api.list_models(author=user['name'])
    print(f'Your models: {[m.id for m in models]}')
"
```

---

## Troubleshooting

### Issue: "401 Unauthorized"

**Solution:**
1. Verify token is correct
2. Check token hasn't expired
3. Ensure you accepted model license

### Issue: "No HF_TOKEN Found"

**Solution:**
```bash
# Set environment variable
export HF_TOKEN="hf_xxxxx..."

# Or create token file
echo "hf_xxxxx..." > ~/.huggingface/token
```

### Issue: Model Loading Fails

**Solution:**
```bash
# Test with public model first
python -c "
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-3B-Instruct')
print('✓ Public models work')
"

# Then test private model with token
```

---

## Next Steps

1. **Get HF Token:**
   - Visit: https://huggingface.co/settings/tokens
   - Create Read token

2. **Setup Authentication:**
   ```bash
   python clip_pipeline/setup_hf_auth.py
   ```

3. **Test with Pipeline:**
   ```bash
   python -m clip_pipeline.run_pipeline \
       --transcript chunks.json \
       --video-id lecture_001
   ```

4. **Use Private Model (Optional):**
   ```python
   # In clip_mining_gpu_FIXED.ipynb
   MODEL_NAME = "your-org/your-private-model"
   ```

---

## Documentation

- **Full Guide:** `docs/HF_AUTH.md`
- **Setup Script:** `python clip_pipeline/setup_hf_auth.py`
- **Test Auth:** `python clip_pipeline/hf_auth.py`

---

## Summary

✅ Hugging Face authentication is now **fully integrated**
✅ Supports **multiple authentication methods**
✅ Works with **both local and Colab** pipelines
✅ Enables **private/gated model usage**
✅ Includes **comprehensive documentation**

You can now use any Hugging Face model you have access to!
