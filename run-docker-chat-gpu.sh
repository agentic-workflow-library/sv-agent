#!/bin/bash

# Create local directory for Ollama models if it doesn't exist
MODELS_DIR="${HOME}/.ollama-docker/models"
mkdir -p "$MODELS_DIR"

echo "Building sv-agent Docker image..."
docker build -f Dockerfile.ollama -t sv-agent-ollama .

# Check if nvidia-docker is available
if command -v nvidia-smi &> /dev/null && docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "GPU support detected! Running with GPU acceleration..."
    echo "Models will be stored in: $MODELS_DIR"
    echo ""
    
    # Run Docker with GPU support
    docker run -it --rm \
      --gpus all \
      -v "$MODELS_DIR:/root/.ollama/models" \
      -v "$(pwd)/outputs:/app/outputs" \
      --name sv-agent-chat \
      sv-agent-ollama
else
    echo "No GPU support detected. Running on CPU..."
    echo "Models will be stored in: $MODELS_DIR"
    echo ""
    echo "To enable GPU support, install:"
    echo "  - NVIDIA drivers"
    echo "  - NVIDIA Container Toolkit"
    echo ""
    
    # Run Docker without GPU
    docker run -it --rm \
      -v "$MODELS_DIR:/root/.ollama/models" \
      -v "$(pwd)/outputs:/app/outputs" \
      --name sv-agent-chat \
      sv-agent-ollama
fi