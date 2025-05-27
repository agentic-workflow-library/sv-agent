# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

sv-agent is an AWLKit-based agent that wraps the GATK-SV structural variant discovery pipeline. It provides a Python interface to automate complex WDL-based workflows for detecting structural variants in genomic data.

## Key Architecture

### Core Components
- **SVAgent**: Main agent class in `src/sv_agent/agent.py` that inherits from AWLKit's Agent base class
- **WorkflowEngine**: Manages WDL workflow execution (from AWLKit)
- **CLI Interface**: Entry point in `src/sv_agent/main.py` using argparse

### Dependencies
- **awlkit**: Core agentic workflow framework (git submodule)
- **gatk-sv**: Broad Institute's SV discovery pipeline (git submodule) containing WDL workflows

### Pipeline Structure
The GATK-SV pipeline consists of sequential modules:
- Module00a: Sample QC
- Module00b: Evidence Gathering (Manta, MELT, read depth, etc.)
- Module00c: Batch QC
- Module01-06: Clustering, Merging, Filtering, Genotyping, Batch Effects, Annotation

## Development Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run tests
pytest
pytest tests/test_agent.py::TestSVAgent::test_process_batch  # Single test

# Code quality
black src/
flake8 src/
mypy src/

# Run the agent
sv-agent examples/batch1.json --output results/
```

## Testing Approach

Tests use pytest with mocking for external dependencies:
- Mock WorkflowEngine to test agent logic without running actual WDL workflows
- Test files in `tests/` with `test_` prefix
- Coverage reports with `--cov=sv_agent`

## Important Notes

1. **AWLKit Framework**: Located in the awlkit/ submodule, provides WDL to CWL conversion tools:
   - `WDLParser`: Parses WDL files into intermediate representation
   - `CWLWriter`: Generates CWL from intermediate representation
   - `WDLToCWLConverter`: High-level conversion API
   - Install with: `pip install -e awlkit/`

2. **WDL to CWL Conversion**: SVAgent can convert GATK-SV workflows:
   ```python
   agent.convert_gatksv_to_cwl(output_dir, modules=["Module00a"])
   ```

3. **Configuration**: Batch processing requires JSON config with:
   - samples: List of sample objects with id, bam, bai paths
   - reference: Path to reference genome
   - output_dir: Where to write results

4. **GATK-SV Submodule**: Contains 90+ WDL files and Docker configurations. Main entry point is `GATKSVPipelineBatch.wdl`

## AWLKit Development

AWLKit is built incrementally as needed. Current components:
- IR (Intermediate Representation): Language-agnostic workflow model
- Parsers: WDL parser implemented with regex-based approach
- Writers: CWL writer generates v1.2 compliant output
- Converters: WDLToCWLConverter handles file/directory conversion
- Utils: Graph analysis and validation tools

To extend AWLKit:
1. Add new features to existing components as needed
2. Test with GATK-SV WDL files for real-world validation
3. Use `awlkit convert` CLI for testing conversions