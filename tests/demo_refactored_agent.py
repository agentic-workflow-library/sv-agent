"""Demonstration of the refactored sv-agent using AWLKit base classes."""

import sys
from pathlib import Path

# Add awlkit to path
sys.path.insert(0, str(Path(__file__).parent.parent / "awlkit" / "src"))

from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat


def main():
    """Run a demo of the refactored sv-agent."""
    
    print("=" * 60)
    print("SV-Agent Refactoring Demo")
    print("Using AWLKit Base Classes")
    print("=" * 60)
    
    # Create agent
    agent = SVAgent()
    
    # 1. Show capabilities (inherited from AWLKit)
    print("\n1. Agent Capabilities:")
    capabilities = agent.get_capabilities()
    print(f"   Total capabilities: {len(capabilities)}")
    print("   Base capabilities (from AWLKit):")
    for cap in ['process_batch', 'analyze_workflow', 'validate_inputs']:
        print(f"     - {cap}")
    print("   Domain capabilities (SV-specific):")
    for cap in capabilities:
        if cap not in ['process_batch', 'analyze_workflow', 'validate_inputs']:
            print(f"     - {cap}")
    
    # 2. Show metadata (inherited method)
    print("\n2. Agent Metadata:")
    metadata = agent.get_metadata()
    print(f"   Name: {metadata['name']}")
    print(f"   Module: {metadata['module']}")
    print(f"   Capabilities count: {len(metadata['capabilities'])}")
    
    # 3. Test batch processing with AWLKit validation
    print("\n3. Batch Processing (with AWLKit validation):")
    
    # This will fail AWLKit's base validation
    try:
        agent.process_batch({})
    except ValueError as e:
        print(f"   ✓ Base validation caught error: {e}")
    
    # This will fail SV-specific validation
    try:
        batch_config = {
            'samples': [{'id': 'low_cov_sample', 'coverage': 10}],
            'reference': '/ref.fa',
            'output_dir': '/output'
        }
        agent.process_batch(batch_config)
    except ValueError as e:
        print(f"   ✓ SV validation caught error: {e}")
    
    # This will succeed
    batch_config = {
        'samples': [
            {'id': 'sample1', 'coverage': 30},
            {'id': 'sample2', 'coverage': 35}
        ],
        'reference': '/ref.fa',
        'output_dir': '/output'
    }
    result = agent.process_batch(batch_config)
    print(f"   ✓ Successful batch processing:")
    print(f"     - Pipeline: {result['pipeline']}")
    print(f"     - Samples processed: {result['samples_processed']}")
    print(f"     - Has metadata: {'_metadata' in result}")
    
    # 4. Test chat interface (inherited from AWLKit)
    print("\n4. Chat Interface (AWLKit ChatInterface):")
    chat = SVAgentChat(agent, llm_provider="none")
    
    # Test SV-specific query
    response = chat.process_query("What is a deletion?")
    print(f"   Query: 'What is a deletion?'")
    print(f"   Response preview: {response[:100]}...")
    
    # 5. Show AWLKit integration benefits
    print("\n5. AWLKit Integration Benefits:")
    print("   ✓ Standardized agent interface (Agent base class)")
    print("   ✓ Reusable chat interface (ChatInterface base)")
    print("   ✓ Common validation logic (process_batch)")
    print("   ✓ Shared LLM integration (awlkit.llm)")
    print("   ✓ Workflow analysis utilities (awlkit.utils)")
    print("   ✓ Consistent metadata and capabilities")
    
    print("\n" + "=" * 60)
    print("Refactoring Complete!")
    print("sv-agent now focuses on SV domain knowledge")
    print("while AWLKit provides the infrastructure")
    print("=" * 60)


if __name__ == "__main__":
    main()