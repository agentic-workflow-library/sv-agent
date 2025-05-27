# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

sv-agent is a domain-specific agent that provides:
1. WDL to CWL conversion for GATK-SV workflows 
2. Expert guidance on structural variant analysis
3. Interactive CLI for workflow conversion and SV analysis questions

## Key Architecture

### Core Components
- **SVAgent** (`src/sv_agent/agent.py`): Main agent class inheriting from AWLKit's Agent base
- **SVAgentChat** (`src/sv_agent/chat.py`): Interactive chat interface for SV expertise
- **SVKnowledgeBase** (`src/sv_agent/knowledge.py`): Domain knowledge about GATK-SV modules
- **CLI** (`src/sv_agent/main.py`): Argparse-based CLI with subcommands: convert, analyze, chat, ask, list

### Dependencies (Git Submodules)
- **awlkit/**: Core agentic workflow framework providing WDL/CWL conversion capabilities
- **gatk-sv/**: Broad Institute's structural variant discovery pipeline (90+ WDL files)

### GATK-SV Pipeline Structure
Sequential modules for SV discovery:
- Module00a-c: Sample QC, Evidence Gathering (Manta, MELT, read depth), Batch QC
- Module01-06: Clustering, Merging, Filtering, Genotyping, Batch Effects, Annotation

## Development Commands

```bash
# Initial setup (includes submodules)
./setup.sh

# Manual installation
git submodule update --init --recursive
pip install -e .
pip install -e awlkit/

# Run tests
pytest
pytest tests/test_agent.py::TestSVAgent::test_process_batch  # Single test
pytest --cov=sv_agent  # With coverage

# Code quality
black src/
flake8 src/
mypy src/

# CLI usage
sv-agent convert -o outputs/cwl  # Convert all workflows
sv-agent convert -o outputs/cwl -m GatherSampleEvidence Module00a  # Specific modules
sv-agent analyze GATKSVPipelineBatch  # Analyze workflow structure
sv-agent chat  # Interactive chat
sv-agent ask "What coverage do I need for SV detection?"  # Single question
sv-agent list --details  # List available modules
```

## Testing Strategy

- Tests use pytest with mocking for external dependencies
- Mock WorkflowEngine to test agent logic without running actual WDL workflows
- Test files in `tests/` directory with `test_` prefix
- Key test classes: TestSVAgent, TestSVAgentChat

## AWLKit Integration

AWLKit (in awlkit/ submodule) provides workflow conversion infrastructure:
- **WDLParser**: Parses WDL files into intermediate representation
- **CWLWriter**: Generates CWL v1.2 compliant output  
- **WDLToCWLConverter**: High-level conversion API
- **IR**: Language-agnostic workflow model

Usage:
```python
from sv_agent import SVAgent
agent = SVAgent()
results = agent.convert_gatksv_to_cwl(output_dir="outputs/cwl", modules=["Module00a"])
```

## Configuration Format

Batch processing configuration (JSON):
```json
{
  "samples": [{"id": "sample1", "bam": "path/to/bam", "bai": "path/to/bai"}],
  "reference": "/path/to/reference.fa",
  "output_dir": "/path/to/output"
}
```

## Important Implementation Details

1. **Conversion Process**: 
   - Searches for WDL files in gatk-sv/wdl/
   - Converts to CWL using AWLKit's converter
   - Outputs to specified directory preserving structure

2. **Knowledge Base**:
   - Embedded SV expertise in prompts/gatksv.txt
   - Module descriptions in SVKnowledgeBase class
   - Context-aware responses based on GATK-SV documentation

3. **Error Handling**:
   - Graceful failure for individual file conversions
   - Detailed error reporting in conversion summaries
   - Validation optional via --validate flag