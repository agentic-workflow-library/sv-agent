# Setting up Gemma for SV-Agent

## Quick Setup

1. **Run the setup script:**
```bash
python setup_gemma.py
```

2. **Follow the prompts:**
   - Choose Gemma 2B (recommended) or 7B
   - Enter your HuggingFace token when prompted
   - The script will download and configure the model

3. **Start using SV-Agent:**
```bash
# Gemma will be used by default after setup
sv-agent --load-in-4bit ask "What coverage do I need for SV detection?"
```

## Getting a HuggingFace Token

1. Create account at https://huggingface.co
2. Go to https://huggingface.co/google/gemma-2b-it
3. Accept the license agreement
4. Go to Settings → Access Tokens
5. Create a token with "read" permissions
6. Use this token when running setup_gemma.py

## Model Locations

After setup:
- Models are stored in `./models/`
- Default model symlink: `./models/gemma-latest`
- Config file: `./models/default_model.txt`

## Usage Examples

```bash
# Ask questions (uses Gemma by default)
sv-agent --load-in-4bit ask "Explain Module00a"

# Interactive chat
sv-agent --load-in-4bit chat

# Use 8-bit quantization (more memory, better quality)
sv-agent --load-in-8bit chat

# Explicitly specify model
sv-agent --model models/gemma-2b-it --load-in-4bit chat
```

## Memory Requirements

| Model | Full | 8-bit | 4-bit |
|-------|------|-------|-------|
| Gemma 2B | ~5GB | ~2.5GB | ~1.5GB |
| Gemma 7B | ~17GB | ~8GB | ~4GB |

**Recommendation:** Use 4-bit quantization for best balance of quality and memory usage.