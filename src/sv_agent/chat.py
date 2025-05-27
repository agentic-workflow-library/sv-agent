"""Chat interface for SV-Agent - Interactive domain-specific agent."""

import asyncio
import json
from typing import Dict, Any, Optional
import re
import logging

from awlkit.agents import ChatInterface
from awlkit.llm.utils import format_prompt_for_sv_domain

from .agent import SVAgent
from .knowledge import SVKnowledgeBase


logger = logging.getLogger(__name__)


class SVAgentChat(ChatInterface):
    """Interactive chat interface for SV-Agent."""
    
    def __init__(self, agent: Optional[SVAgent] = None, llm_config: Optional[Dict[str, Any]] = None):
        """Initialize SV-specific chat interface with LLM provider."""
        # Initialize base chat interface
        sv_agent = agent or SVAgent()
        
        config = llm_config or {}
        
        # Determine which provider to use
        provider_type = config.get("provider", "local")
        
        if provider_type == "api" or config.get("use_api", False):
            # Use HF Inference API for fast responses
            from awlkit.llm import get_hf_inference_provider
            HFInferenceProvider = get_hf_inference_provider()
            
            # Use a model that works without auth if no token provided
            default_api_model = "microsoft/Phi-3.5-mini-instruct" if not config.get("api_token") else "mistralai/Mixtral-8x7B-Instruct-v0.1"
            
            llm = HFInferenceProvider(
                model_id=config.get("model_id", default_api_model),
                api_token=config.get("api_token")
            )
            logger.info(f"Using HF Inference API with model {llm.model_id}")
        else:
            # Use local HuggingFace model
            from awlkit.llm import get_huggingface_provider
            HuggingFaceProvider = get_huggingface_provider()
            
            # Try to find local models intelligently
            from pathlib import Path
            import os
            
            default_model = None
            
            # First check if a model is specified in config
            if config.get("model_id"):
                default_model = config["model_id"]
            else:
                # Look for local models in common locations
                model_dirs = [
                    Path("models"),
                    Path("./models"),
                    Path(os.path.expanduser("~/.cache/huggingface")),
                    Path("/workspaces/sv-agent/models")
                ]
                
                for model_dir in model_dirs:
                    if model_dir.exists():
                        # Look for any subdirectory that looks like a model
                        for item in model_dir.iterdir():
                            if item.is_dir() and any(f in item.name.lower() for f in ["gemma", "llama", "phi", "mistral"]):
                                # Check if it has model files
                                if any(item.glob("*.bin")) or any(item.glob("*.safetensors")) or (item / "config.json").exists():
                                    default_model = str(item)
                                    logger.info(f"Found local model: {default_model}")
                                    break
                        if default_model:
                            break
                
                # If no local model found, use a small public model
                if not default_model:
                    default_model = "microsoft/phi-2"
                    logger.warning(f"No local model found, defaulting to {default_model}. This will download ~5GB on first use.")
                
            llm = HuggingFaceProvider(
                model_id=config.get("model_id", default_model),
                device=config.get("device"),
                load_in_8bit=config.get("load_in_8bit", False),
                load_in_4bit=config.get("load_in_4bit", False),
                trust_remote_code=config.get("trust_remote_code", False),
                cache_dir=config.get("cache_dir"),
                auth_token=config.get("auth_token")
            )
        
        super().__init__(sv_agent, llm)
        
        # SV-specific attributes
        self.knowledge = SVKnowledgeBase()
        self.context = {
            "current_module": None,
            "workflow_state": None,
            "last_results": None
        }
        
        # Register SV-specific handlers
        self._register_sv_handlers()
        
        # Natural language executor
        from .nl_executor import NaturalLanguageExecutor
        self.nl_executor = NaturalLanguageExecutor(self.agent)
        
        # Seven Bridges executor
        from .sb_executor import SevenBridgesExecutor
        self.sb_executor = SevenBridgesExecutor(self.agent)
        
        # Multi-step execution state
        self.execution_state = {
            "mode": None,  # "local", "sb" 
            "plan": None,
            "step": 0,
            "awaiting_response": None
        }
        
    def chat(self, query: str) -> str:
        """Compatibility method that forwards to process_query."""
        return self.process_query(query)
    
    def process_query(self, query: str) -> str:
        """Override to handle multi-step execution dialogs."""
        # Check if we're in the middle of a multi-step execution
        if self.execution_state["awaiting_response"]:
            return self._handle_execution_response(query)
        
        # Check for Seven Bridges execution requests
        query_lower = query.lower()
        sb_keywords = ["seven bridges", "sb", "cgc", "cavatica", "platform", "cloud"]
        execution_keywords = ["run", "execute", "process"]
        
        if (any(sb in query_lower for sb in sb_keywords) and 
            any(exec in query_lower for exec in execution_keywords)):
            return self._initiate_sb_execution(query)
        
        # Otherwise, use the parent implementation
        return super().process_query(query)
    
    def _initiate_sb_execution(self, query: str) -> str:
        """Initiate Seven Bridges execution dialog."""
        result = self.sb_executor.initiate_execution_dialog(query)
        
        if result["status"] == "needs_info":
            # Set up multi-step dialog state
            self.execution_state = {
                "mode": "sb",
                "plan": result["plan"],
                "step": 0,
                "awaiting_response": result["questions"][0]["field"]
            }
            
            # Format the first question
            question = result["questions"][0]
            response = f"**Seven Bridges Execution Setup**\n\n{result['message']}\n\n"
            response += f"**{question['question']}**\n\n"
            
            if question["type"] == "choice":
                for i, option in enumerate(question["options"], 1):
                    response += f"{i}. {option}\n"
                response += "\nPlease respond with a number or the platform name."
            else:
                response += "Please provide your answer."
            
            return response
            
        elif result["status"] == "ready":
            return self._show_sb_execution_plan(result["plan"])
        
        else:
            return "Sorry, I couldn't parse your Seven Bridges execution request."
    
    def _handle_execution_response(self, response: str) -> str:
        """Handle user response in multi-step execution dialog."""
        field = self.execution_state["awaiting_response"]
        plan = self.execution_state["plan"]
        
        # Update plan with user response
        updated_plan = self.sb_executor.update_plan_with_response(plan, field, response)
        self.execution_state["plan"] = updated_plan
        self.execution_state["step"] += 1
        
        # Check if we need more information
        missing_info = self.sb_executor._check_required_info(updated_plan)
        
        if missing_info:
            # Ask the next question
            questions = self.sb_executor._generate_questions(missing_info)
            next_question = questions[0]
            
            self.execution_state["awaiting_response"] = next_question["field"]
            
            response_text = f"**Step {self.execution_state['step'] + 1}**: {next_question['question']}\n\n"
            
            if next_question["type"] == "choice":
                for i, option in enumerate(next_question["options"], 1):
                    response_text += f"{i}. {option}\n"
                response_text += "\nPlease respond with a number or keyword."
            else:
                response_text += "Please provide your answer."
            
            return response_text
        else:
            # All information collected, show execution plan
            self.execution_state["awaiting_response"] = None
            return self._show_sb_execution_plan(updated_plan)
    
    def _show_sb_execution_plan(self, plan: Dict[str, Any]) -> str:
        """Show complete Seven Bridges execution plan."""
        execution_plan = self.sb_executor.generate_execution_plan(plan)
        commands = self.sb_executor.generate_sb_commands(plan)
        
        response = "**🚀 Seven Bridges Execution Plan**\n\n"
        
        # Platform info
        response += f"**Platform:** {execution_plan['platform']['name']}\n"
        response += f"**Project:** {execution_plan['project']}\n"
        response += f"**Module:** {execution_plan['workflow']['module']}\n\n"
        
        # Files
        response += "**Input Files:**\n"
        for file in execution_plan['inputs']['files']:
            response += f"- {file}\n"
        response += "\n"
        
        # Cost estimate
        costs = execution_plan['costs']
        response += f"**Cost Estimate:**\n"
        response += f"- Instance: {execution_plan['inputs']['instance_type']}\n"
        response += f"- Estimated time: {costs['estimated_hours']} hours\n"
        response += f"- Estimated cost: ${costs['estimated_cost_usd']}\n"
        response += f"- Note: {costs['note']}\n\n"
        
        # Steps
        response += "**Execution Steps:**\n"
        for step in execution_plan['steps']:
            response += f"{step}\n"
        response += "\n"
        
        # Commands
        response += "**Seven Bridges CLI Commands:**\n```bash\n"
        response += "\n".join(commands)
        response += "\n```\n\n"
        
        response += "**Next Steps:**\n"
        response += "1. Ensure you have Seven Bridges CLI installed: `pip install sevenbridges-python`\n"
        response += "2. Set up authentication token\n"
        response += "3. Run the commands above\n"
        response += "4. Or say 'execute this plan' to have me guide you through it\n\n"
        
        response += "Would you like me to proceed with execution or modify anything?"
        
        # Reset execution state
        self.execution_state = {
            "mode": None,
            "plan": None, 
            "step": 0,
            "awaiting_response": None
        }
        
        return response
    
    def _register_sv_handlers(self):
        """Register SV-specific intent handlers."""
        # Override base handlers with SV-specific ones
        self.register_handler('help', self._handle_sv_help)
        self.register_handler('explain', self._handle_explain)
        self.register_handler('convert', self._handle_sv_convert)
        self.register_handler('analyze', self._handle_sv_analyze)
        self.register_handler('run', self._handle_run)
        self.register_handler('status', self._handle_status)
        self.register_handler('recommend', self._handle_recommend)
        self.register_handler('troubleshoot', self._handle_troubleshoot)
    
    def _handle_general_query(self, query: str) -> str:
        """Override base method to handle SV-specific queries."""
        # Get relevant SV knowledge
        knowledge_context = self._get_relevant_knowledge(query)
        
        # Format prompt with SV domain context
        context = self.memory.get_context()
        prompt = format_prompt_for_sv_domain(
            query,
            context=f"{context}\n\nRelevant Knowledge:\n{knowledge_context}"
        )
        
        try:
            # Generate response
            if asyncio.iscoroutinefunction(self.llm.generate):
                response = asyncio.run(self.llm.generate(prompt))
            else:
                response = self.llm.generate(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # If it's an API auth error, provide helpful guidance and fall back to knowledge base
            if "401" in str(e) or "Invalid username" in str(e):
                logger.info("API requires authentication, falling back to knowledge base")
                kb_response = self._handle_knowledge_search(query)
                
                return f"{kb_response}\n\n💡 **Tip:** For faster AI-powered responses, get a free API token:\n1. Visit https://huggingface.co/settings/tokens\n2. Create a token with 'read' permissions\n3. Run: export HF_TOKEN='your_token_here'\n4. Use: sv-agent --use-api ask 'your question'"
            else:
                # For other errors, report them clearly
                return f"❌ **Error: Cannot generate response**\n\nThe LLM model failed to load or generate a response.\n\nError: {str(e)}\n\nPlease ensure you have a valid model installed. You can:\n1. Specify a model with --model flag\n2. Download a model from Hugging Face\n3. Check that your model path is correct"
    
    def _get_relevant_knowledge(self, query: str) -> str:
        """Get relevant knowledge context for the query."""
        query_lower = query.lower()
        context_parts = []
        
        # Always include capabilities for tool-related questions
        if any(word in query_lower for word in ["can", "run", "execute", "tool", "what", "do", "capability"]):
            context_parts.append("SV-AGENT CAPABILITIES:")
            context_parts.append("Main function: Execute CWL workflows to run GATK-SV analysis")
            context_parts.append("Can do: " + ", ".join(self.knowledge.capabilities["what_i_can_do"][:3]))
            context_parts.append("Cannot do: " + ", ".join(self.knowledge.capabilities["what_i_cannot_do"][:2]))
            context_parts.append(f"Run command: {self.knowledge.capabilities['execution_details']['run_command']}")
            context_parts.append(f"Convert command: {self.knowledge.capabilities['conversion_details']['command']}")
            context_parts.append("")
        
        # Search for other relevant knowledge
        results = self.knowledge.search_knowledge(query)
        
        for result in results[:3]:
            if result["type"] == "Module":
                context_parts.append(
                    f"{result['id']}: {result['info']['name']} - {result['info']['purpose']}"
                )
            elif result["type"] == "FAQ":
                context_parts.append(f"Q: {result['question']} A: {result['answer']}")
        
        return "\n".join(context_parts)
    
    def _parse_intent(self, query: str) -> str:
        """Override base method with SV-specific intent detection."""
        query_lower = query.lower()
        
        # For general questions like "what is X", use the LLM
        if query_lower.startswith(("what is", "what are", "how do", "why", "when", "who", "define", "explain what")):
            return "general"
        
        # Check for specific command-like intents
        if "explain module" in query_lower or "describe module" in query_lower:
            return "explain"
        elif any(word in query_lower for word in ["convert", "transform"]):
            return "convert" 
        elif any(word in query_lower for word in ["analyze", "analysis"]):
            return "analyze"
        elif any(word in query_lower for word in ["run", "execute"]):
            return "run"
        elif any(word in query_lower for word in ["recommend", "best practice", "should i"]):
            return "recommend"
        elif any(word in query_lower for word in ["error", "failed", "problem", "troubleshoot"]):
            return "troubleshoot"
        elif any(word in query_lower for word in ["help", "what can you"]):
            return "help"
        
        # Default to general LLM handling for open-ended questions
        return "general"
    
    def _handle_sv_help(self, query: str) -> str:
        """Handle SV-specific help requests."""
        return """I'm SV-Agent, your domain-specific agent for structural variant analysis using GATK-SV.

Here's what I can help you with:

**📊 Analysis Tasks:**
- Run GATK-SV pipeline on your samples
- Convert WDL workflows to CWL format
- Analyze workflow structure and dependencies
- Check sample quality metrics

**💡 Knowledge & Guidance:**
- Explain SV types (DEL, DUP, INV, INS, BND)
- Describe GATK-SV modules and their purposes
- Recommend best practices for your analysis
- Troubleshoot common issues

**🔧 Practical Examples:**
- "Explain Module00a"
- "Convert Module00b to CWL"
- "What coverage do I need for SV detection?"
- "How do I handle family samples?"
- "Troubleshoot low variant calls"

**💬 Just ask naturally:**
- "What are structural variants?"
- "How long will my analysis take?"
- "Should I include related samples?"

Type your question or command, and I'll help you with your SV analysis!"""
    
    def _handle_explain(self, query: str) -> str:
        """Handle SV-specific explanation requests."""
        
        # Check for module explanations
        module_match = re.search(r'module\s*(\d+[a-c]?)', query, re.IGNORECASE)
        if module_match:
            module_id = f"Module{module_match.group(1).zfill(2)}"
            module_info = self.knowledge.get_module_info(module_id)
            if module_info:
                return self._format_module_explanation(module_id, module_info)
        
        # Check for SV type explanations
        for sv_type in ["DEL", "DUP", "INV", "INS", "BND"]:
            if sv_type.lower() in query.lower():
                sv_info = self.knowledge.get_sv_type_info(sv_type)
                if sv_info:
                    return self._format_sv_explanation(sv_type, sv_info)
        
        # General knowledge search
        return self._handle_knowledge_search(query)
    
    def _handle_sv_convert(self, query: str) -> str:
        """Handle SV workflow conversion requests."""
        
        # Extract module names
        modules = re.findall(r'module\s*(\d+[a-c]?)', query, re.IGNORECASE)
        
        if modules:
            module_names = [f"Module{m.zfill(2)}" for m in modules]
            return f"""I'll convert the following GATK-SV modules to CWL format: {', '.join(module_names)}

To proceed, you can:

**Python code:**
```python
from sv_agent import SVAgent

agent = SVAgent()
results = agent.convert_gatksv_to_cwl(
    output_dir=Path("cwl_output"),
    modules={module_names}
)

print(f"Converted: {{len(results['converted'])}} files")
print(f"Failed: {{len(results['failed'])}} files")
```

**Command line:**
```bash
sv-agent convert --output cwl_output --modules {' '.join(module_names)}
```

The converted CWL files will be compatible with standard CWL runners like cwltool or Toil."""
        
        else:
            return """To convert GATK-SV workflows to CWL, specify which modules you want to convert.

**Examples:**
- "Convert Module00a to CWL"
- "Convert all modules to CWL"
- "Convert Module01 and Module02"

**Or use Python directly:**
```python
agent.convert_gatksv_to_cwl(output_dir=Path("cwl_output"))
```"""
    
    def _handle_sv_analyze(self, query: str) -> str:
        """Handle SV-specific analysis requests."""
        
        # Check for workflow analysis
        if "workflow" in query.lower():
            return """To analyze a GATK-SV workflow structure:

```python
# Analyze the main batch workflow
analysis = agent.analyze_gatksv_workflow("GATKSVPipelineBatch")

print(f"Workflow: {analysis['name']}")
print(f"Total inputs: {analysis['inputs']}")
print(f"Total tasks: {analysis['tasks']}")
print(f"Max parallelism: {analysis['statistics']['max_parallelism']}")
```

This will show you:
- Input/output requirements
- Task dependencies
- Parallelization opportunities
- Potential bottlenecks"""
        
        # Check for sample/data analysis
        elif any(word in query.lower() for word in ["sample", "data", "bam", "vcf"]):
            return """To analyze your samples before running GATK-SV:

**1. Check BAM/CRAM files:**
```python
# Verify coverage and quality
samtools stats input.bam | grep "average length"
samtools flagstat input.bam
```

**2. Prepare sample metadata:**
```json
{
  "samples": [
    {
      "id": "SAMPLE001",
      "bam": "/path/to/sample001.bam",
      "sex": "female",
      "batch": "batch1"
    }
  ]
}
```

**3. Run preliminary QC:**
- Minimum 30x coverage recommended
- Check for proper pair alignment
- Verify reference genome match"""
        
        return "What would you like to analyze? Please specify workflows, samples, or results."
    
    def _handle_run(self, query: str) -> str:
        """Handle SV pipeline run requests."""
        # Check if this is a natural language execution request
        query_lower = query.lower()
        
        # Keywords that indicate execution intent
        execution_keywords = ["run", "execute", "process", "analyze", "perform"]
        has_files = any(ext in query for ext in [".bam", ".cram", ".vcf", ".bed"])
        has_module = any(word in query_lower for word in ["qc", "evidence", "module", "clustering", "genotyping"])
        
        if any(keyword in query_lower for keyword in execution_keywords) and (has_files or has_module):
            # This looks like an execution request
            # Check if it's a dry run request
            dry_run = "dry run" in query_lower or "show me" in query_lower or "would" in query_lower
            
            try:
                result = self.nl_executor.execute_from_prompt(query, dry_run=dry_run)
                
                if result["status"] == "dry_run":
                    plan = result["plan"]
                    response = f"**Execution Plan for: {plan['module']}**\n\n"
                    
                    if plan["module_info"]:
                        response += f"Module: {plan['module_info']['name']}\n"
                        response += f"Purpose: {plan['module_info']['purpose']}\n\n"
                    
                    response += "**Detected Inputs:**\n"
                    for file in plan["inputs"]["files"]:
                        response += f"- {file}\n"
                    
                    if plan["inputs"]["parameters"]:
                        response += "\n**Parameters:**\n"
                        for key, value in plan["inputs"]["parameters"].items():
                            response += f"- {key}: {value}\n"
                    
                    response += "\n**Commands to execute:**\n```bash\n"
                    response += "\n".join(plan["commands"])
                    response += "\n```\n\n"
                    response += "To execute this plan, confirm by saying 'yes, run it' or run the commands above."
                    
                    return response
                    
                elif result["status"] == "success":
                    return f"✅ **Execution Complete**\n\nModule: {result['module']}\n\nOutputs:\n{json.dumps(result['outputs'], indent=2)}"
                    
                else:
                    return f"❌ **Execution Failed**\n\n{result['message']}"
                    
            except Exception as e:
                logger.error(f"Natural language execution failed: {e}")
                # Fall back to help text
        
        # Default help text for general run queries
        return """sv-agent can execute CWL workflows to run GATK-SV analysis.

**🖥️ Local Execution:**
Try commands like:
- "Run QC on sample1.bam"
- "Execute Module00a with these files: file1.bam, file2.bam"
- "Process evidence QC on my batch"
- "Show me how to run genotyping on these samples"

**☁️ Seven Bridges Platform Execution:**
Try commands like:
- "Run QC on Seven Bridges with sample1.bam"
- "Execute Module00a on CGC platform"
- "Process this on CAVATICA: sbg://project/sample.bam"
- "Run genotyping on Seven Bridges platform"

**Manual Execution:**
```bash
# Local execution
sv-agent convert -o cwl_output -m Module00a
sv-agent run cwl_output/Module00a.cwl inputs.yaml

# Seven Bridges execution
sb apps install-workflow Module00a.cwl project/workflow
sb tasks create --app project/workflow --inputs inputs.json
```

**Supported Platforms:**
- 🏥 Cancer Genomics Cloud (CGC) - Free for cancer research
- 👶 CAVATICA - Free for pediatric research  
- ☁️ Seven Bridges AWS/GCP/Azure - Commercial platforms

**Supported Modules:**
- Module00a: Sample QC
- Module00b: Evidence Collection  
- Module00c: Batch QC
- Module01: Clustering
- Module03: Filtering
- Module04: Genotyping

I can help you execute these modules locally or on Seven Bridges platforms - just describe what you want to do!"""
    
    def _handle_status(self, query: str) -> str:
        """Handle SV pipeline status requests."""
        if self.context["last_results"]:
            return f"""Current status:

Last operation: {self.context.get('last_operation', 'Unknown')}
Results: {json.dumps(self.context['last_results'], indent=2)}

Ready for next command."""
        else:
            return """No active operations.

I'm ready to help with:
- Converting WDL workflows to CWL
- Analyzing workflow structure
- Answering questions about GATK-SV
- Providing best practices for SV analysis

What would you like to do?"""
    
    def _handle_recommend(self, query: str) -> str:
        """Handle SV analysis recommendation requests."""
        query_lower = query.lower()
        
        if "coverage" in query_lower:
            return """**Coverage Recommendations for SV Detection:**

✅ **Optimal:** 30-50x mean coverage
- Detects full range of SV sizes (50bp - 1Mb+)
- High sensitivity for all SV types
- Suitable for clinical/research applications

⚠️ **Acceptable:** 15-30x coverage  
- Good for SVs >500bp
- May miss smaller events
- Reduced sensitivity for complex SVs

❌ **Limited:** <15x coverage
- Only large SVs (>5kb) reliably detected
- High false negative rate
- Not recommended for comprehensive analysis

**Pro tip:** Check your actual coverage with:
```bash
samtools depth -a input.bam | awk '{sum+=$3} END {print sum/NR}'
```"""
        
        elif "samples" in query_lower or "cohort" in query_lower:
            return """**Sample/Cohort Recommendations:**

📊 **Cohort Size:**
- Minimum: 30 samples (for reliable frequency estimates)
- Optimal: 100-500 samples
- Large-scale: 1000+ samples (population studies)

🧬 **Sample Selection:**
- Include both affected and unaffected individuals
- Balance male/female for sex chromosome analysis
- Match sequencing platform and chemistry
- Consider ancestry/population structure

👨‍👩‍👧‍👦 **Family Studies:**
- Include complete trios when possible
- Improves de novo SV detection
- Helps validate inheritance patterns
- Reduces false positives

⚡ **Batch Effects:**
- Process samples from same sequencing run together
- Include technical replicates if available
- Document batch information in metadata"""
        
        elif "filter" in query_lower or "threshold" in query_lower:
            return """**Filtering Recommendations:**

🎯 **Quality Thresholds:**
```
High confidence: FILTER == "PASS" && GQ >= 20
Research use: FILTER == "PASS" && GQ >= 10  
Exploratory: FILTER != "FAIL" && GQ >= 5
```

📈 **Frequency Filters:**
- Rare variants: AF < 0.01 (1%)
- Low frequency: AF < 0.05 (5%)
- Common: AF >= 0.05

🔍 **Size Filters:**
- Small SVs: 50bp - 1kb (higher FP rate)
- Medium SVs: 1kb - 100kb (most reliable)
- Large SVs: >100kb (check for artifacts)

💡 **Best Practice:**
Start with stringent filters, then relax based on validation results."""
        
        return self._search_best_practices(query)
    
    def _handle_troubleshoot(self, query: str) -> str:
        """Handle SV pipeline troubleshooting requests."""
        query_lower = query.lower()
        
        common_issues = {
            "low calls": """**Troubleshooting Low SV Calls:**

1. **Check Coverage:**
   ```bash
   samtools depth input.bam | awk '{sum+=$3} END {print sum/NR}'
   ```
   - Need ≥30x for good sensitivity

2. **Verify Insert Size:**
   ```bash
   samtools stats input.bam | grep "insert size"
   ```
   - Should be 300-500bp for standard libraries

3. **Check Alignment Quality:**
   - High proportion of properly paired reads
   - Low chimeric read rate (<5%)

4. **Module00c Output:**
   - Look for samples flagged as outliers
   - Check batch effects

5. **Common Fixes:**
   - Re-align with BWA-MEM (not BWA-ALN)
   - Include unmapped reads
   - Use correct reference genome version""",
            
            "memory": """**Troubleshooting Memory Issues:**

1. **Reduce Parallelization:**
   - Process fewer samples simultaneously
   - Reduce scatter count in WDL

2. **Adjust Java Memory:**
   ```
   -Xmx100G for large cohorts
   -XX:+UseG1GC for better GC
   ```

3. **Module-Specific Settings:**
   - Module00b: Limit MELT memory
   - Module03: Reduce genotyping batch size

4. **Infrastructure:**
   - Use high-memory instances
   - Enable disk-based temp storage""",
            
            "failed": """**Troubleshooting Failed Jobs:**

1. **Check Logs:**
   - WDL execution logs
   - Individual tool stderr
   - System logs (OOM killer)

2. **Common Failures:**
   - Missing index files (.bai/.crai)
   - Reference mismatch
   - Insufficient disk space
   - Docker pull failures

3. **Recovery:**
   - Most modules can resume
   - Check for partial outputs
   - Increase resource allocations"""
        }
        
        for issue_key, solution in common_issues.items():
            if issue_key in query_lower:
                return solution
        
        return """What issue are you experiencing? Common problems include:

- Low SV call counts
- Memory/resource errors  
- Failed jobs or modules
- Long runtime
- Quality concerns

Please describe your specific issue for targeted troubleshooting."""
    
    def _handle_knowledge_search(self, query: str) -> str:
        """Search knowledge base for relevant information."""
        results = self.knowledge.search_knowledge(query)
        
        if not results:
            # Try to find relevant FAQ
            for question, answer in self.knowledge.faq.items():
                if any(word in question.lower() for word in query.lower().split()):
                    return f"**{question}**\n\n{answer}"
            
            return f"I don't have specific information about '{query}'. Try asking about:\n- GATK-SV modules (Module00a-Module06)\n- SV types (deletions, duplications, inversions)\n- Best practices for SV analysis\n- Troubleshooting common issues"
        
        # Format results
        response = f"Here's what I found about '{query}':\n\n"
        
        for result in results[:3]:  # Top 3 results
            if result["type"] == "FAQ":
                response += f"**{result['question']}**\n{result['answer']}\n\n"
            elif result["type"] == "Module":
                response += f"**{result['id']}: {result['info']['name']}**\n"
                response += f"Purpose: {result['info']['purpose']}\n\n"
            elif result["type"] == "SV Type":
                response += f"**{result['id']}: {result['info']['name']}**\n"
                response += f"{result['info']['description']}\n\n"
        
        return response.strip()
    
    def _format_module_explanation(self, module_id: str, module_info: Dict[str, Any]) -> str:
        """Format module explanation."""
        response = f"**{module_id}: {module_info['name']}**\n\n"
        response += f"**Purpose:** {module_info['purpose']}\n\n"
        
        if "inputs" in module_info:
            response += f"**Inputs:** {', '.join(module_info['inputs'])}\n"
        
        if "outputs" in module_info:
            response += f"**Outputs:** {', '.join(module_info['outputs'])}\n"
        
        if "algorithms" in module_info:
            response += f"\n**Algorithms used:** {', '.join(module_info['algorithms'])}\n"
        
        if "key_metrics" in module_info:
            response += f"\n**Key metrics:** {', '.join(module_info['key_metrics'])}\n"
        
        return response
    
    def _format_sv_explanation(self, sv_type: str, sv_info: Dict[str, Any]) -> str:
        """Format SV type explanation."""
        response = f"**{sv_type}: {sv_info['name']}**\n\n"
        response += f"{sv_info['description']}\n\n"
        response += f"**Minimum size:** {sv_info['min_size']}bp\n"
        response += f"**Detection methods:** {', '.join(sv_info['detection_methods'])}\n"
        response += f"**Potential impact:** {sv_info['impact']}\n"
        return response
    
    def _search_best_practices(self, query: str) -> str:
        """Search best practices."""
        query_lower = query.lower()
        relevant_practices = []
        
        for category, practices in self.knowledge.best_practices.items():
            if category.replace("_", " ") in query_lower:
                relevant_practices.append((category, practices))
        
        if relevant_practices:
            response = "**Best Practices:**\n\n"
            for category, practices in relevant_practices:
                response += f"**{category.replace('_', ' ').title()}:**\n"
                for practice in practices:
                    response += f"• {practice}\n"
                response += "\n"
            return response
        
        return "Please specify what aspect you'd like recommendations for: sample selection, quality control, filtering strategy, or validation."