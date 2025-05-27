# SV-Agent

An AWLKit-based agent for automating the GATK-SV structural variant discovery pipeline. SV-Agent provides a Python interface to GATK-SV workflows and includes tools for converting WDL workflows to CWL format.

## Features

- **Automated Pipeline Execution**: Run GATK-SV workflows with simple Python commands
- **WDL to CWL Conversion**: Convert GATK-SV WDL workflows to CWL format using AWLKit
- **Workflow Analysis**: Analyze workflow structure, dependencies, and complexity
- **Batch Processing**: Process multiple samples through the SV pipeline
- **Modular Architecture**: Work with individual GATK-SV modules or the complete pipeline

## Installation

```bash
# Clone with submodules
git clone --recursive https://github.com/YOUR_USERNAME/sv-agent.git
cd sv-agent

# Install sv-agent
pip install -e .

# Install AWLKit
pip install -e awlkit/

# Install development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Interactive Chat

SV-Agent is a domain-specific agent that can answer questions about structural variant analysis:

```bash
# Start interactive chat
sv-agent chat

# Ask a single question
sv-agent ask "What coverage do I need for SV detection?"
```

### Using in Python/Jupyter

```python
from sv_agent import create_agent

# Create the agent
agent = create_agent()

# Ask questions
agent.ask("What are structural variants?")
agent.ask("Explain Module00a")

# Show GATK-SV modules
agent.show_modules()

# Get best practices
agent.best_practices("sample selection")
```

### Command Line Operations

```bash
# Process a batch of samples
sv-agent process examples/batch1.json --output results/

# Convert WDL to CWL
sv-agent convert --output cwl_output --modules Module00a Module00b

# Analyze workflow
sv-agent analyze GATKSVPipelineBatch
```

### Converting WDL to CWL

```python
from sv_agent import SVAgent

agent = SVAgent()

# Convert specific GATK-SV modules
results = agent.convert_gatksv_to_cwl(
    output_dir=Path("cwl_output"),
    modules=["Module00a", "Module00b"]
)

# Analyze workflow structure
analysis = agent.analyze_gatksv_workflow("GATKSVPipelineBatch")
```

## Project Structure

```
sv-agent/
├── awlkit/                  # AWLKit framework (submodule)
│   └── src/awlkit/         # WDL/CWL conversion tools
├── gatk-sv/                # GATK-SV pipeline (submodule)
│   └── wdl/                # WDL workflow definitions
├── src/sv_agent/           # Main agent implementation
├── tests/                  # Test suite
├── examples/               # Example configurations
└── docs/                   # Additional documentation
```

## Documentation

- [AWL Handbook](awl-handbook/) - Comprehensive documentation for AWLKit and AWL ecosystem
- [AWLKit Development](AWLKIT_DEVELOPMENT.md) - Guide for extending AWLKit  
- [GATK-SV Documentation](https://github.com/broadinstitute/gatk-sv) - Official GATK-SV docs

## Development

```bash
# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
