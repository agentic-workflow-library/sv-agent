# API Setup for Fast Performance

The local Gemma model can be slow. Here are options for faster inference using APIs:

## Option 1: Hugging Face Inference API (Recommended)

1. **Get a free API token:**
   - Go to https://huggingface.co/settings/tokens
   - Create a new token with "read" permissions
   - Copy the token (starts with `hf_...`)

2. **Set the token:**
   ```bash
   export HF_TOKEN="your_token_here"
   ```

3. **Use sv-agent with API:**
   ```bash
   # Interactive chat
   sv-agent --use-api chat
   
   # Single question
   sv-agent --use-api ask "What is a structural variant?"
   
   # Use a specific model
   sv-agent --use-api --model "mistralai/Mistral-7B-Instruct-v0.2" ask "What is a genome?"
   ```

## Option 2: OpenAI-Compatible APIs

You can also modify the code to use OpenAI, Anthropic, or other APIs. The HF Inference API provider can be adapted for any API that follows a similar request/response format.

## Option 3: Local Fast Models

If you prefer local models but want better performance:

1. **Use GGUF quantized models with llama.cpp**
2. **Use ONNX models for CPU inference**
3. **Use smaller models like Phi-2 or TinyLlama**

## Free Models (No Auth Required)

Unfortunately, most models on HF Inference API now require authentication. However, with a free account you get:
- 1000 requests/day for most models
- Access to models like Mistral-7B, Llama-2, etc.

## Performance Comparison

- **Local Gemma-2B**: 10-30 seconds per response
- **HF API (Mistral-7B)**: 1-3 seconds per response
- **HF API (Mixtral-8x7B)**: 2-5 seconds per response

The API is 10-30x faster than local inference!