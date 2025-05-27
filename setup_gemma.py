#!/usr/bin/env python3
"""Setup quantized Gemma model for SV-Agent."""

import os
import sys
from pathlib import Path

def setup_gemma():
    """Download and setup Gemma model with quantization support."""
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    print("SV-Agent Gemma Model Setup")
    print("=" * 50)
    print("\nThis script will download Google's Gemma model for use with SV-Agent.")
    print("The model will be quantized on-the-fly when loaded.\n")
    
    print("Available Gemma models:")
    print("1. google/gemma-2b-it - Gemma 2B Instruct (~5GB download, ~2GB with 4-bit)")
    print("2. google/gemma-7b-it - Gemma 7B Instruct (~17GB download, ~4GB with 4-bit)")
    
    choice = input("\nSelect model (1-2) [default: 1]: ").strip() or "1"
    
    model_map = {
        "1": ("google/gemma-2b-it", "gemma-2b-it"),
        "2": ("google/gemma-7b-it", "gemma-7b-it"),
    }
    
    if choice not in model_map:
        print("Invalid choice")
        sys.exit(1)
    
    model_id, local_name = model_map[choice]
    local_dir = models_dir / local_name
    
    print(f"\nModel: {model_id}")
    print(f"Destination: {local_dir}")
    
    # Check for auth token
    auth_token = os.getenv("HF_TOKEN")
    if not auth_token:
        print("\n⚠️  Gemma models require accepting the license agreement.")
        print("\nSteps:")
        print(f"1. Go to https://huggingface.co/{model_id}")
        print("2. Sign in and accept the license agreement")
        print("3. Get your token from https://huggingface.co/settings/tokens")
        print("\nAlternatively, set the HF_TOKEN environment variable.")
        auth_token = input("\nEnter your HuggingFace token: ").strip()
        
        if not auth_token:
            print("\n❌ Token required for Gemma models")
            sys.exit(1)
    
    # Create a simple download script using transformers
    print("\nDownloading model files...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=auth_token,
            cache_dir=str(local_dir),
        )
        tokenizer.save_pretrained(str(local_dir))
        
        print("Downloading model (this may take a while)...")
        # Just download, don't load into memory
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=auth_token,
            cache_dir=str(local_dir),
            torch_dtype="auto",
            device_map="cpu",  # Just download, don't load to GPU
        )
        model.save_pretrained(str(local_dir))
        
        print(f"\n✅ Model downloaded to: {local_dir}")
        
        # Create convenience symlink
        latest_link = models_dir / "gemma-latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(local_name)
        
        print(f"✅ Created symlink: models/gemma-latest -> {local_name}")
        
        # Show usage examples
        print("\n" + "=" * 50)
        print("Setup complete! Example usage:")
        print("\n# Chat with 4-bit quantization (recommended):")
        print("sv-agent --model models/gemma-latest --load-in-4bit chat")
        print("\n# Single question:")
        print("sv-agent --model models/gemma-latest --load-in-4bit ask \"What coverage do I need for SV detection?\"")
        print("\n# Without quantization (requires more memory):")
        print("sv-agent --model models/gemma-latest chat")
        
        # Update the default model in a config file
        config_file = Path("models/default_model.txt")
        config_file.write_text("models/gemma-latest")
        print(f"\n✅ Set as default model in: {config_file}")
        
    except ImportError:
        print("\n❌ Error: transformers not installed")
        print("Install with: pip install transformers torch")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if "401" in str(e):
            print("\nAuthentication failed. Please ensure:")
            print("1. You have accepted the Gemma license at https://huggingface.co/{model_id}")
            print("2. Your token has read permissions")
        sys.exit(1)

if __name__ == "__main__":
    setup_gemma()