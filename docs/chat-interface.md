# SV-Agent Chat Interface

The sv-agent chat interface provides an interactive, conversational way to get expert guidance on structural variant analysis and GATK-SV workflows. It combines domain-specific knowledge with optional LLM capabilities for natural language understanding.

## Overview

The chat interface offers two modes:
- **LLM-enhanced mode**: Natural conversation using local (Ollama) or cloud LLMs
- **Rule-based mode**: Deterministic responses based on curated knowledge base

## Quick Start

### Basic Usage

```bash
# Start interactive chat
sv-agent chat

# Ask a single question
sv-agent ask "What coverage do I need for SV detection?"

# Use specific LLM provider
sv-agent chat --llm-provider ollama --ollama-model codellama:13b
```

### Python API

```python
from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat

# Initialize chat
agent = SVAgent()
chat = SVAgentChat(agent)

# Get response
response = chat.chat("Explain Module00a")
print(response)
```

## Chat Capabilities

### 1. **Module Explanations**
Ask about any GATK-SV module to understand its purpose, inputs, and outputs.

```
You: Explain Module00a
SV-Agent: Module00a (GatherSampleEvidence) collects SV evidence from individual samples...
```

### 2. **Workflow Conversion Guidance**
Get help converting WDL workflows to CWL format.

```
You: How do I convert Module00b to CWL?
SV-Agent: To convert Module00b to CWL, use: sv-agent convert --modules Module00b...
```

### 3. **Best Practices**
Receive recommendations for SV analysis based on your specific use case.

```
You: What coverage should I use for clinical SV detection?
SV-Agent: For clinical SV detection, we recommend 30-50x mean coverage...
```

### 4. **Troubleshooting**
Get help diagnosing and fixing common issues.

```
You: I'm getting low SV calls, what should I check?
SV-Agent: For low SV calls, check: 1) Coverage depth, 2) Insert size distribution...
```

### 5. **Analysis Planning**
Plan your SV analysis pipeline based on your samples and goals.

```
You: I have 100 trio samples, how should I run GATK-SV?
SV-Agent: For 100 trios, I recommend: 1) Run in family-aware mode...
```

## LLM Integration

### Supported Providers

| Provider | Use Case | Requirements | Command |
|----------|----------|--------------|---------|
| **Ollama** | Air-gapped, privacy-sensitive | Local Ollama installation | `--llm-provider ollama` |
| **OpenAI** | Cloud-based, GPT models | API key | `--llm-provider openai` |
| **Anthropic** | Cloud-based, Claude models | API key | `--llm-provider anthropic` |
| **None** | No LLM, rule-based only | None | `--llm-provider none` |

### Ollama Setup (Recommended for Bioinformatics)

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull recommended models**:
   ```bash
   # For code/CWL generation
   ollama pull codellama:13b
   
   # For general SV questions
   ollama pull llama2:13b
   
   # For biomedical context
   ollama pull biomistral
   ```

3. **Use with sv-agent**:
   ```bash
   sv-agent chat --llm-provider ollama --ollama-model codellama:13b
   ```

### Air-Gapped Setup

For secure environments without internet:

1. **On connected machine**:
   ```bash
   # Download Ollama and models
   ollama pull codellama:13b
   ollama pull llama2:13b
   ```

2. **Transfer to air-gapped system**:
   - Copy Ollama binary
   - Copy model files from `~/.ollama/models/`

3. **Run locally**:
   ```bash
   ollama serve  # Start Ollama server
   sv-agent chat --llm-provider ollama
   ```

## Chat Features

### Intent Recognition
The chat interface recognizes different types of queries:

- **Help/Capabilities**: "What can you do?", "help"
- **Explanations**: "What is...", "Explain..."
- **Conversions**: "Convert to CWL", "How to convert..."
- **Analysis**: "Analyze my samples", "Check quality..."
- **Recommendations**: "Should I...", "Recommend..."
- **Troubleshooting**: "Error with...", "Problem..."

### Context Awareness
- Maintains conversation history for multi-turn interactions
- References previous questions and answers
- Tracks current module/workflow context

### Knowledge Integration
- Access to curated GATK-SV documentation
- Module-specific information
- Best practices database
- Common troubleshooting solutions

## Examples

