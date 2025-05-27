"""Notebook interface for SV-Agent - Jupyter/IPython integration."""

from typing import Dict, Any, Optional, List
from pathlib import Path
from IPython.display import display, Markdown, HTML
import json

from .agent import SVAgent
from .chat import SVAgentChat
from .knowledge import SVKnowledgeBase


class SVAgentNotebook:
    """Notebook-friendly interface for SV-Agent."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize notebook interface."""
        self.agent = SVAgent(config)
        self.chat = SVAgentChat(self.agent)
        self.knowledge = SVKnowledgeBase()
        
        # Display welcome message
        self._display_welcome()
    
    def _display_welcome(self):
        """Display welcome message in notebook."""
        welcome_html = """
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border: 2px solid #4169e1;">
            <h2 style="color: #4169e1; margin-top: 0;">🧬 SV-Agent Notebook Interface</h2>
            <p style="font-size: 16px;">Welcome to your domain-specific agent for structural variant analysis!</p>
            <p style="margin-bottom: 0;">Quick start:</p>
            <ul style="margin-top: 5px;">
                <li><code>agent.help()</code> - See available commands</li>
                <li><code>agent.ask("your question")</code> - Ask about SV analysis</li>
                <li><code>agent.explain("Module00a")</code> - Get detailed explanations</li>
                <li><code>agent.convert_module("Module00a")</code> - Convert WDL to CWL</li>
            </ul>
        </div>
        """
        display(HTML(welcome_html))
    
    def help(self):
        """Display help information."""
        help_md = """
## SV-Agent Notebook Commands

### 💬 Interactive Chat
- `agent.ask("question")` - Ask any question about SV analysis
- `agent.chat()` - Start interactive chat session

### 📚 Knowledge & Explanations  
- `agent.explain("topic")` - Get detailed explanation
- `agent.show_modules()` - Display all GATK-SV modules
- `agent.show_sv_types()` - Display SV type information
- `agent.best_practices("topic")` - Get best practice recommendations

### 🔧 Workflow Operations
- `agent.convert_module("Module00a")` - Convert specific module to CWL
- `agent.convert_all()` - Convert all GATK-SV modules
- `agent.analyze_workflow("name")` - Analyze workflow structure

### 📊 Analysis Functions
- `agent.process_batch(config)` - Run GATK-SV pipeline
- `agent.check_sample_quality(bam_path)` - Check sample metrics
- `agent.visualize_workflow("name")` - Create workflow diagram

### 🛠️ Troubleshooting
- `agent.troubleshoot("issue")` - Get troubleshooting help
- `agent.validate_config(config)` - Validate batch configuration
"""
        display(Markdown(help_md))
    
    def ask(self, question: str):
        """Ask a question and display formatted response."""
        response = self.chat.chat(question)
        display(Markdown(response))
    
    def chat(self):
        """Start an interactive chat session in the notebook."""
        display(Markdown("### 💬 Interactive Chat Session\nType your questions below. Type 'exit' to end."))
        
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ['exit', 'quit']:
                    display(Markdown("*Chat session ended.*"))
                    break
                
                response = self.chat.chat(user_input)
                display(Markdown(f"**SV-Agent:** {response}"))
                
            except KeyboardInterrupt:
                display(Markdown("*Chat session interrupted.*"))
                break
    
    def explain(self, topic: str):
        """Explain a specific topic with rich formatting."""
        response = self.chat._handle_explain({"query": topic})
        display(Markdown(response))
    
    def show_modules(self):
        """Display all GATK-SV modules in a formatted table."""
        html = """
        <h3>GATK-SV Pipeline Modules</h3>
        <table style="width: 100%; border-collapse: collapse;">
        <tr style="background-color: #f0f8ff;">
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Module</th>
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Name</th>
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Purpose</th>
        </tr>
        """
        
        for module_id, info in self.knowledge.modules.items():
            html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>{module_id}</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{info['name']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{info['purpose']}</td>
            </tr>
            """
        
        html += "</table>"
        display(HTML(html))
    
    def show_sv_types(self):
        """Display SV types in a formatted table."""
        html = """
        <h3>Structural Variant Types</h3>
        <table style="width: 100%; border-collapse: collapse;">
        <tr style="background-color: #f0f8ff;">
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Type</th>
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Name</th>
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Description</th>
            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Min Size</th>
        </tr>
        """
        
        for sv_type, info in self.knowledge.sv_types.items():
            html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>{sv_type}</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{info['name']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{info['description']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{info['min_size']}bp</td>
            </tr>
            """
        
        html += "</table>"
        display(HTML(html))
    
    def convert_module(self, module_name: str, output_dir: str = "cwl_output"):
        """Convert a specific GATK-SV module to CWL."""
        display(Markdown(f"### Converting {module_name} to CWL..."))
        
        try:
            results = self.agent.convert_gatksv_to_cwl(
                output_dir=Path(output_dir),
                modules=[module_name]
            )
            
            if results['converted']:
                display(Markdown(f"✅ **Success!** Converted {len(results['converted'])} files:"))
                for file in results['converted']:
                    display(Markdown(f"- `{file}`"))
            
            if results['failed']:
                display(Markdown(f"❌ **Failed:** {len(results['failed'])} files"))
                for failure in results['failed']:
                    display(Markdown(f"- `{failure['file']}`: {failure['error']}"))
                    
        except Exception as e:
            display(Markdown(f"❌ **Error:** {str(e)}"))
    
    def convert_all(self, output_dir: str = "cwl_output"):
        """Convert all GATK-SV modules to CWL."""
        display(Markdown("### Converting all GATK-SV modules to CWL..."))
        
        try:
            results = self.agent.convert_gatksv_to_cwl(output_dir=Path(output_dir))
            
            display(Markdown(f"""
**Conversion Results:**
- ✅ Converted: {len(results['converted'])} files
- ❌ Failed: {len(results['failed'])} files

Output directory: `{output_dir}/`
"""))
            
        except Exception as e:
            display(Markdown(f"❌ **Error:** {str(e)}"))
    
    def analyze_workflow(self, workflow_name: str):
        """Analyze and display workflow structure."""
        try:
            analysis = self.agent.analyze_gatksv_workflow(workflow_name)
            
            display(Markdown(f"### Workflow Analysis: {analysis['name']}"))
            
            # Create summary table
            html = f"""
            <table style="width: 50%; border-collapse: collapse;">
            <tr><td style="padding: 5px; border: 1px solid #ddd;"><b>Inputs</b></td>
                <td style="padding: 5px; border: 1px solid #ddd;">{analysis['inputs']}</td></tr>
            <tr><td style="padding: 5px; border: 1px solid #ddd;"><b>Outputs</b></td>
                <td style="padding: 5px; border: 1px solid #ddd;">{analysis['outputs']}</td></tr>
            <tr><td style="padding: 5px; border: 1px solid #ddd;"><b>Tasks</b></td>
                <td style="padding: 5px; border: 1px solid #ddd;">{analysis['tasks']}</td></tr>
            <tr><td style="padding: 5px; border: 1px solid #ddd;"><b>Calls</b></td>
                <td style="padding: 5px; border: 1px solid #ddd;">{analysis['calls']}</td></tr>
            <tr><td style="padding: 5px; border: 1px solid #ddd;"><b>Max Parallelism</b></td>
                <td style="padding: 5px; border: 1px solid #ddd;">{analysis['statistics']['max_parallelism']}</td></tr>
            </table>
            """
            display(HTML(html))
            
            if analysis['imports']:
                display(Markdown(f"**Imports:** {', '.join(analysis['imports'])}"))
                
        except Exception as e:
            display(Markdown(f"❌ **Error:** {str(e)}"))
    
    def best_practices(self, topic: str = "all"):
        """Display best practices for a specific topic."""
        response = self.chat._handle_recommend({"query": f"best practices for {topic}"})
        display(Markdown(response))
    
    def troubleshoot(self, issue: str):
        """Get troubleshooting help for a specific issue."""
        response = self.chat._handle_troubleshoot({"query": issue})
        display(Markdown(response))
    
    def validate_config(self, config: Dict[str, Any]):
        """Validate a batch configuration."""
        display(Markdown("### Validating Batch Configuration"))
        
        try:
            # Use agent's validation
            self.agent._validate_batch_config(config)
            display(Markdown("✅ **Configuration is valid!**"))
            
            # Display summary
            display(Markdown(f"""
**Configuration Summary:**
- Samples: {len(config.get('samples', []))}
- Reference: `{config.get('reference', 'Not specified')}`
- Output directory: `{config.get('output_dir', 'Not specified')}`
"""))
            
        except ValueError as e:
            display(Markdown(f"❌ **Validation Error:** {str(e)}"))
        except Exception as e:
            display(Markdown(f"❌ **Unexpected Error:** {str(e)}"))
    
    def create_sample_config(self, num_samples: int = 3) -> Dict[str, Any]:
        """Create a sample configuration for testing."""
        config = {
            "samples": [
                {
                    "id": f"SAMPLE{i:03d}",
                    "bam": f"/data/samples/sample{i:03d}.bam",
                    "bai": f"/data/samples/sample{i:03d}.bam.bai"
                }
                for i in range(1, num_samples + 1)
            ],
            "reference": "/data/references/hg38/hg38.fa",
            "output_dir": "/data/output/sv_analysis",
            "batch_metadata": {
                "batch_id": "BATCH001",
                "sequencing_platform": "Illumina",
                "sequencing_center": "MyCenter",
                "project": "SV_Analysis_2024"
            }
        }
        
        display(Markdown("### Sample Configuration Created"))
        display(Markdown(f"```json\n{json.dumps(config, indent=2)}\n```"))
        
        return config
    
    def visualize_workflow(self, workflow_name: str):
        """Create a simple visualization of workflow structure."""
        try:
            analysis = self.agent.analyze_gatksv_workflow(workflow_name)
            
            # Create a simple text-based visualization
            viz = f"""
### Workflow Visualization: {workflow_name}

```
┌─────────────────────────┐
│  {workflow_name:<21} │
├─────────────────────────┤
│  Inputs: {analysis['inputs']:<14} │
│  Tasks: {analysis['tasks']:<15} │
│  Outputs: {analysis['outputs']:<13} │
└─────────────────────────┘
        ↓
    [Processing]
        ↓
┌─────────────────────────┐
│  Statistics:            │
├─────────────────────────┤
│  Total calls: {analysis['statistics']['total_calls']:<9} │
│  Max parallel: {analysis['statistics']['max_parallelism']:<8} │
│  Has cycles: {str(analysis['statistics']['has_cycles']):<10} │
└─────────────────────────┘
```
"""
            display(Markdown(viz))
            
        except Exception as e:
            display(Markdown(f"❌ **Error creating visualization:** {str(e)}"))


# Convenience function for notebook import
def create_agent(config: Optional[Dict[str, Any]] = None) -> SVAgentNotebook:
    """Create and return an SV-Agent notebook interface."""
    return SVAgentNotebook(config)