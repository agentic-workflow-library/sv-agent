#!/usr/bin/env python3
"""Demonstration of AWLKit WDL to CWL conversion capabilities."""

from pathlib import Path
from sv_agent import SVAgent


def main():
    """Run AWLKit demonstration."""
    print("AWLKit WDL to CWL Conversion Demo")
    print("=" * 40)
    
    # Initialize agent
    agent = SVAgent()
    
    # Create output directory
    output_dir = Path("cwl_output")
    
    # Example 1: Convert specific GATK-SV modules
    print("\n1. Converting Module00a (Sample QC)...")
    results = agent.convert_gatksv_to_cwl(
        output_dir=output_dir / "module00a",
        modules=["Module00a"]
    )
    
    print(f"   Converted: {len(results['converted'])} files")
    if results['failed']:
        print(f"   Failed: {len(results['failed'])} files")
        for failure in results['failed'][:3]:  # Show first 3 failures
            print(f"     - {failure['file']}: {failure['error']}")
    
    # Example 2: Analyze a workflow structure
    print("\n2. Analyzing a GATK-SV workflow...")
    try:
        # Try to find a main workflow file
        wdl_files = list((Path(__file__).parent / "gatk-sv" / "wdl").glob("*.wdl"))
        if wdl_files:
            workflow_name = wdl_files[0].stem
            analysis = agent.analyze_gatksv_workflow(workflow_name)
            
            print(f"   Workflow: {analysis['name']}")
            print(f"   Inputs: {analysis['inputs']}")
            print(f"   Outputs: {analysis['outputs']}")
            print(f"   Tasks: {analysis['tasks']}")
            print(f"   Calls: {analysis['calls']}")
            print(f"   Statistics: {analysis['statistics']}")
    except Exception as e:
        print(f"   Error analyzing workflow: {e}")
    
    # Example 3: Direct AWLKit usage
    print("\n3. Direct AWLKit usage example...")
    from awlkit import WDLParser, CWLWriter
    
    # Create a simple WDL example
    simple_wdl = """
    version 1.0
    
    task hello_world {
        input {
            String name
            Int count = 1
        }
        
        command <<<
            for i in $(seq 1 ~{count}); do
                echo "Hello, ~{name}!"
            done
        >>>
        
        runtime {
            docker: "ubuntu:latest"
            memory: "1G"
        }
        
        output {
            File greeting = stdout()
        }
    }
    """
    
    # Parse and convert
    parser = WDLParser()
    task = parser.parse_string(simple_wdl, "hello_world.wdl")
    
    writer = CWLWriter()
    cwl_content = writer.write(task)
    
    print("   Generated CWL:")
    print("   " + "\n   ".join(cwl_content.split("\n")[:10]))  # First 10 lines
    print("   ...")
    
    print("\n✓ Demo completed!")
    print("\nTo use AWLKit in your workflow:")
    print("1. Install awlkit: pip install -e awlkit/")
    print("2. Use sv-agent to convert GATK-SV workflows")
    print("3. Or use awlkit CLI directly: awlkit convert <wdl_file> <cwl_file>")


if __name__ == "__main__":
    main()