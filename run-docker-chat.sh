#!/bin/bash

# Create local directory for Ollama models if it doesn't exist
MODELS_DIR="${HOME}/.ollama-docker/models"
mkdir -p "$MODELS_DIR"

echo "Building sv-agent Docker image..."
docker build -f Dockerfile.ollama -t sv-agent-ollama .

echo "Starting sv-agent chat with Ollama..."
echo "Models will be stored in: $MODELS_DIR"
echo ""

# Run Docker with volume mount for persistent model storage
docker run -it --rm \
  -v "$MODELS_DIR:/root/.ollama/models" \
  -v "$(pwd)/outputs:/app/outputs" \
  --name sv-agent-chat \
  sv-agent-ollama