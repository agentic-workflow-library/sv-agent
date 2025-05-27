# sv-agent

A Python command-line tool for converting GATK-SV WDL workflows to CWL format and providing expert guidance on structural variant analysis.

## Features

- **WDL to CWL Conversion**: Convert GATK-SV workflows from WDL to CWL format
- **Interactive Chat Interface**: Get expert guidance on SV analysis with natural language
- **LLM Integration**: Support for local (Ollama) and cloud LLMs in air-gapped environments  
- **Workflow Analysis**: Analyze and understand GATK-SV workflow structure
- **Domain Expertise**: Built-in knowledge of GATK-SV modules, best practices, and troubleshooting
- **Command-line Interface**: Simple, focused CLI for all operations

## Installation

```bash
# Clone with submodules
git clone --recursive https://github.com/agentic-workflow-library/sv-agent.git
cd sv-agent

# Run setup script
./setup.sh

# Optional: Install with Ollama support for enhanced chat
pip install -e '.[ollama]'
```

## Usage

### Convert WDL to CWL

```bash
# Convert all GATK-SV workflows
sv-agent convert -o src/sv_agent/cwl

# Convert specific modules
sv-agent convert -o src/sv_agent/cwl -m GatherSampleEvidence Module00a

# Convert with custom input directory
sv-agent convert -i path/to/wdl -o src/sv_agent/cwl
```

### Interactive Expert Chat

The chat interface provides conversational guidance on SV analysis:

```bash
# Start interactive chat (auto-detects available LLM)
sv-agent chat

# Use specific LLM provider
sv-agent chat --llm-provider ollama --ollama-model codellama:13b

# Run without LLM (rule-based only)
sv-agent chat --llm-provider none

# Ask a single question
sv-agent ask "What coverage do I need for SV detection?"

# List available modules
sv-agent list --details
```

**Chat capabilities include:**
- Module explanations and documentation
- Best practices for SV analysis
- Troubleshooting guidance
- Workflow conversion help
- Sample preparation advice

See [docs/chat-interface.md](docs/chat-interface.md) for detailed chat documentation.

### Analyze Workflows

```bash
# Analyze workflow structure
sv-agent analyze GATKSVPipelineBatch

# Output as JSON
sv-agent analyze GATKSVPipelineBatch -f json
```

## Examples

```bash
# Convert Module00a (Sample QC) to CWL
sv-agent convert -o src/sv_agent/cwl -m Module00a

# Get help on troubleshooting low variant calls
sv-agent ask "How do I troubleshoot low SV call counts?"

# Analyze the main GATK-SV pipeline
sv-agent analyze GATKSVPipelineBatch
```

## Python API

```python
from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat

# Initialize agent
agent = SVAgent()

# Convert workflows
results = agent.convert_gatksv_to_cwl(
    output_dir="src/sv_agent/cwl",
    modules=["Module00a", "Module00b"]
)

# Analyze workflow
analysis = agent.analyze_gatksv_workflow("GATKSVPipelineBatch")

# Interactive chat
chat = SVAgentChat(agent)
response = chat.chat("What are the key quality metrics in Module00b?")
print(response)
```

## Air-Gapped LLM Setup

For secure environments without internet access:

```bash
# 1. Install Ollama locally
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull recommended models
ollama pull codellama:13b    # Best for CWL generation
ollama pull llama2:13b       # General SV questions
ollama pull biomistral       # Biomedical context

# 3. Use with sv-agent
sv-agent chat --llm-provider ollama --ollama-model codellama:13b
```

Benefits:
- **Data Privacy**: All processing stays local
- **No Internet Required**: Full functionality offline
- **Fast Response**: No network latency
- **Customizable**: Fine-tune on your data

## Project Structure

```
sv-agent/
├── src/sv_agent/       # Main Python package
│   ├── cwl/            # Generated CWL files
│   ├── llm/            # LLM provider integrations
│   └── prompts/        # Domain knowledge
├── docs/               # Documentation
├── examples/           # Example configurations
├── tests/              # Test suite
├── awlkit/             # AWLKit framework (submodule)
└── gatk-sv/            # GATK-SV pipeline (submodule)
```

## Testing

### Unit Tests
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_llm_chat.py

# Run with coverage
pytest --cov=sv_agent
```

### LLM Integration Tests
```bash
# Setup and run Gemma tests
./tests/test_gemma_setup.sh

# Run integration tests manually
pytest tests/test_llm_chat.py --run-integration

# Test specific model
pytest tests/test_llm_chat.py --run-integration --ollama-model gemma:7b
```

## Performance Tips

For faster chat responses, you can use the Hugging Face Inference API instead of local models:

```bash
# Get a free API token at https://huggingface.co/settings/tokens
export HF_TOKEN="your_token_here"

# Use API mode for instant responses
sv-agent --use-api chat
sv-agent --use-api ask "What is a structural variant?"
```

See [API_SETUP.md](API_SETUP.md) for detailed API configuration options.

## Documentation

- [Chat Interface Guide](docs/chat-interface.md) - Detailed chat documentation
- [Chat Examples](docs/chat-examples.md) - Real-world usage examples
- [API Setup Guide](API_SETUP.md) - Configure API for faster responses
- [AWL Handbook](https://github.com/agentic-workflow-library/awl-handbook) - Framework documentation

## License

MIT License - see LICENSE file for details.