#!/usr/bin/env python3
"""Setup Hugging Face Authentication.

Interactive script to setup HF token for clip mining pipeline.
"""

import os
from pathlib import Path


def main():
    print("="*60)
    print("HUGGING FACE AUTHENTICATION SETUP")
    print("="*60)
    print()
    print("This script will help you setup Hugging Face authentication")
    print("for using private/gated models in the clip mining pipeline.")
    print()
    
    # Check current status
    print("Current Status:")
    print("-"*60)
    
    # Check environment variable
    env_token = os.environ.get("HF_TOKEN")
    if env_token:
        print("✓ HF_TOKEN environment variable is set")
        print(f"  Token: {env_token[:10]}...{env_token[-5:]}")
    else:
        print("✗ HF_TOKEN environment variable NOT set")
    
    # Check token file
    token_file = Path.home() / ".huggingface" / "token"
    if token_file.exists():
        print(f"✓ Token file exists: {token_file}")
    else:
        print(f"✗ Token file NOT found: {token_file}")
    
    # Check huggingface_hub cache
    try:
        from huggingface_hub import HfFolder
        cached_token = HfFolder.get_token()
        if cached_token:
            print("✓ Cached token found in huggingface_hub")
        else:
            print("✗ No cached token in huggingface_hub")
    except ImportError:
        print("✗ huggingface_hub not installed")
        print("\nInstall with: pip install huggingface_hub")
        return
    
    print()
    
    # Setup options
    print("Setup Options:")
    print("-"*60)
    print("1. Set HF_TOKEN environment variable (current session only)")
    print("2. Create token file (~/.huggingface/token)")
    print("3. Test token validity")
    print("4. Exit")
    print()
    
    while True:
        choice = input("Your choice (1-4): ").strip()
        
        if choice == "1":
            token = input("Enter HF token: ").strip()
            if token:
                os.environ["HF_TOKEN"] = token
                print(f"✓ HF_TOKEN set for current session")
                print(f"  To make permanent, add to ~/.bashrc:")
                print(f'  export HF_TOKEN="{token}"')
        
        elif choice == "2":
            token = input("Enter HF token: ").strip()
            if token:
                token_file.parent.mkdir(parents=True, exist_ok=True)
                token_file.write_text(token)
                token_file.chmod(0o600)  # Secure permissions
                print(f"✓ Token saved to {token_file}")
        
        elif choice == "3":
            token = os.environ.get("HF_TOKEN")
            if not token and token_file.exists():
                token = token_file.read_text().strip()
            
            if token:
                try:
                    from huggingface_hub import HfApi
                    api = HfApi()
                    user = api.whoami(token=token)
                    print(f"✓ Token is valid!")
                    print(f"  Logged in as: {user['name']}")
                    print(f"  Email: {user.get('email', 'N/A')}")
                    
                    # Check for private models
                    models = list(api.list_models(author=user['name'], limit=5))
                    if models:
                        print(f"  You have access to {len(models)} models")
                except Exception as e:
                    print(f"✗ Token validation failed: {e}")
            else:
                print("✗ No token found to test")
        
        elif choice == "4":
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")
        
        print()
    
    print()
    print("="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Run the clip mining pipeline:")
    print("   python -m clip_pipeline.run_pipeline --transcript chunks.json ...")
    print()
    print("2. For Colab, add HF_TOKEN to Colab Secrets")
    print("   Settings → Secrets → Add secret")
    print()


if __name__ == "__main__":
    main()
