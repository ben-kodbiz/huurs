# auto_agentic_free_gpu.py
import os
import subprocess
import sys
import time
import torch
import webbrowser
from pathlib import Path
import json

# ==========================
# CONFIGURATION
# ==========================
AGENTIC_REPO = "https://github.com/username/agentic_project.git"
MODEL_NAME = "Qwen/Qwen-3.5-35B"
CHECKPOINT_DIR = Path("/content/drive/MyDrive/agentic_checkpoints")
BATCH_SIZES = {"T4": 8, "P100": 16, "K80": 4, "CPU": 1}  
PRECISION = {"GPU": "float16", "CPU": "float32"}  
LAST_STEP_FILE = CHECKPOINT_DIR / "last_step.json"

FREE_GPU_PROVIDERS = {
    "Colab": "https://colab.research.google.com/",
    "Kaggle": "https://www.kaggle.com/kernels",
    "Gradient Community": "https://gradient.run/community",
    "Paperspace Free Tier": "https://www.paperspace.com/console"
}

# ==========================
# UTILITY FUNCTIONS
# ==========================
def check_gpu():
    """Detect GPU and type."""
    try:
        result = subprocess.check_output(["nvidia-smi"], stderr=subprocess.STDOUT).decode()
        print("GPU detected:")
        print(result)
        for gpu_type in BATCH_SIZES:
            if gpu_type in result:
                return True, gpu_type
        return True, "GPU"
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("No GPU detected.")
        return False, "CPU"

def mount_drive():
    """Mount Google Drive if in Colab."""
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Drive mounted. Checkpoints folder: {CHECKPOINT_DIR}")
    except ImportError:
        print("Not running in Colab. Skipping Drive mount.")

def setup_environment():
    """Install essential packages."""
    print("Installing dependencies...")
    packages = ["torch", "transformers", "accelerate", "uv"]
    for pkg in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
    print("Environment ready.")

def clone_agentic_repo():
    """Clone project repo if needed."""
    if not Path("agentic_project").exists():
        subprocess.run(["git", "clone", AGENTIC_REPO])
    os.chdir("agentic_project")
    print("Agentic project directory ready.")

def load_agentic_model(gpu_type):
    """Load model with optimal batch size & precision."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if PRECISION.get(device, "float32") == "float16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto" if device == "cuda" else None,
        torch_dtype=torch_dtype
    )

    batch_size = BATCH_SIZES.get(gpu_type, 1)
    print(f"Model loaded on {device} | Batch size {batch_size} | Precision {torch_dtype}")
    return model, tokenizer, batch_size

# ==========================
# CHECKPOINT FUNCTIONS
# ==========================
def save_checkpoint(model, step):
    """Save model checkpoint and last step."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    path = CHECKPOINT_DIR / f"checkpoint_step_{step}"
    model.save_pretrained(path)
    with open(LAST_STEP_FILE, "w") as f:
        json.dump({"last_step": step}, f)
    print(f"Checkpoint saved at step {step}: {path}")

def load_last_step():
    """Load last step from checkpoint."""
    if LAST_STEP_FILE.exists():
        with open(LAST_STEP_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_step", 0)
    return 0

# ==========================
# FALLBACK FUNCTIONS
# ==========================
def fallback_free_gpu():
    """Open free GPU providers in browser."""
    print("No GPU available. Please use one of these free GPU providers:")
    for name, url in FREE_GPU_PROVIDERS.items():
        print(f"{name}: {url}")
        webbrowser.open(url)

# ==========================
# MAIN AUTOMATION
# ==========================
def main():
    print("=== Full Free GPU Agentic Manager ===")
    gpu_available, gpu_type = check_gpu()

    if gpu_available:
        print(f"GPU available: {gpu_type}. Setting up environment...")
        mount_drive()
        setup_environment()
        clone_agentic_repo()
        model, tokenizer, batch_size = load_agentic_model(gpu_type)

        # Resume from last step if checkpoint exists
        start_step = load_last_step() + 1
        print(f"Resuming from step {start_step}")

        # Example agentic loop with auto checkpointing
        total_steps = 10  # replace with your actual steps
        for step in range(start_step, total_steps + 1):
            print(f"Running agentic step {step}...")
            # Replace this with your actual agentic processing
            time.sleep(1)  # simulate processing
            if step % 2 == 0:  # checkpoint every 2 steps
                save_checkpoint(model, step)

        print("Agentic code run completed successfully on GPU!")

    else:
        print("No free GPU detected in this environment.")
        fallback_free_gpu()
        print("Manual intervention needed. Restart your agentic code on one of these free GPUs.")

if __name__ == "__main__":
    main()