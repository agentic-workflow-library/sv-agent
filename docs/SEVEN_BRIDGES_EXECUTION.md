# Seven Bridges Platform Execution

sv-agent now supports intelligent execution of GATK-SV workflows on Seven Bridges platforms through natural language prompts and interactive dialogs.

## Supported Platforms

### Free/Academic Platforms
- **Cancer Genomics Cloud (CGC)** - Free for cancer research with TCGA/TARGET data access
- **CAVATICA** - Free for pediatric research with Kids First data access

### Commercial Platforms  
- **Seven Bridges Platform (AWS)** - Pay-per-use on AWS infrastructure
- **Seven Bridges Platform (GCP)** - Pay-per-use on Google Cloud
- **Seven Bridges Platform (Azure)** - Pay-per-use on Azure infrastructure

## How to Use

### 1. Natural Language Requests

Simply describe what you want to execute and mention Seven Bridges:

```
"Run QC on Seven Bridges with sample1.bam"
"Execute Module00a on CGC platform"
"Process this on CAVATICA: sbg://project/sample.bam"
"Run genotyping on Seven Bridges platform with large instances"
```

### 2. Interactive Dialog

The agent will guide you through a multi-step dialog to collect:

**Step 1: Platform Selection**
```
Which Seven Bridges platform would you like to use?

1. cgc: Cancer Genomics Cloud - NIH Cancer Genomics Cloud for cancer research
2. cavatica: CAVATICA - Kids First Data Resource Center platform for pediatric research  
3. aws: Seven Bridges Platform (AWS) - Commercial platform on AWS infrastructure
4. gcp: Seven Bridges Platform (GCP) - Commercial platform on Google Cloud infrastructure
5. azure: Seven Bridges Platform (Azure) - Commercial platform on Azure infrastructure

Please respond with a number or the platform name.
```

**Step 2: Module Selection**
```
Which GATK-SV module would you like to run?

1. Module00a: Sample QC (GatherSampleEvidence)
2. Module00b: Evidence Collection
3. Module00c: Batch QC
4. Module01: Clustering
5. Module03: Filtering
6. Module04: Genotyping

Please respond with a number or module name.
```

**Step 3: Input Files**
```
What input files would you like to process? 
Provide Seven Bridges file paths like sbg://project/file.bam or describe the files.
```

**Step 4: Project**
```
What Seven Bridges project should I use? (Format: username/project-name)
```

**Step 5: Instance Size**
```
What instance size would you like to use?

1. small: c5.xlarge (4 CPU, 8 GB RAM) - Small workloads, single sample QC
2. medium: c5.4xlarge (16 CPU, 32 GB RAM) - Medium workloads, batch processing
3. large: c5.9xlarge (36 CPU, 72 GB RAM) - Large workloads, cohort analysis
4. memory: r5.4xlarge (16 CPU, 128 GB RAM) - Memory-intensive tasks, large references

Please respond with a number or size name.
```

### 3. Execution Plan

After collecting all information, you'll get a comprehensive execution plan:

```
🚀 Seven Bridges Execution Plan

Platform: Cancer Genomics Cloud
Project: myuser/my-sv-project
Module: Module00a

Input Files:
- sbg://myuser/my-sv-project/sample1.bam
- sbg://myuser/my-sv-project/sample2.bam

Cost Estimate:
- Instance: c5.4xlarge
- Estimated time: 2 hours
- Estimated cost: $1.60
- Note: Estimates are approximate and exclude storage costs

Execution Steps:
1. Upload CWL workflow to Seven Bridges platform
2. Configure workflow inputs and parameters
3. Set compute instance requirements
4. Submit workflow execution
5. Monitor execution progress
6. Download results when complete

Seven Bridges CLI Commands:
```bash
# Set Seven Bridges profile
sb config set endpoint https://cgc-api.sbgenomics.com/v2
sb config set token YOUR_AUTH_TOKEN

# Upload CWL workflow
sb apps install-workflow src/sv_agent/cwl/Module00a.cwl myuser/my-sv-project

# Create and submit task
sb tasks create \
  --project myuser/my-sv-project \
  --app myuser/my-sv-project/module00a \
  --name 'Module00a-execution' \
  --inputs '{"bam_or_cram_file": "sbg://myuser/my-sv-project/sample1.bam"}' \
  --instance-type c5.4xlarge

# Monitor execution
sb tasks list --project myuser/my-sv-project --status RUNNING
```

Next Steps:
1. Ensure you have Seven Bridges CLI installed: `pip install sevenbridges-python`
2. Set up authentication token
3. Run the commands above
4. Or say 'execute this plan' to have me guide you through it

Would you like me to proceed with execution or modify anything?
```

## Prerequisites

### 1. Seven Bridges CLI
```bash
pip install sevenbridges-python
```

### 2. Authentication Token
Get your authentication token from:
- CGC: https://cgc.sbgenomics.com/developer/token
- CAVATICA: https://cavatica.sbgenomics.com/developer/token  
- Commercial: https://platform.sbgenomics.com/developer/token

### 3. Set Up Profile
```bash
sb config set endpoint https://cgc-api.sbgenomics.com/v2
sb config set token YOUR_AUTH_TOKEN
```

## Supported GATK-SV Modules

- **Module00a**: Sample QC (GatherSampleEvidence) - ~2 hours, $1.60
- **Module00b**: Evidence Collection - ~4 hours, $3.20
- **Module00c**: Batch QC - ~1 hour, $0.80
- **Module01**: Clustering - ~6 hours, $4.80
- **Module03**: Filtering - ~3 hours, $2.40
- **Module04**: Genotyping - ~8 hours, $6.40

*Cost estimates are for medium instances (c5.4xlarge) and exclude storage*

## Example Workflows

### Single Sample QC on CGC
```
You: Run QC on CGC with sbg://myproject/sample.bam
Agent: [Guides through platform/module selection]
You: CGC
Agent: [Asks for project]
You: myuser/cancer-study
Agent: [Shows execution plan with costs and commands]
```

### Batch Processing on CAVATICA
```
You: Process evidence QC on CAVATICA for pediatric samples
Agent: [Interactive dialog to collect file paths and parameters]
You: [Provides project info and files]
Agent: [Generates execution plan with batch configuration]
```

### Large Cohort Analysis
```
You: Run genotyping on Seven Bridges with large instances
Agent: [Guides through platform selection and instance sizing]
You: [Selects AWS platform and large instances]
Agent: [Shows plan with high-memory instances and cost estimates]
```

## Features

- **🤖 Intelligent Platform Selection** - Recommends platforms based on data type
- **💰 Cost Estimation** - Provides runtime and cost estimates before execution
- **📋 Multi-step Dialog** - Guides you through all required parameters
- **🔧 Automatic Configuration** - Generates ready-to-run CLI commands
- **📊 Instance Optimization** - Suggests appropriate compute resources
- **🔐 Security-Aware** - Handles authentication and project permissions

This makes executing GATK-SV on Seven Bridges platforms as easy as having a conversation!