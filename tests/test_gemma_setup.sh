#!/bin/bash
# Setup script for testing sv-agent with Gemma model

echo "Setting up Gemma model for sv-agent testing..."
echo "=============================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed!"
    echo ""
    echo "Please install Ollama first:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Failed to start Ollama"
        exit 1
    fi
    echo "✅ Ollama started (PID: $OLLAMA_PID)"
else
    echo "✅ Ollama is running"
fi

# Check available models
echo ""
echo "Checking available models..."
MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

# Check for Gemma models
GEMMA_2B=$(echo "$MODELS" | grep -c "gemma:2b")
GEMMA_7B=$(echo "$MODELS" | grep -c "gemma:7b")

if [ $GEMMA_2B -eq 0 ] && [ $GEMMA_7B -eq 0 ]; then
    echo "⚠️  No Gemma models found. Pulling gemma:2b..."
    echo "This may take a few minutes..."
    
    if ollama pull gemma:2b; then
        echo "✅ Successfully pulled gemma:2b"
    else
        echo "❌ Failed to pull gemma:2b"
        echo "You can try manually: ollama pull gemma:2b"
        exit 1
    fi
else
    echo "✅ Gemma model available:"
    [ $GEMMA_2B -gt 0 ] && echo "  - gemma:2b"
    [ $GEMMA_7B -gt 0 ] && echo "  - gemma:7b"
fi

# Run tests
echo ""
echo "Running sv-agent LLM tests..."
echo "============================="

# Run unit tests (mocked)
echo ""
echo "1. Running unit tests (mocked LLM)..."
pytest tests/test_llm_chat.py -v -k "not integration"

# Ask if user wants to run integration tests
echo ""
echo "2. Integration tests require Ollama to be running with Gemma model."
read -p "Run integration tests? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running integration tests with Gemma..."
    pytest tests/test_llm_chat.py -v --run-integration -k "integration"
else
    echo "Skipping integration tests."
    echo "You can run them later with:"
    echo "  pytest tests/test_llm_chat.py --run-integration"
fi

# Test the chat interface manually
echo ""
echo "3. Manual test of chat interface"
echo "================================"
echo "You can test the chat interface with:"
echo ""
echo "  # With Gemma (if available):"
echo "  sv-agent chat --llm-provider ollama --ollama-model gemma:2b"
echo ""
echo "  # Without LLM (rule-based):"
echo "  sv-agent chat --llm-provider none"
echo ""
echo "Example questions to try:"
echo "  - What is a structural variant?"
echo "  - Explain Module00a"
echo "  - What coverage do I need for SV detection?"
echo "  - How do I troubleshoot low variant calls?"

# Cleanup message
if [ ! -z "$OLLAMA_PID" ]; then
    echo ""
    echo "Note: Ollama was started by this script (PID: $OLLAMA_PID)"
    echo "You may want to stop it when done: kill $OLLAMA_PID"
fi