# SV-Agent Chat Examples

This document provides real-world examples of using the sv-agent chat interface for various structural variant analysis tasks.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Module Information](#module-information)
3. [Best Practices](#best-practices)
4. [Troubleshooting](#troubleshooting)
5. [Workflow Conversion](#workflow-conversion)
6. [Analysis Planning](#analysis-planning)
7. [Advanced Topics](#advanced-topics)

## Getting Started

### Basic Questions

```
You: What is GATK-SV?

SV-Agent: GATK-SV is the Genome Analysis Toolkit for Structural Variants, a comprehensive pipeline developed by the Broad Institute for discovering and genotyping structural variants (SVs) from whole genome sequencing data. It integrates multiple SV callers (Manta, MELT, Wham, cn.MOPS) and uses sophisticated filtering and genotyping algorithms to produce high-quality SV calls across deletions, duplications, inversions, insertions, and translocations.
```

```
You: What types of structural variants can it detect?

SV-Agent: GATK-SV detects five main types of structural variants:

1. **DEL (Deletions)**: Loss of genomic sequence ≥50bp
2. **DUP (Duplications)**: Gain of genomic sequence, including tandem and dispersed
3. **INV (Inversions)**: Reversal of DNA sequence orientation
4. **INS (Insertions)**: Addition of novel sequence, including MEIs
5. **BND (Breakends)**: Complex rearrangements and translocations

The pipeline also identifies complex variants (CPX) involving multiple breakpoints and can detect mobile element insertions (ALU, LINE1, SVA) using MELT.
```

## Module Information

### Understanding Pipeline Modules

```
You: Explain the purpose of each GATK-SV module

SV-Agent: Here's an overview of the GATK-SV modules in sequential order:

**Evidence Collection (Module00a-c)**:
- Module00a (GatherSampleEvidence): Runs SV callers on individual samples
- Module00b (EvidenceQC): Quality control of evidence collection
- Module00c (GatherBatchEvidence): Merges evidence across samples

**Variant Discovery (Module01-03)**:
- Module01 (ClusterBatch): Clusters raw SV calls across samples
- Module02 (GenerateBatchMetrics): Tests variants against evidence
- Module03 (FilterBatch): Applies quality filters

**Genotyping & Refinement (Module04-06)**:
- Module04 (GenotypeBatch): Re-genotypes filtered variants
- Module05 (MakeCohortVcf): Combines batches, resolves complex SVs
- Module06 (AnnotateVcf): Adds functional annotations

Each module builds on the previous outputs, creating a robust pipeline for SV discovery.
```

### Module-Specific Details

```
You: What exactly does Module00a do? What are its inputs and outputs?

SV-Agent: **Module00a: GatherSampleEvidence** collects SV evidence from individual samples.

**Inputs**:
- BAM/CRAM file (aligned reads)
- Reference genome (FASTA)
- Sample metadata (sex, batch)

**Processing Steps**:
1. Runs Manta for all SV types
2. Runs MELT for mobile elements
3. Runs Scramble for MEI detection
4. Runs Wham for additional signals
5. Collects read depth (binned coverage)
6. Extracts discordant pairs (PE)
7. Identifies split reads (SR)

**Outputs**:
- Manta VCF
- MELT VCF
- Scramble VCF
- Coverage file (RD)
- Discordant pairs file (PE)
- Split reads file (SR)

**Runtime**: ~8-12 hours for 30x WGS
**Memory**: 32GB recommended
```

## Best Practices

### Coverage Requirements

```
You: What coverage do I need for different types of studies?

SV-Agent: Coverage recommendations depend on your study goals:

**Research/Discovery (Recommended)**:
- 30-40x mean coverage
- Detects SVs ≥50bp reliably
- Good sensitivity for all SV types
- Suitable for rare variant discovery

**Population Studies**:
- 15-20x coverage acceptable
- Reliable for SVs >500bp
- May miss smaller events
- Good for common variant analysis

**Clinical/Diagnostic**:
- 40-50x coverage ideal
- Maximum sensitivity needed
- Accurate genotyping critical
- Consider 150bp PE reads

**Low-pass/Screening**:
- 5-10x coverage
- Only large SVs (>5kb)
- Limited genotyping accuracy
- Useful for aneuploidy detection

**Factors affecting requirements**:
- Library prep (PCR-free preferred)
- Read length (longer is better)
- Insert size (300-500bp optimal)
- Sample quality (FFPE needs more)
```

### Sample Selection

```
You: How should I organize samples for a cohort study?

SV-Agent: Here are best practices for cohort organization:

**1. Batch Composition**:
- 100-200 samples per batch (optimal)
- Mix cases and controls in each batch
- Balance by sex (for chrX/Y analysis)
- Include samples from all populations

**2. Technical Considerations**:
- Same sequencing platform per batch
- Consistent library prep methods
- Similar coverage depths (±20%)
- Process related samples together

**3. Quality Controls**:
- Include known reference samples
- Add technical replicates (2-3%)
- Document batch variables
- Track family relationships

**4. Metadata Requirements**:
```
Sample_ID  Sex  Batch  Population  Case_Control  Family_ID
SAMP001    F    B1     EUR         Case          FAM001
SAMP002    M    B1     EUR         Control       FAM001
```

**5. Special Considerations**:
- Trios: Process parents with probands
- Cancer: Match tumor-normal pairs
- Mosaics: Increase coverage depth
- Cell lines: Note passage number
```

## Troubleshooting

### Low Call Counts

```
You: I'm getting very few SV calls from my samples. What could be wrong?

SV-Agent: Low SV calls can result from several issues. Let's diagnose:

**1. Check Coverage Depth**:
```bash
samtools depth -a sample.bam | awk '{sum+=$3} END {print "Mean coverage:", sum/NR}'
```
- Need ≥30x for good sensitivity
- Check coverage uniformity

**2. Verify Alignment Quality**:
```bash
samtools flagstat sample.bam
```
- Look for >90% mapped reads
- Check properly paired percentage
- High duplicates reduce effective coverage

**3. Library Characteristics**:
```bash
samtools stats sample.bam | grep "insert size"
```
- Insert size should be 300-500bp
- Narrow inserts miss large deletions
- Check for PCR artifacts

**4. Common Issues & Solutions**:
- **Wrong reference**: Ensure hg38/GRCh38 match
- **Missing chrY**: Check sex chromosomes included
- **Old aligner**: Use BWA-MEM, not BWA-ALN
- **Filtered reads**: Include unmapped/clipped reads
- **Module00c failed**: Check batch outliers

**5. Expected SV Counts** (per genome):
- DEL: 2,500-3,500
- DUP: 500-1,000
- INV: 200-400
- INS: 200-400
- Total: 3,500-5,000

Would you like me to help analyze your specific QC metrics?
```

### Memory Errors

```
You: Module02 keeps failing with java.lang.OutOfMemoryError

SV-Agent: Java memory errors in Module02 (GenerateBatchMetrics) typically occur during evidence collection. Here's how to fix:

**1. Increase Java Heap Memory**:
Edit the WDL runtime block:
```wdl
runtime {
  memory: "120 GB"  # Increase from default
  java_mem: "-Xmx100G"  # Set explicit heap
}
```

**2. Add JVM Flags**:
```
-XX:+UseG1GC
-XX:ParallelGCThreads=4
-XX:ConcGCThreads=1
-XX:InitiatingHeapOccupancyPercent=35
```

**3. Reduce Batch Size**:
- Split large batches (>200 samples)
- Process in groups of 100
- Merge results afterward

**4. Check Problem Regions**:
- Centromeres use excessive memory
- Consider excluding with interval list
- Check for reference assembly issues

**5. Alternative Solutions**:
- Use scattered execution
- Process chromosomes separately
- Increase disk space for temp files
- Use SSDs for faster I/O

**6. Monitoring**:
```bash
# Watch memory usage
jstat -gc <pid> 1000

# Check heap dumps if still failing
-XX:+HeapDumpOnOutOfMemoryError
```

The memory requirement scales with:
- Number of samples (linear)
- SV density (problematic regions)
- Evidence file sizes
```

## Workflow Conversion

### Converting Modules to CWL

```
You: How do I convert Module00a to CWL and what should I expect?

SV-Agent: To convert Module00a (GatherSampleEvidence) to CWL:

**1. Run Conversion**:
```bash
sv-agent convert -o cwl_output -m Module00a

# Or use Python:
from sv_agent import SVAgent
agent = SVAgent()
results = agent.convert_gatksv_to_cwl(
    output_dir="cwl_output",
    modules=["Module00a"]
)
```

**2. Expected Output Structure**:
```
cwl_output/
├── GatherSampleEvidence.cwl      # Main workflow
├── tools/
│   ├── manta.cwl                # Individual tools
│   ├── melt.cwl
│   ├── scramble.cwl
│   └── collect_coverage.cwl
└── types/
    └── sv_types.cwl             # Common type definitions
```

**3. Key Conversions**:
- WDL `task` → CWL `CommandLineTool`
- WDL `workflow` → CWL `Workflow`
- WDL `scatter` → CWL `scatter`
- WDL `runtime` → CWL `requirements`

**4. Validation**:
```bash
# Validate CWL syntax
cwltool --validate cwl_output/GatherSampleEvidence.cwl

# Test with sample inputs
cwltool cwl_output/GatherSampleEvidence.cwl inputs.yaml
```

**5. Input File Format** (inputs.yaml):
```yaml
bam_file:
  class: File
  path: /path/to/sample.bam
reference:
  class: File
  path: /path/to/reference.fa
sample_id: "SAMPLE001"
```

**6. Common Issues**:
- Docker images: Ensure URIs are accessible
- File paths: Use absolute paths
- Memory: Adjust ResourceRequirements
```

## Analysis Planning

### Cohort Study Design

```
You: I'm planning a study with 500 samples from autism families. How should I design the analysis?

SV-Agent: Here's a comprehensive plan for your 500-sample autism family study:

**1. Sample Organization**:
```
- Complete trios: ~150 families (450 samples)
- Unaffected siblings: 50 samples
- Batch size: 125 samples × 4 batches
- Mix families across batches
```

**2. Sequencing Strategy**:
- Coverage: 35-40x WGS
- Read length: 150bp PE
- Insert size: 350-450bp
- PCR-free library prep
- Include 5-10 GIAB controls

**3. Analysis Pipeline**:
```bash
# Phase 1: Evidence Collection
Module00a-c per batch
Estimated time: 2-3 days

# Phase 2: Joint Calling
Modules 01-03 on all samples
Focus on rare variants (AF < 0.01)
Estimated time: 3-4 days

# Phase 3: Family-Aware Genotyping
Module04 with pedigree file
Enable de novo calling
Estimated time: 2 days

# Phase 4: Annotation & Filtering
Prioritize brain-expressed genes
Filter for high-impact variants
Check inheritance patterns
```

**4. De Novo Detection**:
- Expected: 5-10 de novo SVs per trio
- Higher rates suggest QC issues
- Validate with orthogonal methods

**5. Computational Resources**:
- CPU cores: 500-1000
- Memory: 10TB total
- Storage: 50TB for full analysis
- Cost: ~$20-30K on cloud

**6. Quality Checkpoints**:
- Post-Module00b: Sample QC
- Post-Module03: Variant QC  
- Post-Module04: Mendelian errors
- Final: Clinical interpretation

Would you like specific parameter recommendations for any module?
```

### Single Sample Analysis

```
You: Can I analyze just one sample with GATK-SV?

SV-Agent: Yes, GATK-SV supports single-sample mode, though it differs from cohort analysis:

**1. Use GATKSVPipelineSingleSample**:
```bash
sv-agent convert -m GATKSVPipelineSingleSample
```

**2. Key Differences**:
- No batch effects to correct
- Limited filtering capabilities
- Uses reference panel for comparison
- Faster but less sensitive

**3. When to Use**:
- Rapid clinical diagnosis
- Pilot/QC runs
- Samples incompatible with cohorts
- Validation of specific variants

**4. Requirements**:
- Reference panel VCF (provided)
- Higher coverage helpful (40x+)
- Same reference genome version

**5. Workflow**:
```python
config = {
    "sample": {
        "id": "PATIENT001",
        "bam": "/path/to/patient.bam",
        "sex": "female"
    },
    "reference_panel": "/refs/gnomad_sv_panel.vcf",
    "output_dir": "/results/patient001"
}
```

**6. Limitations**:
- Reduced sensitivity for rare variants
- No cohort frequency information
- Complex variants harder to resolve
- May miss low-quality calls

**7. Best Practice**:
Include sample in next cohort run for comprehensive analysis. Single-sample mode is good for quick screening but shouldn't replace cohort analysis for research.
```

## Advanced Topics

### Complex Structural Variants

```
You: How does GATK-SV handle complex SVs?

SV-Agent: GATK-SV has sophisticated handling for complex structural variants (CPX):

**1. Complex SV Types Detected**:
- **Dispersed Duplications**: DUP with insertion site elsewhere
- **Inverted Duplications**: DUP with inverted orientation  
- **Complex Inversions**: INV with additional breakpoints
- **Chromothripsis**: Massive rearrangements
- **Translocations**: Inter-chromosomal events
- **Multi-breakpoint Events**: 3+ breakpoints

**2. Resolution Process** (Module05):
```
Raw Variants → Breakpoint Clustering → Graph Construction → Path Resolution → Final CPX Call
```

**3. Evidence Integration**:
- PE/SR define breakpoints
- RD confirms copy number
- BAF indicates loss of heterozygosity
- Long reads validate structure

**4. Example Complex Event**:
```
CPX_123: chr1:1000-2000 
Type: delINVdup
Interpretation: Deletion + Inversion + Duplication
Breakpoints: 4
Copy number: 0,2,3
```

**5. Quality Considerations**:
- Requires high coverage (>35x)
- Multiple evidence types needed
- Manual review recommended
- Validation challenging

**6. Clinical Relevance**:
- Often pathogenic
- Gene disruption common
- Fusion genes possible
- Inheritance usually de novo

**7. Visualization**:
The pipeline generates plots showing:
- Copy number profile
- Breakpoint connections
- Supporting reads
- Allele frequency shifts

Would you like details on interpreting specific complex variant types?
```

### Performance Optimization

```
You: How can I make GATK-SV run faster for large cohorts?

SV-Agent: Here are strategies to optimize GATK-SV performance:

**1. Parallelization Settings**:
```wdl
# Increase scatter width
scatter_count: 50  # Default: 10

# Parallel sample processing
samples_per_chunk: 10  # For Module00a

# Chromosome-level parallelism
process_chromosomes_parallel: true
```

**2. Resource Allocation**:
```
Module00a: 8 CPU, 32GB RAM per sample
Module01: 32 CPU, 120GB RAM per batch
Module04: 16 CPU, 64GB RAM per shard
```

**3. Storage Optimization**:
- Use SSDs for temp files
- Enable compression for intermediates
- Delete evidence files after Module03
- Archive raw caller outputs

**4. Batch Strategy**:
```python
# Optimal batch sizes
if total_samples < 100:
    batch_size = total_samples
elif total_samples < 500:
    batch_size = 100
else:
    batch_size = 200
```

**5. Skip Unnecessary Steps**:
- `--skip-melt` if no MEI interest
- `--skip-qc-plots` for production
- `--minimal-output` for storage

**6. Infrastructure Tips**:
- Preemptible instances for Module00a
- High-memory nodes for Module01-03
- Local scratch disks reduce I/O
- Cache Docker images

**7. Time Estimates** (1000 samples):
```
Standard: 7-10 days
Optimized: 3-5 days
Cost reduction: 40-50%
```

**8. Monitoring**:
```bash
# Track progress
tail -f workflow.log | grep "Completed"

# Resource usage
cromwell-monitor --workflow-id xxx
```

**9. Common Bottlenecks**:
- MELT in Module00a (8hrs/sample)
- Evidence merging in Module00c
- Genotyping in Module04
- Complex resolution in Module05
```

## Summary

These examples demonstrate the sv-agent chat interface's ability to provide:
- Detailed technical guidance
- Troubleshooting assistance
- Best practices recommendations
- Workflow planning support
- Performance optimization tips

The chat adapts responses based on user expertise level and provides actionable commands and code snippets for immediate use.