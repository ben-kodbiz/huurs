# 🔐 Setup HF_TOKEN Permanently in .zshrc

This guide shows you how to setup Hugging Face authentication **permanently** so you don't have to enter your token every time.

---

## What is .zshrc?

`.zshrc` is a configuration file that runs automatically when you open a new terminal session. It's the perfect place to store environment variables like `HF_TOKEN`.

---

## Step-by-Step Setup

### Step 1: Get Your HF Token

1. Visit: https://huggingface.co/settings/tokens
2. Click **"Create new token"**
3. Choose **"Read"** access (enough for loading models)
4. Copy the token (starts with `hf_...`)

### Step 2: Add to .zshrc

Open your terminal and run:

```bash
# Open .zshrc in your text editor
nano ~/.zshrc
```

Add this line at the end:

```bash
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Replace `hf_xxxxx...` with your actual token.

**Save and exit:**
- Press `Ctrl + O` then `Enter` (save)
- Press `Ctrl + X` (exit)

### Step 3: Apply Changes

```bash
# Reload .zshrc
source ~/.zshrc

# Verify it worked
echo $HF_TOKEN
```

You should see your token printed (or at least the first few characters).

---

## Verify Setup

### Test 1: Check Environment Variable

```bash
echo $HF_TOKEN
```

Should output: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Test 2: Test with Python

```bash
python3 -c "
import os
from huggingface_hub import HfApi

token = os.environ.get('HF_TOKEN')
if token:
    api = HfApi()
    user = api.whoami(token=token)
    print(f'✓ Logged in as: {user[\"name\"]}')
else:
    print('❌ HF_TOKEN not found')
"
```

### Test 3: Test Model Access

```bash
python3 -c "
import os
from huggingface_hub import HfApi

api = HfApi()
token = os.environ.get('HF_TOKEN')

try:
    api.model_info('Qwen/Qwen3.5-4B', token=token)
    print('✓ Access granted: Qwen/Qwen3.5-4B')
except Exception as e:
    print(f'⚠️ Access issue: {e}')
"
```

---

## Test with Clip Mining Pipeline

```bash
cd /mnt/AI/dev/huurs
source .venv/bin/activate

# Run pipeline - HF_TOKEN will be automatically used
python -m clip_pipeline.run_pipeline \
    --transcript video_pipeline/chunks.json \
    --video-id lecture_001 \
    --title "Test Lecture"
```

You should see:
```
✓ HF_TOKEN found (authenticated)
  Logged in as: your_username
```

---

## Security Tips

### ✅ DO:

- Use **Read** tokens for inference (not Write)
- Set file permissions to protect `.zshrc`:
  ```bash
  chmod 600 ~/.zshrc
  ```
- Rotate tokens every few months
- Use different tokens for different purposes

### ❌ DON'T:

- Commit `.zshrc` to git (add to `.gitignore`)
- Share your token publicly
- Use Write tokens for model loading
- Paste tokens in public forums

---

## Alternative: Separate Token File

If you prefer not to put tokens in `.zshrc`, create a separate file:

```bash
# Create secure token file
mkdir -p ~/.config
echo 'export HF_TOKEN="hf_xxxxx..."' > ~/.config/hf_token.sh
chmod 600 ~/.config/hf_token.sh

# Source it in .zshrc
echo 'source ~/.config/hf_token.sh 2>/dev/null' >> ~/.zshrc
source ~/.zshrc
```

---

## Troubleshooting

### Issue: `echo $HF_TOKEN` shows nothing

**Solution:**
```bash
# Check if .zshrc was edited correctly
cat ~/.zshrc | grep HF_TOKEN

# Make sure you sourced it
source ~/.zshrc

# Check which shell you're using
echo $SHELL

# If it's /bin/bash instead of /bin/zsh, edit ~/.bashrc instead
```

### Issue: "command not found: source"

**Solution:**
```bash
# Use . instead of source
. ~/.zshrc
```

### Issue: Token shows but authentication fails

**Solution:**
1. Verify token is correct (no extra spaces)
2. Check token hasn't expired
3. Regenerate token from https://huggingface.co/settings/tokens

---

## For Bash Users

If you use **bash** instead of zsh:

```bash
# Edit .bashrc instead
nano ~/.bashrc

# Add the same line
export HF_TOKEN="hf_xxxxx..."

# Reload
source ~/.bashrc
```

---

## For Fish Shell Users

If you use **fish** shell:

```fish
# Set universal variable
set -U HF_TOKEN "hf_xxxxx..."

# Or add to config
echo 'set -x HF_TOKEN "hf_xxxxx..."' >> ~/.config/fish/config.fish
```

---

## Verify in New Terminal Session

**Important:** Test that it works in a **new** terminal window:

1. Close current terminal
2. Open new terminal
3. Run: `echo $HF_TOKEN`
4. Should show your token

If it doesn't work in a new terminal, check:
- You're using zsh (`echo $SHELL` should show `/bin/zsh`)
- `.zshrc` syntax is correct (no typos)
- File has correct permissions

---

## Remove HF_TOKEN (If Needed)

To remove the token later:

```bash
# Edit .zshrc
nano ~/.zshrc

# Delete or comment out the line
# export HF_TOKEN="hf_xxxxx..."

# Reload
source ~/.zshrc

# Verify removal
echo $HF_TOKEN  # Should be empty
```

---

## Summary

```bash
# 1. Edit .zshrc
nano ~/.zshrc

# 2. Add this line (use your token)
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 3. Save: Ctrl+O, Enter, Ctrl+X

# 4. Reload
source ~/.zshrc

# 5. Verify
echo $HF_TOKEN

# 6. Test
python -m clip_pipeline.run_pipeline --transcript chunks.json --video-id test
```

Your HF token is now permanently available! 🎉
