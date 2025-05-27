# sv-agent Installation Guide

## Overview

sv-agent can be installed in several ways depending on your needs:
- Quick setup using the provided script
- Manual installation with pip
- Development installation
- Docker container (coming soon)

## Prerequisites

- Python 3.8 or higher
- Git (for cloning with submodules)
- pip package manager
- Optional: cwltool for workflow execution
- Optional: Ollama for enhanced chat capabilities

## Quick Installation

### 1. Clone with Submodules

```bash
# Clone the repository with all submodules
git clone --recursive https://github.com/agentic-workflow-library/sv-agent.git
cd sv-agent
```

### 2. Run Setup Script

```bash
# Make setup script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

This script will:
- Initialize git submodules (awlkit, gatk-sv, awl-handbook)
- Install sv-agent in editable mode
- Install awlkit dependency
- Check for optional components (Ollama)
- Create output directories

## Manual Installation

### 1. Clone Repository

```bash
git clone https://github.com/agentic-workflow-library/sv-agent.git
cd sv-agent

# Initialize submodules
git submodule update --init --recursive
```

### 2. Install Dependencies

```bash
# Install sv-agent in editable mode
pip install -e .

# Install awlkit dependency
pip install -e submodules/awlkit/

# Optional: Install with LLM support
pip install -e '.[ollama]'      # For Ollama support
pip install -e '.[openai]'       # For OpenAI support
pip install -e '.[anthropic]'    # For Anthropic support
pip install -e '.[all]'          # For all LLM providers
```

### 3. Install Execution Engines (Optional)

For workflow execution capabilities:

```bash
# Install cwltool
pip install cwltool

# Or install Toil for scalable execution
pip install toil[cwl]
```

## Development Installation

For developers who want to contribute:

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/sv-agent.git
cd sv-agent
git submodule update --init --recursive

# Install in development mode with all extras
pip install -e '.[dev,all]'

# Install pre-commit hooks (optional)
pre-commit install
```

## Installation Options

### Base Installation

The base installation includes:
- WDL to CWL conversion
- Workflow analysis
- Basic chat interface (rule-based)
- CLI commands

### Optional Components

#### 1. LLM Providers

```bash
# Ollama (local LLMs)
pip install -e '.[ollama]'

# OpenAI (GPT models)
pip install -e '.[openai]'
export OPENAI_API_KEY=your-key-here

# Anthropic (Claude models)
pip install -e '.[anthropic]'
export ANTHROPIC_API_KEY=your-key-here

# All providers
pip install -e '.[all]'
```

#### 2. Ollama Setup

For enhanced local LLM chat:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull llama2:13b          # General purpose
ollama pull codellama:13b       # Code/CWL generation
ollama pull biomistral           # Biomedical text

# Verify installation
ollama list
```

#### 3. Workflow Execution

```bash
# cwltool (reference implementation)
pip install cwltool

# Seven Bridges CLI
pip install sevenbridges-python
sb configure  # Follow prompts to set up credentials
```

## Verify Installation

```bash
# Check sv-agent is installed
sv-agent --help

# Check version
sv-agent --version  # Note: version command may need to be added

# List available commands
sv-agent

# Test conversion
sv-agent list  # Should show GATK-SV modules

# Test chat (rule-based)
sv-agent chat --llm-provider none

# Check execution engines
python -c "from awlkit.execution import LocalRunner; print(LocalRunner.list_available_engines())"
```

## Environment Configuration

### Required PYTHONPATH

Since awlkit is a submodule, you may need to set PYTHONPATH:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PYTHONPATH="${PYTHONPATH}:${SV_AGENT_DIR}/submodules/awlkit/src"
```

### Optional Environment Variables

```bash
# LLM API Keys
export OPENAI_API_KEY=your-openai-key
export ANTHROPIC_API_KEY=your-anthropic-key

# Seven Bridges
export SB_AUTH_TOKEN=your-sb-token

# Ollama (if not using default localhost:11434)
export OLLAMA_HOST=http://your-ollama-server:11434
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'awlkit'**
   ```bash
   # Ensure submodules are initialized
   git submodule update --init --recursive
   
   # Install awlkit
   pip install -e submodules/awlkit/
   ```

2. **Command 'sv-agent' not found**
   ```bash
   # Reinstall sv-agent
   pip install -e .
   
   # Or add to PATH
   export PATH="${PATH}:${HOME}/.local/bin"
   ```

3. **Git submodule errors**
   ```bash
   # Reset submodules
   git submodule deinit -f .
   git submodule update --init --recursive
   ```

4. **LLM provider not available**
   ```bash
   # Check Ollama is running
   ollama list
   
   # Start Ollama service
   ollama serve
   ```

## Uninstallation

```bash
# Uninstall sv-agent
pip uninstall sv-agent

# Uninstall awlkit
pip uninstall awlkit

# Remove cloned directory
cd ..
rm -rf sv-agent
```

## Next Steps

After installation:
1. Run `sv-agent list` to see available modules
2. Try `sv-agent chat` for interactive guidance
3. Convert your first workflow with `sv-agent convert`
4. See [CLI_REFERENCE.md](CLI_REFERENCE.md) for all commands