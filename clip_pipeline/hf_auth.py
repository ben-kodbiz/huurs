"""Hugging Face Authentication Helper.

Supports:
- Login via environment variable
- Login via token file
- Login via interactive prompt
- Token validation
- Private model access
"""

import os
from pathlib import Path
from huggingface_hub import login, HfApi


class HFAuth:
    """Hugging Face Authentication Manager."""

    def __init__(self, token: str = None):
        """
        Initialize HF authentication.

        Args:
            token: Optional HF token. If not provided, will try:
                   1. HF_TOKEN environment variable
                   2. ~/.huggingface/token file
                   3. Interactive prompt
        """
        self.token = token
        self.api = None
        self.logged_in = False

    def login(self) -> bool:
        """
        Login to Hugging Face.

        Returns:
            True if successful, False otherwise.
        """
        # Try to get token from various sources
        token = self._get_token()

        if not token:
            print("⚠️ No Hugging Face token found.")
            print("\nGet your token from: https://huggingface.co/settings/tokens")
            print("\nOptions:")
            print("  1. Set HF_TOKEN environment variable")
            print("  2. Create ~/.huggingface/token file")
            print("  3. Enter token interactively")
            return False

        try:
            # Login
            login(token=token)
            self.token = token
            self.logged_in = True

            # Initialize API
            self.api = HfApi()

            # Verify token
            user = self.api.whoami(token=token)
            username = user.get("name", "unknown")
            print(f"✓ Logged in to Hugging Face as: {username}")

            return True

        except Exception as e:
            print(f"❌ Failed to login: {e}")
            return False

    def _get_token(self) -> str:
        """Get token from various sources."""
        # 1. Check constructor argument
        if self.token:
            print("✓ Using provided token")
            return self.token

        # 2. Check environment variable
        token = os.environ.get("HF_TOKEN")
        if token:
            print("✓ Using HF_TOKEN environment variable")
            return token

        # 3. Check token file
        token_file = Path.home() / ".huggingface" / "token"
        if token_file.exists():
            token = token_file.read_text().strip()
            if token:
                print(f"✓ Using token from {token_file}")
                return token

        # 4. Check Hugging Face cache
        try:
            from huggingface_hub import get_token
            token = get_token()
            if token:
                print("✓ Using cached Hugging Face token")
                return token
        except Exception:
            pass
        
        # 5. Interactive prompt
        print("Enter your Hugging Face token:")
        print("Get it from: https://huggingface.co/settings/tokens")
        token = input("Token: ").strip()
        if token:
            # Save for future use
            token_file.parent.mkdir(parents=True, exist_ok=True)
            token_file.write_text(token)
            print(f"✓ Token saved to {token_file}")
            return token

        return None

    def check_model_access(self, model_id: str) -> bool:
        """
        Check if user has access to a model.

        Args:
            model_id: Model identifier (e.g., "meta-llama/Llama-2-7b")

        Returns:
            True if accessible, False otherwise.
        """
        if not self.logged_in:
            print(f"⚠️ Not logged in - cannot check access to {model_id}")
            return False

        try:
            # Try to get model info
            self.api.model_info(model_id, token=self.token)
            print(f"✓ Access confirmed: {model_id}")
            return True
        except Exception as e:
            print(f"❌ No access to {model_id}: {e}")
            return False

    def list_private_models(self) -> list:
        """
        List private models user has access to.

        Returns:
            List of model IDs.
        """
        if not self.logged_in:
            return []

        try:
            models = self.api.list_models(author=self.api.whoami(self.token)["name"])
            private_models = []
            for model in models:
                if getattr(model, "private", False):
                    private_models.append(model.id)
            return private_models
        except Exception:
            return []


def login_hf(token: str = None) -> bool:
    """
    Convenience function to login to Hugging Face.

    Args:
        token: Optional HF token.

    Returns:
        True if successful.
    """
    auth = HFAuth(token)
    return auth.login()


def check_hf_auth() -> bool:
    """
    Check if Hugging Face is authenticated.

    Returns:
        True if logged in.
    """
    token = os.environ.get("HF_TOKEN") or HfFolder.get_token()
    token_file = Path.home() / ".huggingface" / "token"

    if token or token_file.exists():
        return True
    return False


# Test
if __name__ == "__main__":
    print("Testing Hugging Face Authentication...")
    print("="*60)

    auth = HFAuth()

    if auth.login():
        print("\n✓ Authentication successful!")

        # Test model access
        print("\nTesting model access...")
        test_models = [
            "Qwen/Qwen2.5-3B-Instruct",  # Public
            "meta-llama/Llama-2-7b",     # Gated
        ]

        for model in test_models:
            auth.check_model_access(model)

        # List private models
        private = auth.list_private_models()
        if private:
            print(f"\nYour private models: {private}")
    else:
        print("\n❌ Authentication failed")