### Example 1: Planning an Analysis
```
You: I have 50 samples from families with autism. How should I set up my analysis?

SV-Agent: For 50 samples from autism families, I recommend:

1. **Sample Organization**:
   - Group samples by family
   - Include unaffected family members as controls
   - Document relationships in PED file

2. **Coverage Requirements**:
   - Aim for 30-40x coverage
   - Consistent library prep across families

3. **Analysis Strategy**:
   - Run Module00a-c for evidence gathering
   - Use family-aware mode in Module04
   - Focus on de novo SV detection

4. **Special Considerations**:
   - Enable trio-aware genotyping
   - Apply inheritance filters
   - Annotate with brain-expressed genes

Would you like help setting up the configuration file?
```

### Example 2: Troubleshooting
```
You: Module00b failed with memory error on sample NA12878

SV-Agent: Memory errors in Module00b typically occur during MELT processing. Try:

1. **Increase memory allocation**:
   ```
   runtime {
     memory: "64 GB"  # Increase from default 32 GB
   }
   ```

2. **Check problematic regions**:
   - High repeat content can cause excessive memory use
   - Consider excluding centromeric regions

3. **Sample-specific issues**:
   ```bash
   # Check BAM file size
   ls -lh NA12878.bam
   
   # Verify not corrupted
   samtools quickcheck NA12878.bam
   ```

4. **Workaround**:
   - Process this sample separately
   - Use --exclude-melt flag if needed

Did the job fail immediately or after running for a while?
```

### Example 3: Module Deep Dive
```
You: Tell me everything about Module03 filtering

SV-Agent: **Module03: FilterBatch** - Comprehensive Variant Filtering

**Purpose**: Apply quality filters to remove false positive SV calls

**Key Steps**:
1. Random Forest filtering using evidence metrics
2. Frequency-based filtering
3. Size-based filtering
4. Batch effect detection

**Inputs**:
- Genotyped VCFs from Module02
- Evidence metrics
- Batch metadata

**Outputs**:
- Filtered VCF files
- QC plots
- Outlier sample lists

**Important Parameters**:
- `min_sv_size`: 50 (default)
- `max_ref_freq`: 0.01 for rare variants
- `min_GQ`: 20 for high confidence

**Quality Metrics Used**:
- PE_SR_support: Read evidence
- RD_CN_concordance: Copy number agreement
- BAF_KS_stat: Allele frequency deviation

**Common Issues**:
- Over-filtering in small cohorts
- Under-filtering common variants
- Batch effects from different prep methods

Would you like to see the recommended thresholds for your cohort size?
```

## Advanced Usage

### Custom Knowledge Base

```python
from sv_agent.chat import SVAgentChat
from sv_agent.knowledge import SVKnowledgeBase

# Extend with custom knowledge
kb = SVKnowledgeBase()
kb.add_faq(
    "What is my lab's SV calling protocol?",
    "Our lab uses 40x WGS with 150bp PE reads..."
)

chat = SVAgentChat(knowledge_base=kb)
```

### Conversation Memory

```python
# Access conversation history
chat = SVAgentChat(agent)
chat.chat("What is Module00a?")
chat.chat("What are its outputs?")  # Refers to Module00a

# Clear memory for new topic
chat.memory.clear()
```

### Programmatic Integration

```python
# Batch Q&A processing
questions = [
    "What coverage for trios?",
    "How to handle related samples?",
    "Best practices for rare variants?"
]

responses = {}
for q in questions:
    responses[q] = chat.chat(q)
```

## Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic  
export ANTHROPIC_API_KEY="sk-ant-..."

# Ollama (if not default)
export OLLAMA_HOST="http://localhost:11434"
```

### CLI Options

```bash
sv-agent chat \
  --llm-provider ollama \
  --ollama-model codellama:13b \
  --ollama-url http://localhost:11434 \
  --no-banner  # Skip welcome message
```

## Best Practices

1. **Start with general questions** to understand capabilities
2. **Be specific** about your samples and goals
3. **Use module names** (Module00a) for targeted help
4. **Provide context** (sample count, coverage, platform)
5. **Ask follow-up questions** for clarification

## Limitations

- **Rule-based mode**: Limited to predefined patterns
- **LLM mode**: May require fact-checking for specific parameters
- **No direct execution**: Provides commands but doesn't run them
- **Knowledge cutoff**: Based on GATK-SV documentation version

## Getting Help

```bash
# In chat
You: help

# Check available modules
sv-agent list --details

# View this documentation
sv-agent chat
You: How do I use the chat interface?
```