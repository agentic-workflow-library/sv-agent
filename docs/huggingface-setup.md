# Using HuggingFace Transformers with SV-Agent

SV-Agent uses HuggingFace Transformers library for local LLM inference with quantized Google Gemma models by default.

## Installation

Install SV-Agent with HuggingFace support:

```bash
# Install with HuggingFace dependencies
pip install -e ".[huggingface]"

# Or install all LLM providers
pip install -e ".[all]"
```

## Basic Usage

### Ask Command (Single Question)

```bash
# Use default model (Mistral-7B-Instruct)
sv-agent ask "what coverage do i need for sv detection"

# Use a specific model from HuggingFace Hub
sv-agent ask --model "microsoft/phi-2" "explain Module00a"

# Use a local model directory
sv-agent ask --model "/path/to/local/model" "what are structural variants"

# Use Llama 2 (requires HF authentication)
sv-agent ask --model "meta-llama/Llama-2-7b-chat-hf" \
  --auth-token YOUR_HF_TOKEN \
  "what are structural variants"
```

### Interactive Chat Mode

```bash
# Start chat with Gemma (4-bit recommended)
sv-agent --load-in-4bit chat

# Use Gemma 7B for better quality
sv-agent --model models/gemma-7b-it --load-in-4bit chat

# Use Code Llama for technical questions
sv-agent --model "codellama/CodeLlama-7b-Instruct-hf" chat
```

## Available Options

### Model Selection
- `--hf-model-id MODEL_ID`: HuggingFace model ID (default: mistralai/Mistral-7B-Instruct-v0.2)

### Hardware Options
- `--hf-device {cuda,cpu,auto}`: Device to use (default: auto-detect)
- `--hf-load-in-8bit`: Use 8-bit quantization (reduces memory by ~50%)
- `--hf-load-in-4bit`: Use 4-bit quantization (reduces memory by ~75%)

### Authentication & Storage
- `--hf-auth-token TOKEN`: HuggingFace token for gated models (like Llama 2)
- `--hf-cache-dir DIR`: Directory to cache downloaded models

## Recommended Models

### Small Models (< 8GB VRAM)
```bash
# Phi-2 (2.7B parameters) - Fast and efficient
sv-agent chat --llm-provider huggingface --hf-model-id "microsoft/phi-2"

# Mistral 7B with 4-bit quantization
sv-agent chat --llm-provider huggingface \
  --hf-model-id "mistralai/Mistral-7B-Instruct-v0.2" \
  --hf-load-in-4bit
```

### Medium Models (8-16GB VRAM)
```bash
# Mistral 7B - Good balance of speed and quality
sv-agent chat --llm-provider huggingface \
  --hf-model-id "mistralai/Mistral-7B-Instruct-v0.2"

# Llama 2 7B Chat (requires authentication)
sv-agent chat --llm-provider huggingface \
  --hf-model-id "meta-llama/Llama-2-7b-chat-hf" \
  --hf-auth-token YOUR_TOKEN
```

### Code-Focused Models
```bash
# Code Llama 7B - Optimized for technical content
sv-agent chat --llm-provider huggingface \
  --hf-model-id "codellama/CodeLlama-7b-Instruct-hf"
```

## Memory Requirements

| Model | Full Precision | 8-bit | 4-bit |
|-------|---------------|--------|--------|
| Phi-2 (2.7B) | ~6GB | ~3GB | ~2GB |
| Mistral-7B | ~14GB | ~7GB | ~4GB |
| Llama-2-7B | ~14GB | ~7GB | ~4GB |
| Llama-2-13B | ~26GB | ~13GB | ~7GB |

## Getting a HuggingFace Token

Some models (like Llama 2) require authentication:

1. Create a free account at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create a new token with "read" permissions
4. Accept the model's license agreement on its HuggingFace page
5. Use the token with `--auth-token`

## Examples

### Basic SV Analysis
```bash
# Get coverage recommendations
sv-agent ask "what coverage do I need for reliable SV detection"

# Understand pipeline modules
sv-agent ask "explain the purpose of Module00a in GATK-SV"
```

### Interactive Workflow Conversion
```bash
# Start interactive session with 4-bit quantization
sv-agent chat --load-in-4bit

> You: I need to convert Module00b to CWL format
> SV-Agent: I'll help you convert Module00b (Manta SV calling) to CWL...

> You: What quality filters should I apply?
> SV-Agent: For GATK-SV, I recommend these quality filters...
```

### Troubleshooting with AI
```bash
# Get help with low SV calls using Code Llama
sv-agent ask --model "codellama/CodeLlama-7b-Instruct-hf" \
  "why am I getting very few SV calls from my 30x WGS data"
```

## Performance Tips

1. **Use quantization** for larger models:
   ```bash
   sv-agent chat --llm-provider huggingface --hf-load-in-4bit
   ```

2. **Cache models** to avoid re-downloading:
   ```bash
   sv-agent chat --llm-provider huggingface \
     --hf-cache-dir ~/.cache/huggingface
   ```

3. **Start with smaller models** like Phi-2 or Mistral-7B

4. **Use GPU if available** - automatically detected, or specify:
   ```bash
   sv-agent chat --llm-provider huggingface --hf-device cuda
   ```

## Troubleshooting

### Out of Memory
- Use `--hf-load-in-4bit` or `--hf-load-in-8bit`
- Try a smaller model
- Use CPU with `--hf-device cpu` (slower but works)

### Model Download Issues
- Check your internet connection
- Verify HF token for gated models
- Use `--hf-cache-dir` to specify download location

### Slow Generation
- Ensure you're using GPU if available
- Use a smaller model
- Enable quantization

## Using Local Model Files

You can use locally downloaded models:

```bash
# Use a model from a local directory
sv-agent chat --model /path/to/model/directory

# Example with a downloaded Llama model
sv-agent chat --model ~/models/llama-2-7b-chat

# Use with quantization
sv-agent chat --model /path/to/model --load-in-4bit
```

Local models should contain:
- `config.json` - Model configuration
- `tokenizer.json` or `tokenizer_config.json` - Tokenizer files  
- Model weights (`.bin` or `.safetensors` files)