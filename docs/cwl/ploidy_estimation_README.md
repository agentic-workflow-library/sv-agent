# Ploidy Estimation CWL Workflow

This directory contains a high-quality CWL conversion of the GATK-SV PloidyEstimation.wdl workflow.

## Overview

The Ploidy Estimation workflow analyzes chromosomal copy number to detect whole-genome duplications and aneuploidies. It consists of two main steps:

1. **BuildPloidyMatrix**: Aggregates fine-resolution coverage bins (typically 100kb) to 1Mb bins for more robust ploidy estimation
2. **PloidyScore**: Runs statistical analysis to estimate ploidy and generates diagnostic plots

## Files

- `PloidyEstimation.cwl` - Main workflow orchestrating the two steps
- `BuildPloidyMatrix.cwl` - Tool for aggregating coverage matrix to 1Mb resolution
- `PloidyScore.cwl` - Tool for ploidy estimation and plot generation
- `RuntimeAttr.yml` - Schema definition for runtime attributes

## Key Conversion Decisions

### 1. Runtime Attributes
- Converted WDL's `RuntimeAttr` struct to a CWL schema defined in `RuntimeAttr.yml`
- Used JavaScript expressions to handle optional overrides with defaults
- Mapped WDL runtime blocks to CWL's `ResourceRequirement`

### 2. Shell Commands
- Preserved complex AWK script exactly as written for bin aggregation
- Used `ShellCommandRequirement` to maintain shell semantics
- Properly escaped special characters in AWK script

### 3. Docker Integration
- Docker images passed as workflow inputs (following GATK-SV pattern)
- Used `DockerRequirement` with dynamic image selection

### 4. File Handling
- Output files use parameterized naming with batch identifier
- Proper glob patterns for output capture
- Maintained gzip compression for matrix files

## Usage Example

```yaml
# inputs.yml
bincov_matrix:
  class: File
  path: /path/to/sample.bincov.bed.gz

batch: "batch001"

sv_base_mini_docker: "us.gcr.io/broad-gatk/gatk-sv/sv-base-mini:latest"
sv_pipeline_qc_docker: "us.gcr.io/broad-gatk/gatk-sv/sv-pipeline-qc:latest"

# Optional runtime overrides
runtime_attr_build:
  mem_gb: 8
  cpu_cores: 2
  disk_gb: 100
```

Run with:
```bash
cwltool PloidyEstimation.cwl inputs.yml
```

## Validation

The CWL files have been designed to be compliant with CWL v1.2 and include:
- Proper typing for all inputs/outputs
- Comprehensive documentation
- Schema validation for custom types
- Resource requirements handling

## Differences from WDL

1. **Type System**: CWL uses explicit schema definitions rather than WDL structs
2. **Runtime**: CWL ResourceRequirement vs WDL runtime block
3. **Expressions**: JavaScript expressions vs WDL's select_first()
4. **Defaults**: Handled via JavaScript expressions with || operator

## Testing

To validate the CWL files:
```bash
cwltool --validate PloidyEstimation.cwl
cwltool --validate BuildPloidyMatrix.cwl
cwltool --validate PloidyScore.cwl
```

## Integration with GATK-SV

This workflow is typically called as part of:
- Module 00c (Batch QC)
- Used for detecting samples with abnormal ploidy
- Results feed into downstream filtering steps