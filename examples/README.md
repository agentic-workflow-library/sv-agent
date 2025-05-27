# SV-Agent Examples

This directory contains example notebooks and scripts demonstrating sv-agent's capabilities for structural variant analysis using GATK-SV.

## Notebooks

### 1. `sv_agent_chat_demo.ipynb`
Interactive demonstration of sv-agent's chat interface, including:
- Basic rule-based chat (no LLM required)
- LLM-enhanced chat with Ollama/Gemma
- Module information and explanations
- Best practices guidance
- Troubleshooting common issues
- Interactive Q&A examples

### 2. `sv_agent_cwl_execution_demo.ipynb`
Comprehensive guide to executing CWL workflows with sv-agent:
- Converting WDL to CWL format
- Preparing input configurations
- Running GATK-SV analysis
- Batch processing examples
- Trio analysis configuration
- Performance optimization

### 3. `sv_agent_demo.ipynb`
Original demo notebook showing:
- Basic sv-agent usage
- Workflow conversion examples
- Simple chat interactions

## Python Scripts

### `test_gemma_chat.py`
Tests sv-agent chat with Gemma model via Ollama:
```bash
python test_gemma_chat.py
```

### `ollama_usage.py`
Demonstrates Ollama integration for air-gapped environments:
```bash
python ollama_usage.py
```

### `convert_gatksv_module.py`
Example of programmatic WDL to CWL conversion:
```bash
python convert_gatksv_module.py
```

## Configuration Files

### `batch1.json`
Sample batch configuration for multiple samples:
```json
{
  "samples": [
    {"id": "sample1", "bam": "path/to/bam", "bai": "path/to/bai"}
  ],
  "reference": "/path/to/reference.fa",
  "output_dir": "/path/to/output"
}
```

## Quick Start

1. **Install sv-agent**:
   ```bash
   pip install -e ..
   pip install -e ../awlkit/
   ```

2. **Run Jupyter notebooks**:
   ```bash
   jupyter notebook sv_agent_chat_demo.ipynb
   ```

3. **Try the chat interface**:
   ```bash
   sv-agent chat
   ```

4. **Convert and run a workflow**:
   ```bash
   # Convert WDL to CWL
   sv-agent convert -o cwl_output -m Module00a
   
   # Run the CWL workflow
   sv-agent run cwl_output/GatherSampleEvidence.cwl inputs.yaml
   ```

## Key Concepts

- **sv-agent executes CWL workflows** for running GATK-SV analysis
- Converts WDL to CWL for compatibility
- Provides expert guidance through chat interface
- Supports both rule-based and LLM-enhanced interactions
- Designed for genomic data processing in secure environments

## Resources

- [GATK-SV Documentation](https://github.com/broadinstitute/gatk-sv)
- [CWL Specification](https://www.commonwl.org/)
- [sv-agent Documentation](../docs/)
- [Chat Interface Guide](../docs/chat-interface.md)