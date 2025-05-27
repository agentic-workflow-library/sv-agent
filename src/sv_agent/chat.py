"""Chat interface for SV-Agent - Interactive domain-specific agent."""

import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import re
import logging

from .agent import SVAgent
from .knowledge import SVKnowledgeBase
from .llm import detect_available_provider, OllamaProvider, RuleBasedProvider
from .llm.utils import ConversationMemory, format_prompt_for_sv_domain


logger = logging.getLogger(__name__)


class SVAgentChat:
    """Interactive chat interface for SV-Agent."""
    
    def __init__(self, agent: Optional[SVAgent] = None, llm_provider=None,
                 llm_config: Optional[Dict[str, Any]] = None):
        """Initialize chat interface."""
        self.agent = agent or SVAgent()
        self.knowledge = SVKnowledgeBase()
        self.context = {
            "current_module": None,
            "workflow_state": None,
            "last_results": None
        }
        
        # Initialize LLM provider
        if llm_provider == "none":
            self.llm = RuleBasedProvider(self.knowledge)
        else:
            self.llm = llm_provider or self._initialize_llm(llm_config)
        
        # Conversation memory for multi-turn interactions
        self.memory = ConversationMemory()
        
        # Check if we're using a capable LLM
        self.has_llm = not isinstance(self.llm, RuleBasedProvider)
        logger.info(f"Initialized chat with LLM provider: {type(self.llm).__name__}")
        
        # Define intent handlers
        self.handlers = {
            "help": self._handle_help,
            "explain": self._handle_explain,
            "convert": self._handle_convert,
            "analyze": self._handle_analyze,
            "run": self._handle_run,
            "status": self._handle_status,
            "recommend": self._handle_recommend,
            "troubleshoot": self._handle_troubleshoot
        }
    
    def _initialize_llm(self, config: Optional[Dict[str, Any]] = None) -> Any:
        """Initialize LLM provider based on configuration."""
        config = config or {}
        
        # Try to detect from config
        if config.get("provider") == "ollama":
            return OllamaProvider(
                model=config.get("model", "llama2:13b"),
                base_url=config.get("url", "http://localhost:11434")
            )
        
        # Auto-detect
        return detect_available_provider(config.get("provider"))
    
    def chat(self, message: str) -> str:
        """Process a chat message and return response."""
        # If we have a capable LLM, use it for natural conversation
        if self.has_llm:
            return self._handle_llm_chat(message)
        
        # Otherwise fall back to rule-based routing
        intent, params = self._parse_intent(message)
        
        # Route to appropriate handler
        if intent in self.handlers:
            return self.handlers[intent](params)
        
        # Default to knowledge search
        return self._handle_knowledge_search(message)
    
    def _handle_llm_chat(self, message: str) -> str:
        """Handle chat using LLM for natural conversation."""
        try:
            # Get conversation context
            context = self.memory.get_context()
            
            # Get relevant knowledge
            knowledge_context = self._get_relevant_knowledge(message)
            
            # Format prompt with SV domain context
            prompt = format_prompt_for_sv_domain(
                message,
                context=f"{context}\n\nRelevant Knowledge:\n{knowledge_context}"
            )
            
            # Generate response (handle async properly)
            if asyncio.iscoroutinefunction(self.llm.generate):
                response = asyncio.run(self.llm.generate(prompt))
            else:
                response = self.llm.generate(prompt)
            
            # Store in memory
            self.memory.add_turn(message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fall back to rule-based response
            return self._handle_knowledge_search(message)
    
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
    
    def _parse_intent(self, message: str) -> tuple[str, Dict[str, Any]]:
        """Parse user intent from message."""
        message_lower = message.lower()
        
        # Check for specific intents
        if any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
            return "help", {}
        
        elif any(word in message_lower for word in ["explain", "what is", "tell me about"]):
            return "explain", {"query": message}
        
        elif any(word in message_lower for word in ["convert", "cwl", "wdl to cwl"]):
            return "convert", {"query": message}
        
        elif any(word in message_lower for word in ["analyze", "check", "inspect"]):
            return "analyze", {"query": message}
        
        elif any(word in message_lower for word in ["run", "execute", "process"]):
            return "run", {"query": message}
        
        elif any(word in message_lower for word in ["status", "progress", "current"]):
            return "status", {}
        
        elif any(word in message_lower for word in ["recommend", "suggest", "should i"]):
            return "recommend", {"query": message}
        
        elif any(word in message_lower for word in ["error", "problem", "issue", "troubleshoot"]):
            return "troubleshoot", {"query": message}
        
        return "search", {"query": message}
    
    def _handle_help(self, params: Dict[str, Any]) -> str:
        """Handle help requests."""
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
    
    def _handle_explain(self, params: Dict[str, Any]) -> str:
        """Handle explanation requests."""
        query = params.get("query", "")
        
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
    
    def _handle_convert(self, params: Dict[str, Any]) -> str:
        """Handle conversion requests."""
        query = params.get("query", "")
        
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
    
    def _handle_analyze(self, params: Dict[str, Any]) -> str:
        """Handle analysis requests."""
        query = params.get("query", "")
        
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
    
    def _handle_run(self, params: Dict[str, Any]) -> str:
        """Handle run/execution requests."""
        return """sv-agent can execute CWL workflows to run GATK-SV analysis:

**1. First, convert WDL to CWL:**
```bash
sv-agent convert -o cwl_output -m Module00a
```

**2. Prepare input configuration** (`inputs.yaml`):
```yaml
bam_file:
  class: File
  path: /path/to/sample.bam
  secondaryFiles:
    - class: File
      path: /path/to/sample.bam.bai
reference:
  class: File
  path: /path/to/reference.fa
  secondaryFiles:
    - class: File
      path: /path/to/reference.fa.fai
sample_id: "SAMPLE001"
```

**3. Run the CWL workflow:**
```bash
sv-agent run cwl_output/GatherSampleEvidence.cwl inputs.yaml
```

**Key Points:**
- sv-agent has an integrated CWL execution engine
- Processes BAM/CRAM files through GATK-SV pipeline
- Generates VCF files with structural variant calls
- Handles all GATK-SV modules (Module00a through Module06)

**Full pipeline execution:**
```bash
# Convert all modules
sv-agent convert -o cwl_output

# Run complete pipeline
sv-agent run cwl_output/GATKSVPipelineBatch.cwl batch_inputs.yaml
```"""
    
    def _handle_status(self, params: Dict[str, Any]) -> str:
        """Handle status requests."""
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
    
    def _handle_recommend(self, params: Dict[str, Any]) -> str:
        """Handle recommendation requests."""
        query = params.get("query", "").lower()
        
        if "coverage" in query:
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
        
        elif "samples" in query or "cohort" in query:
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
        
        elif "filter" in query or "threshold" in query:
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
    
    def _handle_troubleshoot(self, params: Dict[str, Any]) -> str:
        """Handle troubleshooting requests."""
        query = params.get("query", "").lower()
        
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
            if issue_key in query:
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