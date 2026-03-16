"""GPU Manager for Colab Video Pipeline

Features:
- GPU detection (T4, P100, K80, CPU)
- Auto batch size configuration
- Google Drive mount for checkpoints
- Auto-checkpointing every N batches
- Manual resume from checkpoint
- Precision auto-tuning (float16/float32)
"""

import os
import json
import time
import torch
from pathlib import Path
from datetime import datetime


# ==========================
# CONFIGURATION
# ==========================

# GPU-specific configurations
GPU_CONFIGS = {
    "T4": {
        "batch_size": 8,
        "precision": "float16",
        "max_memory_gb": 15
    },
    "P100": {
        "batch_size": 16,
        "precision": "float16",
        "max_memory_gb": 16
    },
    "V100": {
        "batch_size": 16,
        "precision": "float16",
        "max_memory_gb": 16
    },
    "K80": {
        "batch_size": 4,
        "precision": "float16",
        "max_memory_gb": 12
    },
    "CPU": {
        "batch_size": 1,
        "precision": "float32",
        "max_memory_gb": 0
    }
}

# Free GPU providers (for fallback)
FREE_GPU_PROVIDERS = {
    "Google Colab": "https://colab.research.google.com/",
    "Kaggle Kernels": "https://www.kaggle.com/kernels",
    "Gradient Community": "https://gradient.run/community",
    "Paperspace Free Tier": "https://www.paperspace.com/console"
}


