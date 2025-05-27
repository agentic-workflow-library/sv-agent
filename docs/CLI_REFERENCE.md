# sv-agent Command Line Reference

## Overview

sv-agent is a command-line tool for converting GATK-SV WDL workflows to CWL and providing SV analysis expertise.

## Global Options

```bash
sv-agent [OPTIONS] COMMAND [ARGS]
```

### Options:
- `-v, --verbose` - Enable verbose logging
- `--llm-provider {ollama,openai,anthropic,auto,none}` - LLM provider to use (default: auto)
- `--ollama-model MODEL` - Ollama model to use (default: llama2:13b)
- `--ollama-url URL` - Ollama API URL (default: http://localhost:11434)

## Commands

### 1. convert - Convert WDL to CWL

Convert GATK-SV WDL workflows to CWL format.

```bash
sv-agent convert [OPTIONS]
```

**Options:**
- `-i, --input PATH` - Input directory containing WDL files (default: gatk-sv/wdl)
- `-o, --output PATH` - Output directory for CWL files (default: src/sv_agent/cwl)
- `-m, --modules MODULE [MODULE...]` - Specific modules to convert
- `--validate` - Validate generated CWL files

**Examples:**
```bash
# Convert all workflows
sv-agent convert -o output/cwl

# Convert specific modules
sv-agent convert -m GatherSampleEvidence Module00a -o output/cwl

# Convert with validation
sv-agent convert --validate -o output/cwl

# Convert from custom input directory
sv-agent convert -i /path/to/wdl -o output/cwl
```

### 2. analyze - Analyze Workflow Structure

Analyze GATK-SV workflow structure and dependencies.

```bash
sv-agent analyze WORKFLOW [OPTIONS]
```

**Arguments:**
- `WORKFLOW` - Workflow name to analyze (without .wdl extension)

**Options:**
- `-f, --format {json,text}` - Output format (default: text)

**Examples:**
```bash
# Analyze a workflow in text format
sv-agent analyze GATKSVPipelineBatch

# Analyze with JSON output
sv-agent analyze GatherSampleEvidence -f json

# Analyze Module00a
sv-agent analyze Module00a
```

### 3. chat - Interactive Chat

Start an interactive chat session for SV analysis guidance.

```bash
sv-agent chat [OPTIONS]
```

**Options:**
- `--no-banner` - Skip welcome banner

**Examples:**
```bash
# Start chat with auto-detected LLM
sv-agent chat

# Start chat with Ollama
sv-agent chat --llm-provider ollama

# Start chat with specific Ollama model
sv-agent chat --llm-provider ollama --ollama-model codellama:13b

# Start chat without LLM (rule-based only)
sv-agent chat --llm-provider none
```

### 4. ask - Ask a Single Question

Ask a single question about SV analysis without entering chat mode.

```bash
sv-agent ask QUESTION
```

**Arguments:**
- `QUESTION` - Your question (can be multiple words)

**Examples:**
```bash
# Ask about coverage requirements
sv-agent ask "What coverage do I need for SV detection?"

# Ask about specific modules
sv-agent ask "What does Module00a do?"

# Ask about SV types
sv-agent ask "What is a deletion in genomics?"

# Ask about best practices
sv-agent ask "Should I include related samples in my cohort?"
```

### 5. list - List Available Modules

List all available GATK-SV modules.

```bash
sv-agent list [OPTIONS]
```

**Options:**
- `--details` - Show detailed information about each module

**Examples:**
```bash
# List all modules (simple)
sv-agent list

# List with detailed descriptions
sv-agent list --details
```

### 6. run - Execute CWL Workflows

Execute CWL workflows using integrated execution engines (cwltool or Seven Bridges).

```bash
sv-agent run WORKFLOW INPUTS [OPTIONS]
```

**Arguments:**
- `WORKFLOW` - Path to CWL workflow file
- `INPUTS` - Path to inputs YAML/JSON file

**Options:**
- `-o, --output-dir PATH` - Output directory (default: current directory)
- `--no-container` - Run without container (Docker/Singularity)
- `--singularity` - Use Singularity instead of Docker
- `--podman` - Use Podman instead of Docker
- `--engine {auto,cwltool,sevenbridges}` - Execution engine to use (default: auto)
- `--sb-project PROJECT_ID` - Seven Bridges project ID (for sevenbridges engine)

**Examples:**
```bash
# Run with auto-detected engine (cwltool if available)
sv-agent run workflow.cwl inputs.yaml

# Run with specific output directory
sv-agent run workflow.cwl inputs.yaml -o results/

# Run without Docker containers
sv-agent run workflow.cwl inputs.yaml --no-container

# Run with Singularity
sv-agent run workflow.cwl inputs.yaml --singularity

# Run on Seven Bridges Platform
sv-agent run workflow.cwl inputs.yaml --engine sevenbridges --sb-project my-project-id

# Run a converted GATK-SV module
sv-agent run cwl_output/GatherSampleEvidence.cwl sample_inputs.yaml -o results/
```

## Common Use Cases

### 1. Complete Pipeline Conversion
```bash
# Convert entire GATK-SV pipeline to CWL
sv-agent convert -i submodules/gatk-sv/wdl -o cwl_output --validate
```

### 2. Module-by-Module Conversion
```bash
# Convert sample processing modules
sv-agent convert -m Module00a Module00b Module00c -o cwl_output
```

### 3. Interactive Analysis Session
```bash
# Start chat with Ollama for comprehensive analysis
sv-agent chat --llm-provider ollama --ollama-model codellama:13b
```

### 4. Quick Information Lookup
```bash
# Get quick answers
sv-agent ask "What are the key quality metrics for SV calling?"
sv-agent ask "How do I handle batch effects?"
```

### 5. Workflow Analysis
```bash
# Analyze main batch workflow
sv-agent analyze GATKSVPipelineBatch -f json > workflow_analysis.json
```

### 6. Complete Workflow Execution
```bash
# Convert and run a module
sv-agent convert -m Module00a -o cwl_output
sv-agent run cwl_output/Module00a.cwl inputs.yaml -o results/

# Run with Singularity on HPC
sv-agent run workflow.cwl inputs.yaml --singularity --engine cwltool

# Run on Seven Bridges cloud
export SB_AUTH_TOKEN=your-token-here
sv-agent run workflow.cwl inputs.yaml --engine sevenbridges --sb-project my-project
```

## Environment Variables

sv-agent respects the following environment variables:

- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude models
- `OLLAMA_HOST` - Override default Ollama host

## Tips

1. **For code generation**: Use `--llm-provider ollama --ollama-model codellama:13b`
2. **For quick lookups**: Use the `ask` command instead of entering chat
3. **For automation**: Use `--format json` with analyze command
4. **For debugging**: Add `-v` for verbose logging

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Conversion error