#!/usr/bin/env python3
"""Download quantized Gemma model for SV-Agent."""

import os
import sys
from pathlib import Path

def download_gemma():
    """Download quantized Gemma model using HuggingFace Hub."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Error: huggingface_hub not installed.")
        print("Install with: pip install huggingface_hub")
        sys.exit(1)
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Quantized Gemma models available
    models = {
        "gemma-2b-it-q4": "google/gemma-2b-it",  # 2B instruction-tuned
        "gemma-2b-it-q8": "google/gemma-2b-it",  # 2B instruction-tuned 
        "gemma-7b-it-q4": "google/gemma-7b-it",  # 7B instruction-tuned
    }
    
    # For quantized models, we'll use community versions
    quantized_models = {
        "gemma-2b-it-q4": "TheBloke/gemma-2b-it-GGUF",
        "gemma-2b-it-q8": "TheBloke/gemma-2b-it-GGUF",
        "gemma-7b-it-q4": "TheBloke/gemma-7b-it-GGUF",
    }
    
    print("Available Gemma models:")
    print("1. gemma-2b-it-q4 - Gemma 2B Instruct 4-bit (~1.5GB)")
    print("2. gemma-2b-it-q8 - Gemma 2B Instruct 8-bit (~2.5GB)")
    print("3. gemma-7b-it-q4 - Gemma 7B Instruct 4-bit (~4GB)")
    
    choice = input("\nSelect model (1-3) [default: 1]: ").strip() or "1"
    
    model_map = {
        "1": "gemma-2b-it-q4",
        "2": "gemma-2b-it-q8", 
        "3": "gemma-7b-it-q4",
    }
    
    if choice not in model_map:
        print("Invalid choice")
        sys.exit(1)
    
    model_name = model_map[choice]
    
    # For standard transformers format (not GGUF), use the original models
    # We'll download the standard format for compatibility with transformers
    print(f"\nDownloading {model_name}...")
    
    # Use the original Google model for transformers compatibility
    model_id = models[model_name]
    local_dir = models_dir / model_name.replace("-q4", "").replace("-q8", "")
    
    print(f"Model ID: {model_id}")
    print(f"Destination: {local_dir}")
    
    # Check if we need auth token for Gemma
    auth_token = os.getenv("HF_TOKEN")
    if not auth_token:
        print("\nNote: Gemma models require accepting the license agreement.")
        print("1. Go to https://huggingface.co/{model_id}")
        print("2. Accept the license agreement")
        print("3. Get your token from https://huggingface.co/settings/tokens")
        auth_token = input("\nEnter your HuggingFace token (or set HF_TOKEN env var): ").strip()
        
        if not auth_token:
            print("Token required for Gemma models")
            sys.exit(1)
    
    try:
        # Download the model
        snapshot_download(
            repo_id=model_id,
            local_dir=str(local_dir),
            token=auth_token,
            ignore_patterns=["*.gguf", "*.ggml"],  # Skip GGUF files if any
        )
        
        print(f"\n✓ Model downloaded to: {local_dir}")
        print("\nTo use this model:")
        print(f"sv-agent --model {local_dir} chat")
        print(f"sv-agent --model {local_dir} --load-in-4bit chat  # For 4-bit quantization")
        print(f"sv-agent --model {local_dir} ask \"What coverage do I need?\"")
        
        # Create a symlink for convenience
        latest_link = models_dir / "gemma-latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(local_dir.name)
        print(f"\n✓ Created symlink: {latest_link} -> {local_dir.name}")
        print("\nYou can also use: sv-agent --model models/gemma-latest chat")
        
    except Exception as e:
        print(f"\nError downloading model: {e}")
        if "401" in str(e):
            print("\nAuthentication failed. Please check:")
            print("1. You have accepted the Gemma license agreement")
            print("2. Your token is valid")
        sys.exit(1)

if __name__ == "__main__":
    download_gemma()