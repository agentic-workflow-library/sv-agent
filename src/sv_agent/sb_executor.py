"""Seven Bridges platform execution module for sv-agent."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class SevenBridgesExecutor:
    """Execute GATK-SV workflows on Seven Bridges platforms."""
    
    def __init__(self, agent=None):
        """Initialize Seven Bridges executor."""
        self.agent = agent
        
        # Available Seven Bridges platforms
        self.platforms = {
            "cgc": {
                "name": "Cancer Genomics Cloud",
                "url": "https://cgc-api.sbgenomics.com/v2",
                "description": "NIH Cancer Genomics Cloud for cancer research",
                "pricing": "Free tier available with TCGA/TARGET data access"
            },
            "cavatica": {
                "name": "CAVATICA", 
                "url": "https://cavatica-api.sbgenomics.com/v2",
                "description": "Kids First Data Resource Center platform for pediatric research",
                "pricing": "Free tier available with Kids First data access"
            },
            "aws": {
                "name": "Seven Bridges Platform (AWS)",
                "url": "https://api.sbgenomics.com/v2", 
                "description": "Commercial platform on AWS infrastructure",
                "pricing": "Pay-per-use pricing"
            },
            "gcp": {
                "name": "Seven Bridges Platform (GCP)",
                "url": "https://gcp-api.sbgenomics.com/v2",
                "description": "Commercial platform on Google Cloud infrastructure", 
                "pricing": "Pay-per-use pricing"
            },
            "azure": {
                "name": "Seven Bridges Platform (Azure)",
                "url": "https://eu-api.sbgenomics.com/v2",
                "description": "Commercial platform on Azure infrastructure",
                "pricing": "Pay-per-use pricing"
            }
        }
        
        # Instance types for different workloads
        self.instance_types = {
            "small": {
                "name": "c5.xlarge",
                "cpu": 4,
                "memory": 8,
                "description": "Small workloads, single sample QC"
            },
            "medium": {
                "name": "c5.4xlarge", 
                "cpu": 16,
                "memory": 32,
                "description": "Medium workloads, batch processing"
            },
            "large": {
                "name": "c5.9xlarge",
                "cpu": 36,
                "memory": 72,
                "description": "Large workloads, cohort analysis"
            },
            "memory": {
                "name": "r5.4xlarge",
                "cpu": 16,
                "memory": 128,
                "description": "Memory-intensive tasks, large references"
            }
        }
    
    def initiate_execution_dialog(self, prompt: str) -> Dict[str, Any]:
        """Start interactive dialog for Seven Bridges execution."""
        
        # Parse initial request
        execution_plan = self._parse_sb_request(prompt)
        
        # Determine what information we need
        missing_info = self._check_required_info(execution_plan)
        
        if missing_info:
            return {
                "status": "needs_info",
                "plan": execution_plan,
                "questions": self._generate_questions(missing_info),
                "message": "I need some additional information to execute on Seven Bridges platform."
            }
        else:
            return {
                "status": "ready",
                "plan": execution_plan,
                "message": "Ready to execute on Seven Bridges. Confirm to proceed."
            }
    
    def _parse_sb_request(self, prompt: str) -> Dict[str, Any]:
        """Parse Seven Bridges execution request."""
        prompt_lower = prompt.lower()
        
        # Extract platform preference
        platform = None
        for key, info in self.platforms.items():
            if key in prompt_lower or info["name"].lower() in prompt_lower:
                platform = key
                break
        
        # Extract module/workflow
        module = self._extract_module(prompt)
        
        # Extract files
        files = self._extract_file_references(prompt)
        
        # Extract project reference
        project = self._extract_project(prompt)
        
        # Extract instance size preference
        instance_size = self._extract_instance_size(prompt)
        
        return {
            "platform": platform,
            "module": module,
            "files": files,
            "project": project,
            "instance_size": instance_size,
            "original_prompt": prompt
        }
    
    def _extract_module(self, prompt: str) -> Optional[str]:
        """Extract GATK-SV module from prompt."""
        prompt_lower = prompt.lower()
        
        # Direct module references
        module_match = re.search(r'module\s*(\d+[a-c]?)', prompt_lower)
        if module_match:
            return f"Module{module_match.group(1).zfill(2)}"
        
        # Module keywords
        module_keywords = {
            "qc": "Module00a",
            "sample qc": "Module00a", 
            "evidence": "Module00b",
            "batch qc": "Module00c",
            "clustering": "Module01",
            "filtering": "Module03",
            "genotyping": "Module04"
        }
        
        for keyword, module in module_keywords.items():
            if keyword in prompt_lower:
                return module
        
        # Workflow names
        if "gathersampleevidence" in prompt_lower.replace(" ", ""):
            return "GatherSampleEvidence"
        
        return None
    
    def _extract_file_references(self, prompt: str) -> List[str]:
        """Extract file references (could be platform paths or local)."""
        files = []
        
        # Seven Bridges file paths (sbg://)
        sb_files = re.findall(r'sbg://[\w\-/\.]+', prompt)
        files.extend(sb_files)
        
        # Regular file paths
        file_patterns = [
            r'[\w/\-\.]+\.(bam|cram|vcf|bed|fa|fasta)',
            r'["\']([^"\']+\.(bam|cram|vcf|bed|fa|fasta))["\']'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if isinstance(matches[0], tuple) if matches else False:
                files.extend([m[0] for m in matches])
            else:
                files.extend(matches)
        
        return list(set(files))
    
    def _extract_project(self, prompt: str) -> Optional[str]:
        """Extract Seven Bridges project reference."""
        # Project ID pattern (username/project)
        project_match = re.search(r'project\s+([a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+)', prompt)
        if project_match:
            return project_match.group(1)
        
        # Direct project reference
        project_match = re.search(r'([a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+)', prompt)
        if project_match and "/" in project_match.group(1):
            return project_match.group(1)
        
        return None
    
    def _extract_instance_size(self, prompt: str) -> Optional[str]:
        """Extract instance size preference."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["large", "big", "high memory", "intensive"]):
            return "large"
        elif any(word in prompt_lower for word in ["small", "quick", "test"]):
            return "small"
        elif any(word in prompt_lower for word in ["medium", "batch"]):
            return "medium"
        elif any(word in prompt_lower for word in ["memory", "ram"]):
            return "memory"
        
        return None
    
    def _check_required_info(self, plan: Dict[str, Any]) -> List[str]:
        """Check what information is still needed."""
        missing = []
        
        if not plan["platform"]:
            missing.append("platform")
        
        if not plan["module"]:
            missing.append("module") 
        
        if not plan["files"]:
            missing.append("files")
        
        if not plan["project"]:
            missing.append("project")
        
        if not plan["instance_size"]:
            missing.append("instance_size")
        
        return missing
    
    def _generate_questions(self, missing_info: List[str]) -> List[Dict[str, Any]]:
        """Generate questions to gather missing information."""
        questions = []
        
        if "platform" in missing_info:
            questions.append({
                "type": "choice",
                "question": "Which Seven Bridges platform would you like to use?",
                "options": [
                    f"{key}: {info['name']} - {info['description']}" 
                    for key, info in self.platforms.items()
                ],
                "field": "platform"
            })
        
        if "module" in missing_info:
            questions.append({
                "type": "choice", 
                "question": "Which GATK-SV module would you like to run?",
                "options": [
                    "Module00a: Sample QC (GatherSampleEvidence)",
                    "Module00b: Evidence Collection", 
                    "Module00c: Batch QC",
                    "Module01: Clustering",
                    "Module03: Filtering", 
                    "Module04: Genotyping"
                ],
                "field": "module"
            })
        
        if "files" in missing_info:
            questions.append({
                "type": "text",
                "question": "What input files would you like to process? (Provide Seven Bridges file paths like sbg://project/file.bam or describe the files)",
                "field": "files"
            })
        
        if "project" in missing_info:
            questions.append({
                "type": "text", 
                "question": "What Seven Bridges project should I use? (Format: username/project-name)",
                "field": "project"
            })
        
        if "instance_size" in missing_info:
            questions.append({
                "type": "choice",
                "question": "What instance size would you like to use?",
                "options": [
                    f"{key}: {info['name']} ({info['cpu']} CPU, {info['memory']} GB RAM) - {info['description']}"
                    for key, info in self.instance_types.items()
                ],
                "field": "instance_size"
            })
        
        return questions
    
    def update_plan_with_response(self, plan: Dict[str, Any], field: str, response: str) -> Dict[str, Any]:
        """Update execution plan with user response."""
        updated_plan = plan.copy()
        
        if field == "platform":
            # Extract platform key from response
            if response.strip().isdigit():
                # Handle numeric response
                platform_keys = list(self.platforms.keys())
                choice = int(response.strip()) - 1
                if 0 <= choice < len(platform_keys):
                    updated_plan["platform"] = platform_keys[choice]
            else:
                # Handle text response
                for key in self.platforms.keys():
                    if key in response.lower():
                        updated_plan["platform"] = key
                        break
        
        elif field == "module":
            # Extract module from response
            if "module00a" in response.lower() or "sample qc" in response.lower():
                updated_plan["module"] = "Module00a"
            elif "module00b" in response.lower() or "evidence collection" in response.lower():
                updated_plan["module"] = "Module00b"
            # Add more module mappings...
        
        elif field == "files":
            # Parse file list from response
            files = []
            # Seven Bridges paths
            sb_files = re.findall(r'sbg://[\w\-/\.]+', response)
            files.extend(sb_files)
            # Regular paths
            file_matches = re.findall(r'[\w/\-\.]+\.(bam|cram|vcf|bed|fa|fasta)', response)
            files.extend(file_matches)
            updated_plan["files"] = files
        
        elif field == "project":
            # Extract project ID
            project_match = re.search(r'([a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+)', response)
            if project_match:
                updated_plan["project"] = project_match.group(1)
        
        elif field == "instance_size":
            # Extract instance size
            for key in self.instance_types.keys():
                if key in response.lower():
                    updated_plan["instance_size"] = key
                    break
        
        return updated_plan
    
    def generate_execution_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed execution plan for Seven Bridges."""
        platform_info = self.platforms[plan["platform"]]
        instance_info = self.instance_types[plan["instance_size"]]
        
        # Estimate costs
        cost_estimate = self._estimate_costs(plan)
        
        execution_plan = {
            "platform": {
                "name": platform_info["name"],
                "url": platform_info["url"]
            },
            "project": plan["project"],
            "workflow": {
                "module": plan["module"],
                "app_id": f"gatk-sv/{plan['module'].lower()}"
            },
            "inputs": {
                "files": plan["files"],
                "instance_type": instance_info["name"]
            },
            "costs": cost_estimate,
            "steps": [
                "1. Upload CWL workflow to Seven Bridges platform",
                "2. Configure workflow inputs and parameters", 
                "3. Set compute instance requirements",
                "4. Submit workflow execution",
                "5. Monitor execution progress",
                "6. Download results when complete"
            ]
        }
        
        return execution_plan
    
    def _estimate_costs(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate execution costs."""
        instance_info = self.instance_types[plan["instance_size"]]
        
        # Rough time estimates by module (hours)
        time_estimates = {
            "Module00a": 2,
            "Module00b": 4, 
            "Module00c": 1,
            "Module01": 6,
            "Module03": 3,
            "Module04": 8
        }
        
        estimated_hours = time_estimates.get(plan["module"], 4)
        
        # Rough cost per hour by instance type (USD)
        cost_per_hour = {
            "small": 0.20,
            "medium": 0.80,
            "large": 1.80,
            "memory": 1.20
        }
        
        hourly_rate = cost_per_hour[plan["instance_size"]]
        estimated_cost = estimated_hours * hourly_rate
        
        return {
            "estimated_hours": estimated_hours,
            "hourly_rate": hourly_rate,
            "estimated_cost_usd": round(estimated_cost, 2),
            "note": "Estimates are approximate and exclude storage costs"
        }
    
    def generate_sb_commands(self, plan: Dict[str, Any]) -> List[str]:
        """Generate Seven Bridges CLI commands."""
        platform_url = self.platforms[plan["platform"]]["url"]
        
        commands = [
            f"# Set Seven Bridges profile",
            f"sb config set endpoint {platform_url}",
            f"sb config set token YOUR_AUTH_TOKEN",
            f"",
            f"# Upload CWL workflow",
            f"sb apps install-workflow src/sv_agent/cwl/{plan['module']}.cwl {plan['project']}",
            f"",
            f"# Create and submit task",
            f"sb tasks create \\",
            f"  --project {plan['project']} \\",
            f"  --app {plan['project']}/{plan['module'].lower()} \\",
            f"  --name '{plan['module']}-execution' \\",
            f"  --inputs '{json.dumps(self._format_sb_inputs(plan))}' \\",
            f"  --instance-type {self.instance_types[plan['instance_size']]['name']}",
            f"",
            f"# Monitor execution",
            f"sb tasks list --project {plan['project']} --status RUNNING"
        ]
        
        return commands
    
    def _format_sb_inputs(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Format inputs for Seven Bridges execution."""
        inputs = {}
        
        if plan["files"]:
            # For now, assume first file is main input
            inputs["bam_or_cram_file"] = plan["files"][0]
        
        inputs["sample_id"] = "sample1"  # Could be extracted from filename
        
        return inputs