class GPUManager:
    """Manages GPU resources for Colab video pipeline."""
    
    def __init__(self, checkpoint_dir="/content/drive/MyDrive/video_pipeline/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.gpu_available = False
        self.gpu_type = "CPU"
        self.config = GPU_CONFIGS["CPU"]
        self.last_checkpoint_file = None
        
    def detect_gpu(self):
        """Detect GPU type and return configuration."""
        print("="*60)
        print("GPU DETECTION")
        print("="*60)
        
        if torch.cuda.is_available():
            self.gpu_available = True
            gpu_name = torch.cuda.get_device_name(0)
            
            # Detect GPU type
            if "T4" in gpu_name:
                self.gpu_type = "T4"
            elif "P100" in gpu_name:
                self.gpu_type = "P100"
            elif "V100" in gpu_name:
                self.gpu_type = "V100"
            elif "K80" in gpu_name:
                self.gpu_type = "K80"
            else:
                self.gpu_type = "GPU"  # Generic GPU
            
            self.config = GPU_CONFIGS.get(self.gpu_type, GPU_CONFIGS["T4"])
            
            print(f"✓ GPU Detected: {gpu_name}")
            print(f"  Type: {self.gpu_type}")
            print(f"  Batch Size: {self.config['batch_size']}")
            print(f"  Precision: {self.config['precision']}")
            print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("⚠️ No GPU detected - using CPU")
            self.gpu_available = False
            self.gpu_type = "CPU"
            self.config = GPU_CONFIGS["CPU"]
        
        print("="*60)
        return self.gpu_available, self.gpu_type, self.config
    
    def get_batch_size(self):
        """Get optimal batch size for current GPU."""
        return self.config['batch_size']
    
    def get_precision(self):
        """Get optimal precision for current GPU."""
        if self.config['precision'] == "float16":
            return torch.float16
        return torch.float32
    
    def mount_google_drive(self):
        """Mount Google Drive for checkpoint storage."""
        print("\n" + "="*60)
        print("GOOGLE DRIVE MOUNT")
        print("="*60)
        
        try:
            from google.colab import drive
            print("Running in Google Colab - mounting Drive...")
            drive.mount('/content/drive')
            
            # Create checkpoint directory
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"✓ Drive mounted successfully")
            print(f"  Checkpoint directory: {self.checkpoint_dir}")
            return True
            
        except ImportError:
            print("⚠️ Not running in Colab - skipping Drive mount")
            # Create local checkpoint dir
            self.checkpoint_dir = Path("./checkpoints")
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Using local directory: {self.checkpoint_dir}")
            return False
    
    def save_checkpoint(self, processed_chunks, step, total_steps, metadata=None):
        """Save checkpoint to Drive."""
        if not self.checkpoint_dir.exists():
            print("⚠️ Checkpoint directory not set - skipping save")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.checkpoint_dir / f"checkpoint_step_{step}_{timestamp}.json"
        
        checkpoint_data = {
            "step": step,
            "total_steps": total_steps,
            "timestamp": timestamp,
            "gpu_type": self.gpu_type,
            "processed_chunks": processed_chunks,
            "metadata": metadata or {}
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        self.last_checkpoint_file = checkpoint_file
        print(f"💾 Checkpoint saved: {checkpoint_file.name}")
        print(f"   Processed: {step}/{total_steps} chunks")
        return checkpoint_file
    
    def list_checkpoints(self):
        """List available checkpoints."""
        if not self.checkpoint_dir.exists():
            return []
        
        checkpoints = list(self.checkpoint_dir.glob("checkpoint_step_*.json"))
        return sorted(checkpoints, key=lambda p: p.stat().st_mtime, reverse=True)
    
    def load_checkpoint(self, checkpoint_file=None):
        """Load checkpoint for resume."""
        if checkpoint_file is None:
            # Get latest checkpoint
            checkpoints = self.list_checkpoints()
            if not checkpoints:
                print("✓ No checkpoints found - starting fresh")
                return None, 0
            
            checkpoint_file = checkpoints[0]
            print(f"Found latest checkpoint: {checkpoint_file.name}")
        
        if not checkpoint_file.exists():
            print(f"⚠️ Checkpoint file not found: {checkpoint_file}")
            return None, 0
        
        print(f"Loading checkpoint: {checkpoint_file.name}")
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        step = data.get('step', 0)
        processed_chunks = data.get('processed_chunks', [])
        
        print(f"✓ Loaded checkpoint from step {step}")
        print(f"  Processed chunks: {len(processed_chunks)}")
        print(f"  Timestamp: {data.get('timestamp', 'unknown')}")
        
        return processed_chunks, step
    
    def show_resume_prompt(self, checkpoint_file, step, total_steps):
        """Show manual resume prompt."""
        print("\n" + "="*60)
        print("CHECKPOINT FOUND - MANUAL RESUME")
        print("="*60)
        print(f"Previous session checkpoint found:")
        print(f"  File: {checkpoint_file.name}")
        print(f"  Progress: {step}/{total_steps} chunks ({step/total_steps*100:.1f}%)")
        print(f"  GPU Type: {self.gpu_type}")
        print(f"  Timestamp: {checkpoint_file.stat().st_mtime}")
        print()
        print("Options:")
        print("  [R] Resume from checkpoint (continue processing)")
        print("  [N] Start fresh (ignore checkpoint)")
        print()
        
        while True:
            choice = input("Your choice (R/N): ").strip().lower()
            if choice in ['r', 'resume']:
                print("✓ Resuming from checkpoint...")
                return True
            elif choice in ['n', 'new', 'no']:
                print("✓ Starting fresh processing...")
                return False
            else:
                print("Please enter 'R' or 'N'")
    
    def show_fallback_providers(self):
        """Show free GPU providers if no GPU available."""
        print("\n" + "="*60)
        print("⚠️ NO GPU AVAILABLE")
        print("="*60)
        print("Please use one of these FREE GPU providers:")
        print()
        for name, url in FREE_GPU_PROVIDERS.items():
            print(f"  {name}:")
            print(f"    {url}")
            print()
        print("After connecting to a GPU, restart this notebook.")
        print("="*60)
    
    def get_processing_stats(self, processed_count, total_count, elapsed_time):
        """Get processing statistics."""
        remaining = total_count - processed_count
        avg_time = elapsed_time / processed_count if processed_count > 0 else 0
        eta_seconds = remaining * avg_time
        
        return {
            "processed": processed_count,
            "total": total_count,
            "remaining": remaining,
            "progress": processed_count / total_count * 100,
            "elapsed_min": elapsed_time / 60,
            "eta_min": eta_seconds / 60,
            "chunks_per_min": processed_count / (elapsed_time / 60) if elapsed_time > 0 else 0
        }


# ==========================
# UTILITY FUNCTIONS
# ==========================

def check_gpu():
    """Quick GPU check."""
    gpu_mgr = GPUManager()
    return gpu_mgr.detect_gpu()


def get_optimal_config():
    """Get optimal GPU configuration."""
    gpu_mgr = GPUManager()
    gpu_mgr.detect_gpu()
    return {
        "gpu_type": gpu_mgr.gpu_type,
        "batch_size": gpu_mgr.get_batch_size(),
        "precision": gpu_mgr.get_precision(),
        "gpu_available": gpu_mgr.gpu_available
    }


# Test
if __name__ == "__main__":
    print("Testing GPU Manager...")
    gpu_mgr = GPUManager()
    gpu_mgr.detect_gpu()
    gpu_mgr.mount_google_drive()
    
    print(f"\nConfiguration:")
    print(f"  GPU: {gpu_mgr.gpu_type}")
    print(f"  Batch Size: {gpu_mgr.get_batch_size()}")
    print(f"  Precision: {gpu_mgr.get_precision()}")
