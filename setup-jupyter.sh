#!/bin/bash

echo "Setting up JupyterLab environment for sv-agent..."

# Install JupyterLab and useful extensions
pip install jupyterlab ipywidgets jupyter-ai

# Install sv-agent and its dependencies
pip install -e .
pip install -e submodules/awlkit/

# Install optional dependencies for better notebook experience
pip install -e '.[ollama,openai,anthropic]'

# Install additional useful packages for notebooks
pip install pandas matplotlib seaborn plotly

echo ""
echo "JupyterLab setup complete!"
echo ""
echo "To start JupyterLab, run:"
echo "  jupyter lab --ip=0.0.0.0 --allow-root --no-browser"
echo ""
echo "Then open the URL shown in your browser."