"""Natural language execution module for sv-agent."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from .agent import SVAgent
from .knowledge import SVKnowledgeBase

logger = logging.getLogger(__name__)


class NaturalLanguageExecutor:
    """Execute GATK-SV workflows based on natural language prompts."""
    
    def __init__(self, agent: SVAgent):
        """Initialize with an SVAgent instance."""
        self.agent = agent
        self.knowledge = SVKnowledgeBase()
        
        # Module patterns for common requests
        self.module_patterns = {
            "qc": ["Module00a", "GatherSampleEvidence"],
            "evidence": ["Module00b", "EvidenceQC"],
            "batch_qc": ["Module00c", "GatherBatchEvidence"],
            "clustering": ["Module01", "ClusterBatch"],
            "filtering": ["Module03", "FilterBatch"],
            "genotyping": ["Module04", "GenotypeBatch"],
            "annotation": ["AnnotateVcf"]
        }
    
    def parse_execution_request(self, prompt: str) -> Dict[str, Any]:
        """Parse natural language execution request into structured format.
        
        Args:
            prompt: Natural language request like "run QC on these 3 BAM files"
            
        Returns:
            Structured execution plan
        """
        prompt_lower = prompt.lower()
        
        # Identify module to run
        module = self._identify_module(prompt_lower)
        
        # Extract file paths
        files = self._extract_file_paths(prompt)
        
        # Determine operation type
        operation = self._determine_operation(prompt_lower)
        
        # Build execution plan
        plan = {
            "module": module,
            "operation": operation,
            "inputs": {
                "files": files,
                "parameters": self._extract_parameters(prompt)
            }
        }
        
        return plan
    
    def execute_from_prompt(self, prompt: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute GATK-SV workflow based on natural language prompt.
        
        Args:
            prompt: Natural language execution request
            dry_run: If True, only show what would be executed
            
        Returns:
            Execution results or plan
        """
        try:
            # Parse the request
            plan = self.parse_execution_request(prompt)
            
            if dry_run:
                return self._format_execution_plan(plan)
            
            # Execute based on module
            if plan["module"]:
                return self._execute_module(plan)
            else:
                return {
                    "status": "error",
                    "message": "Could not determine which module to run from your request"
                }
                
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _identify_module(self, prompt_lower: str) -> Optional[str]:
        """Identify which GATK-SV module to run."""
        # Check for explicit module mentions
        for pattern, modules in self.module_patterns.items():
            if pattern in prompt_lower:
                return modules[0]
        
        # Check for specific module names
        module_match = re.search(r'module\s*(\d+[a-c]?)', prompt_lower)
        if module_match:
            return f"Module{module_match.group(1).zfill(2)}"
        
        # Check for workflow names
        if "gathersampleevidence" in prompt_lower.replace(" ", ""):
            return "GatherSampleEvidence"
        elif "evidenceqc" in prompt_lower.replace(" ", ""):
            return "EvidenceQC"
        
        return None
    
    def _extract_file_paths(self, prompt: str) -> List[str]:
        """Extract file paths from prompt."""
        files = []
        
        # Look for quoted paths
        quoted_paths = re.findall(r'["\']([^"\']+)["\']', prompt)
        files.extend(quoted_paths)
        
        # Look for paths with extensions
        path_pattern = r'[\w/\-\.]+\.(bam|cram|vcf|bed|fa|fasta)'
        paths = re.findall(path_pattern, prompt, re.IGNORECASE)
        files.extend(paths)
        
        # Look for numbered files (e.g., "these 3 files")
        if "these" in prompt and "files" in prompt:
            # Extract any paths after "these X files"
            after_files = prompt.split("files")[-1]
            paths = re.findall(r'[\w/\-\.]+', after_files)
            files.extend([p for p in paths if '.' in p])
        
        return list(set(files))  # Remove duplicates
    
    def _extract_parameters(self, prompt: str) -> Dict[str, Any]:
        """Extract parameters from prompt."""
        params = {}
        
        # Extract reference genome
        if "hg38" in prompt.lower():
            params["reference"] = "hg38"
        elif "hg19" in prompt.lower() or "grch37" in prompt.lower():
            params["reference"] = "hg19"
        
        # Extract output directory
        output_match = re.search(r'output\s+(?:to|in|directory)?\s*["\']?([^\s"\']+)', prompt, re.IGNORECASE)
        if output_match:
            params["output_dir"] = output_match.group(1)
        
        # Extract sample names
        sample_match = re.search(r'sample\s+(?:name|id)?\s*["\']?(\w+)', prompt, re.IGNORECASE)
        if sample_match:
            params["sample_id"] = sample_match.group(1)
        
        return params
    
    def _determine_operation(self, prompt_lower: str) -> str:
        """Determine what operation to perform."""
        if any(word in prompt_lower for word in ["run", "execute", "process", "analyze"]):
            return "execute"
        elif any(word in prompt_lower for word in ["check", "validate", "verify"]):
            return "validate"
        elif any(word in prompt_lower for word in ["convert", "transform"]):
            return "convert"
        else:
            return "execute"  # Default
    
    def _execute_module(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific GATK-SV module."""
        module = plan["module"]
        inputs = plan["inputs"]
        
        # Get CWL file for module
        cwl_dir = Path("src/sv_agent/cwl")
        cwl_file = cwl_dir / f"{module}.cwl"
        
        if not cwl_file.exists():
            # Try to convert it first
            self.agent.convert_gatksv_to_cwl(cwl_dir, [module])
            if not cwl_file.exists():
                return {
                    "status": "error",
                    "message": f"CWL file not found for {module}. Conversion may have failed."
                }
        
        # Prepare inputs YAML
        input_config = self._prepare_module_inputs(module, inputs)
        
        # Execute using agent's execution engine
        if self.agent.execution_engine:
            result = self.agent.execute_workflow(
                str(cwl_file),
                input_config,
                output_dir=inputs.get("parameters", {}).get("output_dir")
            )
            
            return {
                "status": "success" if result.success else "failed",
                "module": module,
                "outputs": result.outputs,
                "logs": result.logs,
                "message": f"Module {module} execution completed"
            }
        else:
            return {
                "status": "error",
                "message": "No execution engine available. Install cwltool: pip install cwltool"
            }
    
    def _prepare_module_inputs(self, module: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input configuration for a specific module."""
        files = inputs.get("files", [])
        params = inputs.get("parameters", {})
        
        # Module-specific input preparation
        if module in ["Module00a", "GatherSampleEvidence"]:
            # Sample QC module
            return {
                "bam_or_cram_file": {
                    "class": "File",
                    "path": files[0] if files else None
                },
                "sample_id": params.get("sample_id", "sample1"),
                "reference_fasta": {
                    "class": "File", 
                    "path": f"/references/{params.get('reference', 'hg38')}.fa"
                }
            }
        
        elif module in ["Module00b", "EvidenceQC"]:
            # Evidence QC module
            return {
                "evidence_files": [
                    {"class": "File", "path": f} for f in files
                ],
                "batch_id": params.get("batch_id", "batch1")
            }
        
        # Add more module-specific configurations as needed
        
        # Default configuration
        return {
            "input_files": [{"class": "File", "path": f} for f in files],
            **params
        }
    
    def _format_execution_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Format execution plan for dry run display."""
        module_info = self.knowledge.get_module_info(plan["module"]) if plan["module"] else {}
        
        return {
            "status": "dry_run",
            "plan": {
                "module": plan["module"],
                "module_info": module_info,
                "operation": plan["operation"],
                "inputs": plan["inputs"],
                "commands": self._generate_commands(plan)
            },
            "message": "Dry run - no execution performed"
        }
    
    def _generate_commands(self, plan: Dict[str, Any]) -> List[str]:
        """Generate commands that would be executed."""
        commands = []
        
        # Convert command if needed
        if plan["operation"] == "convert":
            commands.append(f"sv-agent convert -m {plan['module']}")
        
        # Execution command
        if plan["operation"] == "execute":
            cwl_file = f"src/sv_agent/cwl/{plan['module']}.cwl"
            input_yaml = f"{plan['module']}_inputs.yaml"
            commands.append(f"sv-agent run {cwl_file} {input_yaml}")
        
        return commands