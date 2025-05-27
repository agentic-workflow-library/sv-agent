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

# Create output directory
mkdir -p outputs

echo "Setup complete!"
echo ""
echo "You can now use sv-agent:"
echo "  sv-agent convert -o outputs/cwl"
echo "  sv-agent chat"
echo "  sv-agent list"