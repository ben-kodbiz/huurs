# 🔐 Hugging Face Authentication Guide

This guide explains how to setup Hugging Face authentication for using **private** and **gated** models in the clip mining pipeline.

---

## Why Authenticate?

Hugging Face authentication allows you to:

1. **Access gated models** (e.g., Llama-2, Mistral)
2. **Use private models** (your own or shared with you)
3. **Higher rate limits** for model downloads
4. **Track usage** across sessions

---

## Get Your HF Token

1. Go to https://huggingface.co/settings/tokens
2. Click **"Create new token"**
3. Choose token type:
   - **Read** (recommended) - For loading models
   - **Write** - For uploading models
4. Copy the token (starts with `hf_...`)

---

## Setup Methods

### Method 1: Environment Variable (Recommended for Colab)

**Google Colab:**

1. In Colab, click **Settings** (gear icon) → **Secrets**
2. Click **"Add secret"**
3. Enter:
   - **Name:** `HF_TOKEN`
   - **Value:** `hf_xxxxxxxxxxxxxxxxxxxxxxxxxx`
4. Click **"OK"**

The token will be automatically available as `os.environ.get("HF_TOKEN")`.

**Local (Linux/Mac):**

```bash
# Add to ~/.bashrc or ~/.zshrc
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"

# Reload
source ~/.bashrc
```

**Local (Windows):**

```powershell
# PowerShell
$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"

# Or permanently via System Properties → Environment Variables
```

---

### Method 2: Token File

Create a token file at `~/.huggingface/token`:

```bash
mkdir -p ~/.huggingface
echo "hf_xxxxxxxxxxxxxxxxxxxxxxxxxx" > ~/.huggingface/token
chmod 600 ~/.huggingface/token
```

The pipeline will automatically read this file.

---

### Method 3: Interactive Prompt

Run the authentication helper:

```bash
cd /mnt/AI/dev/huurs
source .venv/bin/activate

python clip_pipeline/hf_auth.py
```

It will prompt you to enter your token interactively.

---

### Method 4: Command Line Argument

Pass token directly when running the pipeline:

```bash
python -m clip_pipeline.run_pipeline \
    --transcript chunks.json \
    --video-id lecture_001 \
    --hf-token hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **Warning:** This exposes your token in shell history. Use environment variables instead.

---

## Using in Colab Notebook

The updated `clip_mining_gpu_FIXED.ipynb` automatically checks for HF authentication:

### Step 1: Set Secret (First Time Only)

1. Colab → Settings → Secrets
2. Add `HF_TOKEN` with your token value

### Step 2: Run Authentication Cell

```python
# Step 1b: Hugging Face Authentication
import os
from huggingface_hub import login, HfApi

hf_token = os.environ.get("HF_TOKEN")

if hf_token:
    login(token=hf_token)
    api = HfApi()
    user = api.whoami(token=hf_token)
    print(f"✓ Logged in as: {user['name']}")
```

### Step 3: Load Private Model

```python
# Use your private model
MODEL_NAME = "your-org/your-private-model"

# Token is automatically passed
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=hf_token  # Uses your token
)
```

---

## Verify Authentication

### Check Token Validity

```bash
python -c "
from huggingface_hub import HfApi
import os

token = os.environ.get('HF_TOKEN')
if token:
    api = HfApi()
    user = api.whoami(token=token)
    print(f'✓ Valid token for: {user[\"name\"]}')
else:
    print('❌ No token found')
"
```

### List Your Private Models

```bash
python -c "
from huggingface_hub import HfApi
import os

api = HfApi()
token = os.environ.get('HF_TOKEN')

if token:
    models = api.list_models(author=api.whoami(token)['name'])
    private = [m.id for m in models if getattr(m, 'private', False)]
    print(f'Your private models: {private}')
"
```

### Check Model Access

```bash
python -c "
from huggingface_hub import HfApi
import os

api = HfApi()
token = os.environ.get('HF_TOKEN')

model_id = 'meta-llama/Llama-2-7b'  # Example gated model

try:
    api.model_info(model_id, token=token)
    print(f'✓ Access granted: {model_id}')
except Exception as e:
    print(f'❌ No access: {e}')
"
```

---

## Common Issues

### Issue: "401 Unauthorized"

**Cause:** Invalid or missing token

**Solution:**
1. Verify token is correct (starts with `hf_`)
2. Check token hasn't expired
3. Ensure you're using the right token type (Read is enough)

### Issue: "Model Not Found"

**Cause:** No access to gated/private model

**Solution:**
1. Accept model license on Hugging Face
2. Wait for access approval (some models require manual approval)
3. Verify token has correct permissions

### Issue: "Token Not Found"

**Cause:** Token not set in environment

**Solution:**
```bash
# Check if token is set
echo $HF_TOKEN

# If empty, set it
export HF_TOKEN="hf_xxxxx..."
```

---

## Example: Using Llama-2 (Gated Model)

1. **Get Access:**
   - Go to https://huggingface.co/meta-llama/Llama-2-7b
   - Click "Agree" to accept license
   - Wait for approval email

2. **Set Token:**
   ```bash
   export HF_TOKEN="hf_xxxxx..."
   ```

3. **Use in Pipeline:**
   ```python
   MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
   
   tokenizer = AutoTokenizer.from_pretrained(
       MODEL_NAME,
       token=os.environ.get("HF_TOKEN")
   )
   ```

---

## Security Best Practices

✅ **DO:**
- Use **Read** tokens for inference
- Store tokens in environment variables
- Rotate tokens periodically
- Use Colab Secrets for Colab

❌ **DON'T:**
- Commit tokens to git
- Share tokens publicly
- Use Write tokens for inference
- Pass tokens in command line arguments

---

## Files Added for HF Auth

| File | Purpose |
|------|---------|
| `clip_pipeline/hf_auth.py` | Authentication helper module |
| `clip_pipeline/clip_mining_gpu_FIXED.ipynb` | Updated Colab with HF auth |
| `clip_pipeline/run_pipeline.py` | Updated CLI with `--hf-token` option |
| `docs/HF_AUTH.md` | This documentation |

---

## Quick Reference

```bash
# Set token (Linux/Mac)
export HF_TOKEN="hf_xxxxx..."

# Set token (Windows PowerShell)
$env:HF_TOKEN="hf_xxxxx..."

# Run pipeline with auth
python -m clip_pipeline.run_pipeline \
    --transcript chunks.json \
    --video-id lecture_001

# Test authentication
python clip_pipeline/hf_auth.py
```

---

## Support

For issues with Hugging Face authentication:
- Docs: https://huggingface.co/docs/hub/security-tokens
- Forum: https://discuss.huggingface.co/
