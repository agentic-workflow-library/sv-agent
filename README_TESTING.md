# Testing SV-Agent with HuggingFace

This version of sv-agent has been refactored to use only HuggingFace Transformers for LLM functionality.

## Key Changes

1. **Removed all Ollama references** - No longer requires a separate server
2. **Simplified CLI** - Model specification is now straightforward
3. **Support for local models** - Can load models from local directories
4. **Lazy imports** - Transformers only imported when needed

## Installation

```bash
# Basic installation (without transformers)
pip install -e .

# With HuggingFace support
pip install -e ".[huggingface]"
```

## Basic Usage

```bash
# List available modules (works without transformers)
sv-agent list

# Get help
sv-agent --help

# Setup Gemma model (one-time):
python setup_gemma.py

# With transformers installed and Gemma downloaded:

# Use Gemma (if downloaded, will be default)
sv-agent ask "What coverage do I need for SV detection?"

# Use Gemma with 4-bit quantization (recommended)
sv-agent --load-in-4bit ask "Explain Module00a"

# Use local Gemma model explicitly
sv-agent --model models/gemma-latest ask "What are structural variants?"

# Interactive chat with Gemma
sv-agent --load-in-4bit chat

# Use a different model from HuggingFace
sv-agent --model "microsoft/phi-2" chat

# Use 8-bit quantization
sv-agent --load-in-8bit chat
```

## Model Options

- `--model MODEL_PATH`: HuggingFace model ID or local path
- `--device {cuda,cpu,auto}`: Device for inference
- `--load-in-8bit`: 8-bit quantization
- `--load-in-4bit`: 4-bit quantization  
- `--auth-token TOKEN`: For gated models
- `--cache-dir DIR`: Model cache directory

## Testing

Run the test script:

```bash
python test_huggingface_only.py
```

This verifies:
1. Basic commands work without transformers
2. Proper error messages when transformers not installed
3. Correct argument parsing