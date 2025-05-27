#!/usr/bin/env python3
"""Example: Convert a GATK-SV module from WDL to CWL."""

from pathlib import Path
import sys

# Add parent directory to path to import sv_agent
sys.path.append(str(Path(__file__).parent.parent))

from sv_agent import SVAgent


def main():
    """Convert GATK-SV Module00a to CWL format."""
    
    # Initialize agent
    agent = SVAgent()
    
    # Output directory
    output_dir = Path("cwl_conversions")
    
    print("Converting GATK-SV Module00a (Sample QC) to CWL...")
    print("-" * 50)
    
    # Convert Module00a workflows
    results = agent.convert_gatksv_to_cwl(
        output_dir=output_dir,
        modules=["Module00a"]
    )
    
    print(f"\nConversion Results:")
    print(f"Successfully converted: {len(results['converted'])} files")
    
    if results['converted']:
        print("\nConverted files:")
        for filename in results['converted']:
            print(f"  ✓ {filename}")
    
    if results['failed']:
        print(f"\nFailed conversions: {len(results['failed'])} files")
        for failure in results['failed']:
            print(f"  ✗ {failure['file']}: {failure['error']}")
    
    # Analyze one of the converted workflows
    if results['converted']:
        workflow_name = results['converted'][0].replace('.wdl', '')
        print(f"\nAnalyzing workflow: {workflow_name}")
        
        try:
            analysis = agent.analyze_gatksv_workflow(workflow_name)
            print(f"  - Inputs: {analysis['inputs']}")
            print(f"  - Outputs: {analysis['outputs']}")
            print(f"  - Tasks: {analysis['tasks']}")
            print(f"  - Total calls: {analysis['calls']}")
            
            stats = analysis['statistics']
            print(f"  - Has cycles: {stats['has_cycles']}")
            print(f"  - Max parallelism: {stats['max_parallelism']}")
        except Exception as e:
            print(f"  Error analyzing: {e}")
    
    print(f"\nCWL files written to: {output_dir.absolute()}")
    print("\nTo validate the generated CWL files:")
    print("  cwltool --validate <cwl_file>")
    
    print("\nTo use these CWL files:")
    print("  1. Ensure all Docker images are available")
    print("  2. Prepare input JSON/YAML files")
    print("  3. Run with: cwltool <cwl_file> <inputs.json>")


if __name__ == "__main__":
    main()