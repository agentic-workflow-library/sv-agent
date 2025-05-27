# sv-agent

A Python command-line tool for converting GATK-SV WDL workflows to CWL format and providing expert guidance on structural variant analysis.

## Features

- **WDL to CWL Conversion**: Convert GATK-SV workflows from WDL to CWL format
- **Expert SV Guidance**: Interactive chat with domain expertise in structural variant analysis
- **Workflow Analysis**: Analyze and understand GATK-SV workflow structure
- **Command-line Interface**: Simple, focused CLI for all operations

## Installation

```bash
# Clone with submodules
git clone --recursive https://github.com/agentic-workflow-library/sv-agent.git
cd sv-agent

# Install dependencies
pip install -e .
pip install -e awlkit/
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

### Interactive Expert Guidance

```bash
# Start interactive chat
sv-agent chat

# Ask a single question
sv-agent ask "What coverage do I need for SV detection?"

# List available modules
sv-agent list --details
```

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

agent = SVAgent()

# Convert workflows
results = agent.convert_gatksv_to_cwl(
    output_dir="src/sv_agent/cwl",
    modules=["Module00a", "Module00b"]
)

# Analyze workflow
analysis = agent.analyze_gatksv_workflow("GATKSVPipelineBatch")
```

## Project Structure

```
sv-agent/
├── src/sv_agent/       # Main Python package
│   └── cwl/            # Generated CWL files
├── docs/               # Documentation
├── examples/           # Example configurations
├── tests/              # Test suite
├── awlkit/             # AWLKit framework (submodule)
└── gatk-sv/            # GATK-SV pipeline (submodule)
```

## Documentation

For comprehensive documentation, see the [AWL Handbook](https://github.com/agentic-workflow-library/awl-handbook).

## License

MIT License - see LICENSE file for details.