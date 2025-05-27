"""SVAgent implementation using AWLKit framework."""

from pathlib import Path
from typing import Dict, Any, Optional, List

from awlkit import WDLToCWLConverter, WDLParser
from awlkit.agents import Agent
from .knowledge import SVKnowledgeBase


class SVAgent(Agent):
    """Agent for automating GATK-SV structural variant discovery pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SVAgent with optional configuration."""
        super().__init__(config)
        self.name = "SVAgent"
        self.gatksv_path = Path(__file__).parent.parent.parent / "submodules" / "gatk-sv"
        self.converter = WDLToCWLConverter()
        self.parser = WDLParser()
        self.knowledge = SVKnowledgeBase()
        
        # Domain-specific capabilities
        self.domain_capabilities = [
            'convert_gatksv_to_cwl',
            'analyze_gatksv_workflow',
            'sv_detection',
            'sv_filtering',
            'sv_genotyping'
        ]
    
    def _execute_batch(self, batch_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SV-specific batch processing.
        
        Args:
            batch_config: Validated batch configuration
            
        Returns:
            Dictionary containing processing results
        """
        # SV-specific validation
        self._validate_sv_requirements(batch_config)
        
        # For now, return a mock result
        # Real implementation would execute the GATK-SV workflow
        return {
            "status": "success",
            "pipeline": "GATK-SV",
            "modules_executed": ["GatherSampleEvidence", "EvidenceQC", "ClusterBatch"],
            "samples_processed": len(batch_config['samples']),
            "outputs": {
                "vcf": f"{batch_config.get('output_dir', '.')}/sv_calls.vcf.gz",
                "qc_metrics": f"{batch_config.get('output_dir', '.')}/qc_metrics.json"
            },
            "message": "SV detection completed successfully"
        }
    
    def convert_gatksv_to_cwl(self, 
                             output_dir: Path,
                             modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """Convert GATK-SV WDL workflows to CWL format.
        
        Args:
            output_dir: Directory to write CWL files
            modules: Specific modules to convert (None = all)
            
        Returns:
            Dictionary with conversion results
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {"converted": [], "failed": []}
        
        # Get WDL files to convert
        wdl_dir = self.gatksv_path / "wdl"
        if modules:
            wdl_files = []
            for module in modules:
                wdl_files.extend(wdl_dir.glob(f"*{module}*.wdl"))
        else:
            wdl_files = list(wdl_dir.glob("*.wdl"))
        
        # Convert each WDL file
        for wdl_file in wdl_files:
            try:
                cwl_file = output_dir / wdl_file.with_suffix('.cwl').name
                self.converter.convert_file(wdl_file, cwl_file)
                results["converted"].append(str(wdl_file.name))
            except Exception as e:
                results["failed"].append({
                    "file": str(wdl_file.name),
                    "error": str(e)
                })
        
        return results
    
    def analyze_gatksv_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Analyze a GATK-SV workflow structure.
        
        Args:
            workflow_name: Name of the workflow file (without .wdl)
            
        Returns:
            Analysis results
        """
        wdl_file = self.gatksv_path / "wdl" / f"{workflow_name}.wdl"
        
        if not wdl_file.exists():
            raise FileNotFoundError(f"Workflow not found: {wdl_file}")
        
        # Use base class analyze_workflow method
        analysis = self.analyze_workflow(str(wdl_file))
        
        # Add SV-specific information
        if workflow_name in self.knowledge.module_descriptions:
            analysis['sv_info'] = self.knowledge.get_module_info(workflow_name)
        
        return analysis
    
    def _validate_sv_requirements(self, config: Dict[str, Any]) -> None:
        """Validate SV-specific requirements."""
        # SV-specific required fields
        sv_required = ["reference", "output_dir"]
        for field in sv_required:
            if field not in config:
                raise ValueError(f"Missing required field for SV analysis: {field}")
        
        # Check coverage requirements
        for sample in config['samples']:
            if 'coverage' in sample and sample['coverage'] < 30:
                raise ValueError(
                    f"Sample {sample['id']} has insufficient coverage ({sample['coverage']}x). "
                    "GATK-SV requires minimum 30x coverage."
                )
    
    def _validate_domain_inputs(self, inputs: Dict[str, Any]) -> None:
        """Validate SV-specific inputs."""
        # Check for required SV inputs
        if 'bam_files' in inputs:
            for bam in inputs['bam_files']:
                if not bam.endswith('.bam'):
                    raise ValueError(f"Invalid BAM file: {bam}")
    
    def _prepare_workflow_inputs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare inputs for GATK-SV workflow."""
        return {
            "samples": config["samples"],
            "reference": config["reference"],
            "output_directory": config["output_dir"],
            "sv_pipeline_docker": self.config.get('docker_image', 'gatksv/sv-pipeline:latest'),
            "primary_contigs_list": self.config.get('contigs', self._get_default_contigs()),
            # Add more GATK-SV specific inputs
        }
    
    def _get_default_contigs(self) -> List[str]:
        """Get default contig list for hg38."""
        return [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]