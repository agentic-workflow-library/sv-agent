"""Knowledge base for SV-Agent - Domain expertise in structural variant analysis."""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json


class SVKnowledgeBase:
    """Knowledge base containing domain expertise for structural variant analysis."""
    
    def __init__(self):
        """Initialize the SV knowledge base."""
        self.domain = "Structural Variant Analysis"
        self.pipeline = "GATK-SV"
        
        # Define SV types and their characteristics
        self.sv_types = {
            "DEL": {
                "name": "Deletion",
                "description": "Loss of genomic sequence",
                "min_size": 50,
                "detection_methods": ["read depth", "split reads", "discordant pairs"],
                "impact": "Can cause loss of function if affecting genes"
            },
            "DUP": {
                "name": "Duplication", 
                "description": "Gain of genomic sequence",
                "min_size": 50,
                "detection_methods": ["read depth", "split reads", "discordant pairs"],
                "impact": "Can cause dosage imbalance"
            },
            "INV": {
                "name": "Inversion",
                "description": "Reversal of genomic sequence orientation",
                "min_size": 50,
                "detection_methods": ["split reads", "discordant pairs"],
                "impact": "Can disrupt genes at breakpoints"
            },
            "INS": {
                "name": "Insertion",
                "description": "Addition of new sequence",
                "min_size": 50,
                "detection_methods": ["split reads", "local assembly"],
                "impact": "Can disrupt genes or regulatory elements"
            },
            "BND": {
                "name": "Breakend",
                "description": "Complex rearrangement or translocation",
                "min_size": 0,
                "detection_methods": ["split reads", "discordant pairs"],
                "impact": "Can create fusion genes or disrupt multiple loci"
            }
        }
        
        # GATK-SV modules and their purposes
        self.modules = {
            "Module00a": {
                "name": "Sample QC",
                "purpose": "Assess individual sample quality metrics",
                "inputs": ["BAM/CRAM files", "reference genome"],
                "outputs": ["QC metrics", "coverage statistics"],
                "key_metrics": ["mean coverage", "insert size distribution", "chimeric read rate"]
            },
            "Module00b": {
                "name": "Evidence Collection",
                "purpose": "Gather SV evidence from multiple algorithms",
                "algorithms": ["Manta", "MELT", "Wham", "cn.MOPS"],
                "evidence_types": ["split reads", "discordant pairs", "read depth"],
                "outputs": ["raw SV calls per algorithm", "evidence files"]
            },
            "Module00c": {
                "name": "Batch QC",
                "purpose": "Assess batch-level quality and identify outliers",
                "checks": ["sample relatedness", "batch effects", "coverage uniformity"],
                "outputs": ["outlier samples", "batch statistics"]
            },
            "Module01": {
                "name": "Clustering",
                "purpose": "Cluster SV calls across samples",
                "process": "Merge similar calls within and across samples",
                "outputs": ["clustered SV sites", "variant frequencies"]
            },
            "Module02": {
                "name": "Variant Filtering",
                "purpose": "Apply quality filters to SV calls",
                "filters": ["frequency", "quality score", "evidence support"],
                "outputs": ["filtered VCF", "filter statistics"]
            },
            "Module03": {
                "name": "Genotyping",
                "purpose": "Re-genotype SVs across all samples",
                "methods": ["read depth", "split read counting", "paired-end mapping"],
                "outputs": ["genotyped VCF", "genotype quality scores"]
            },
            "Module04": {
                "name": "Complex SV Resolution",
                "purpose": "Resolve complex and multi-allelic SVs",
                "handles": ["overlapping SVs", "complex rearrangements", "multi-allelic sites"],
                "outputs": ["resolved VCF"]
            },
            "Module05": {
                "name": "Annotation",
                "purpose": "Annotate SVs with functional information",
                "annotations": ["gene overlap", "regulatory elements", "population frequency"],
                "databases": ["gnomAD-SV", "DGV", "ENCODE"],
                "outputs": ["annotated VCF"]
            },
            "Module06": {
                "name": "Final QC",
                "purpose": "Final quality control and metric generation",
                "metrics": ["Ti/Tv ratio", "SV size distribution", "per-sample counts"],
                "outputs": ["final VCF", "QC report"]
            }
        }
        
        # Common questions and answers
        self.faq = {
            "What is GATK-SV?": "GATK-SV is a comprehensive pipeline developed by the Broad Institute for discovering structural variants (SVs) in whole-genome sequencing data. It uses multiple evidence types and algorithms to detect deletions, duplications, inversions, insertions, and complex rearrangements.",
            
            "What are structural variants?": "Structural variants (SVs) are genomic alterations larger than 50bp, including deletions (DEL), duplications (DUP), inversions (INV), insertions (INS), and translocations (BND). They contribute significantly to genetic diversity and disease.",
            
            "What input data do I need?": "You need: 1) Aligned BAM or CRAM files (whole genome sequencing, >30x coverage recommended), 2) Reference genome (matching your alignment), 3) Sample metadata (sex, batch information)",
            
            "How long does the pipeline take?": "For a cohort of 100 samples at 30x coverage: Module00a-c: 2-4 hours, Module01-03: 6-12 hours, Module04-06: 4-8 hours. Total: 12-24 hours depending on compute resources.",
            
            "What algorithms does GATK-SV use?": "GATK-SV integrates multiple SV callers: Manta (all SV types), MELT (mobile element insertions), Wham (deletions, duplications), cn.MOPS (copy number variants). It combines their results for comprehensive SV detection.",
            
            "How do I interpret the outputs?": "The final VCF contains: SV type and coordinates, quality scores, genotypes for each sample, allele frequencies, functional annotations. Use FILTER column for high-confidence calls (PASS) and INFO fields for detailed metrics.",
            
            "What coverage is recommended?": "Minimum 30x mean coverage for reliable SV detection. Lower coverage (10-20x) can detect large SVs but misses smaller events. Higher coverage (>50x) improves sensitivity for complex SVs.",
            
            "Can I run on a single sample?": "GATK-SV is designed for cohort analysis (minimum 30 samples recommended). For single samples, consider using individual SV callers like Manta or Delly directly.",
            
            "How do I handle related samples?": "Include relationship information in your sample metadata. The pipeline accounts for relatedness in allele frequency calculations and filtering. Trios and families can improve SV calling accuracy.",
            
            "What compute resources do I need?": "Recommended: 16-32 cores, 64-128GB RAM per node, 1-2TB storage per 100 samples. The pipeline is parallelizable across samples and genomic regions."
        }
        
        # Best practices
        self.best_practices = {
            "sample_selection": [
                "Use samples from the same sequencing platform and chemistry",
                "Include at least 30 samples for robust frequency estimates",
                "Balance cases and controls if studying disease",
                "Include both sexes for better X/Y chromosome SV calling"
            ],
            "quality_control": [
                "Remove samples with <10x mean coverage",
                "Check for contamination and sample swaps",
                "Identify and handle outliers in insert size or chimeric reads",
                "Verify sex from coverage of sex chromosomes"
            ],
            "filtering_strategy": [
                "Start with default filters, adjust based on validation",
                "Consider population-specific allele frequencies",
                "Use orthogonal validation for novel SVs",
                "Be more stringent for clinical applications"
            ],
            "validation": [
                "Use PCR for breakpoint validation",
                "Employ orthogonal methods (array CGH, optical mapping)",
                "Check inheritance patterns in families",
                "Visualize calls in IGV or similar tools"
            ]
        }
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific module."""
        return self.modules.get(module_name, {})
    
    def get_sv_type_info(self, sv_type: str) -> Dict[str, Any]:
        """Get information about a specific SV type."""
        return self.sv_types.get(sv_type.upper(), {})
    
    def search_knowledge(self, query: str) -> List[Dict[str, str]]:
        """Search the knowledge base for relevant information."""
        query_lower = query.lower()
        results = []
        
        # Search FAQs
        for question, answer in self.faq.items():
            if query_lower in question.lower() or query_lower in answer.lower():
                results.append({
                    "type": "FAQ",
                    "question": question,
                    "answer": answer
                })
        
        # Search modules
        for module_id, module_info in self.modules.items():
            if query_lower in str(module_info).lower():
                results.append({
                    "type": "Module",
                    "id": module_id,
                    "info": module_info
                })
        
        # Search SV types
        for sv_type, sv_info in self.sv_types.items():
            if query_lower in str(sv_info).lower():
                results.append({
                    "type": "SV Type",
                    "id": sv_type,
                    "info": sv_info
                })
        
        return results
    
    def get_pipeline_overview(self) -> str:
        """Get a comprehensive overview of the GATK-SV pipeline."""
        return """
GATK-SV Pipeline Overview:

The GATK-SV pipeline is a comprehensive workflow for structural variant discovery in whole-genome sequencing data. It consists of several modules that work together:

1. **Evidence Collection** (Module00a-c): 
   - Collects quality metrics per sample
   - Runs multiple SV calling algorithms
   - Performs batch-level QC

2. **SV Discovery** (Module01-02):
   - Clusters SV calls across samples
   - Filters based on quality and frequency

3. **Genotyping** (Module03):
   - Re-genotypes all SVs across all samples
   - Provides accurate allele frequencies

4. **Resolution & Annotation** (Module04-05):
   - Resolves complex variants
   - Annotates with functional information

5. **Final QC** (Module06):
   - Generates final metrics
   - Produces analysis-ready VCF

The pipeline can detect:
- Deletions (DEL) ≥50bp
- Duplications (DUP) ≥50bp  
- Inversions (INV) ≥50bp
- Insertions (INS) ≥50bp
- Translocations/Complex (BND)

It integrates evidence from:
- Split reads
- Discordant read pairs
- Read depth
- Local assembly
"""