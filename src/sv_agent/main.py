"""CLI entry point for SVAgent."""

import argparse
import json
import sys
import logging
from pathlib import Path

from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat


def setup_logging(verbose: bool):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="sv-agent - Convert GATK-SV WDL workflows to CWL and provide SV analysis expertise",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sv-agent convert -i gatk-sv/wdl -o src/sv_agent/cwl
  sv-agent convert -i gatk-sv/wdl -o src/sv_agent/cwl -m GatherSampleEvidence
  sv-agent chat
  sv-agent ask "What coverage do I need for SV detection?"
  sv-agent analyze GATKSVPipelineBatch
  sv-agent chat --llm-provider ollama --ollama-model codellama:13b
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # LLM configuration options
    parser.add_argument(
        '--llm-provider',
        choices=['ollama', 'openai', 'anthropic', 'auto', 'none'],
        default='auto',
        help='LLM provider to use (default: auto-detect)'
    )
    parser.add_argument(
        '--ollama-model',
        default='llama2:13b',
        help='Ollama model to use (default: llama2:13b)'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama API URL (default: http://localhost:11434)'
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Convert command - main functionality
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert GATK-SV WDL workflows to CWL format"
    )
    convert_parser.add_argument(
        '-i', '--input',
        type=Path,
        default=Path("gatk-sv/wdl"),
        help="Input directory containing WDL files (default: gatk-sv/wdl)"
    )
    convert_parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path("src/sv_agent/cwl"),
        help="Output directory for CWL files (default: src/sv_agent/cwl)"
    )
    convert_parser.add_argument(
        '-m', '--modules',
        nargs="+",
        help="Specific modules to convert (e.g., GatherSampleEvidence)"
    )
    convert_parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate generated CWL files'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze GATK-SV workflow structure"
    )
    analyze_parser.add_argument(
        "workflow",
        help="Workflow name to analyze (without .wdl extension)"
    )
    analyze_parser.add_argument(
        '-f', '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Chat command
    chat_parser = subparsers.add_parser(
        "chat",
        help="Interactive chat for SV analysis guidance"
    )
    chat_parser.add_argument(
        '--no-banner',
        action="store_true",
        help="Skip welcome banner"
    )
    
    # Ask command
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a single question about SV analysis"
    )
    ask_parser.add_argument(
        "question",
        nargs="+",
        help="Your question"
    )
    
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available GATK-SV modules"
    )
    list_parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Initialize agent
    agent = SVAgent()
    
    try:
        if args.command == "convert":
            # Main conversion functionality
            logger.info(f"Converting WDL files from {args.input} to {args.output}")
            
            results = agent.convert_gatksv_to_cwl(
                output_dir=args.output,
                modules=args.modules
            )
            
            print(f"\nConversion Summary:")
            print(f"  ✓ Converted: {len(results['converted'])} files")
            
            if results['converted']:
                print("\nSuccessfully converted:")
                for f in results['converted'][:10]:  # Show first 10
                    print(f"  - {f}")
                if len(results['converted']) > 10:
                    print(f"  ... and {len(results['converted']) - 10} more")
            
            if results['failed']:
                print(f"\n  ✗ Failed: {len(results['failed'])} files")
                for failure in results['failed'][:5]:
                    print(f"  - {failure['file']}: {failure['error']}")
            
            print(f"\nOutput directory: {args.output}")
            
            if args.validate:
                print("\nValidation: Run 'cwltool --validate <cwl_file>' to validate outputs")
        
        elif args.command == "analyze":
            # Analyze workflow
            analysis = agent.analyze_gatksv_workflow(args.workflow)
            
            if args.format == 'json':
                print(json.dumps(analysis, indent=2))
            else:
                print(f"\nWorkflow Analysis: {analysis['name']}")
                print(f"{'=' * 50}")
                print(f"Inputs:       {analysis['inputs']}")
                print(f"Outputs:      {analysis['outputs']}")
                print(f"Tasks:        {analysis['tasks']}")
                print(f"Calls:        {analysis['calls']}")
                print(f"Imports:      {len(analysis['imports'])}")
                
                stats = analysis['statistics']
                print(f"\nStatistics:")
                print(f"  Max parallelism:  {stats['max_parallelism']}")
                print(f"  Has cycles:       {stats['has_cycles']}")
                print(f"  Total calls:      {stats['total_calls']}")
        
        elif args.command == "list":
            # List available modules
            from sv_agent.knowledge import SVKnowledgeBase
            kb = SVKnowledgeBase()
            
            print("\nAvailable GATK-SV Modules:")
            print("=" * 60)
            
            for module_id, info in kb.modules.items():
                if args.details:
                    print(f"\n{module_id}: {info['name']}")
                    print(f"  Purpose: {info['purpose']}")
                else:
                    print(f"  {module_id:<12} - {info['name']}")
        
        elif args.command == "chat":
            # Initialize LLM provider based on args
            llm_config = {
                "provider": args.llm_provider,
                "model": args.ollama_model,
                "url": args.ollama_url
            }
            
            # Handle special case for no LLM
            llm_provider = None
            if args.llm_provider == "none":
                llm_provider = "none"
            
            # Interactive chat
            chat = SVAgentChat(agent, llm_provider=llm_provider, llm_config=llm_config)
            
            if not args.no_banner:
                print("🧬 SV-Agent Interactive Chat")
                print("=" * 50)
                
                if chat.has_llm:
                    print(f"Using LLM: {type(chat.llm).__name__}")
                else:
                    print("Running in rule-based mode (no LLM)")
                
                print("Ask me about GATK-SV, structural variants, or workflow conversion.")
                print("Type 'help' for guidance or 'exit' to quit.\n")
            
            while True:
                try:
                    user_input = input("You: ")
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        print("SV-Agent: Goodbye! Happy SV hunting! 🧬")
                        break
                    
                    response = chat.chat(user_input)
                    print(f"\nSV-Agent: {response}\n")
                
                except KeyboardInterrupt:
                    print("\nSV-Agent: Goodbye!")
                    break
                except Exception as e:
                    logger.error(f"Chat error: {e}")
                    print(f"\nSV-Agent: Sorry, I encountered an error: {e}\n")
        
        elif args.command == "ask":
            # Initialize LLM provider based on args
            llm_config = {
                "provider": args.llm_provider,
                "model": args.ollama_model,
                "url": args.ollama_url
            }
            
            # Handle special case for no LLM
            llm_provider = None
            if args.llm_provider == "none":
                llm_provider = "none"
            
            # Single question
            chat = SVAgentChat(agent, llm_provider=llm_provider, llm_config=llm_config)
            question = " ".join(args.question)
            response = chat.chat(question)
            print(response)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()