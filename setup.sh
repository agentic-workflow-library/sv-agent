#!/bin/bash
# Setup script for sv-agent

echo "Setting up sv-agent..."

# Check if submodules are initialized
if [ ! -f "awlkit/setup.py" ]; then
    echo "Initializing submodules..."
    git submodule update --init --recursive
fi

# Install dependencies
echo "Installing dependencies..."
pip install -e .
pip install -e awlkit/

# Optional: Install Ollama support
echo ""
echo "For enhanced chat capabilities with Ollama (optional):"
echo "  pip install -e '.[ollama]'"
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    echo ""
    echo "Recommended models for SV analysis:"
    echo "  - codellama:13b (best for code/CWL generation)"
    echo "  - llama2:13b (general purpose)"
    echo "  - biomistral (biomedical text)"
    echo ""
    echo "To pull a model: ollama pull codellama:13b"
else
    echo "ℹ Ollama not found. To use local LLMs:"
    echo "  1. Install Ollama: https://ollama.ai"
    echo "  2. Pull a model: ollama pull llama2:13b"
    echo "  3. Run: sv-agent chat --llm-provider ollama"
fi

# Create output directory
mkdir -p outputs

echo ""
echo "Setup complete!"
echo ""
echo "You can now use sv-agent:"
echo "  sv-agent convert -o src/sv_agent/cwl"
echo "  sv-agent chat"
echo "  sv-agent chat --llm-provider ollama --ollama-model codellama:13b"
echo "  sv-agent list"