"""CLI entry point for SVAgent."""

import argparse
import json
import sys
from pathlib import Path

from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SVAgent - Domain-specific agent for structural variant analysis"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command (original functionality)
    process_parser = subparsers.add_parser("process", help="Process a batch of samples")
    process_parser.add_argument(
        "batch_config",
        type=Path,
        help="Path to batch configuration JSON file"
    )
    process_parser.add_argument(
        "--config",
        type=Path,
        help="Path to agent configuration file"
    )
    process_parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Output directory for results (default: results)"
    )
    process_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert WDL workflows to CWL")
    convert_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for CWL files"
    )
    convert_parser.add_argument(
        "--modules",
        nargs="+",
        help="Specific modules to convert"
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze workflow structure")
    analyze_parser.add_argument(
        "workflow",
        help="Workflow name to analyze"
    )
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Interactive chat with SV-Agent")
    chat_parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip welcome banner"
    )
    
    # Ask command (single question)
    ask_parser = subparsers.add_parser("ask", help="Ask a single question")
    ask_parser.add_argument(
        "question",
        nargs="+",
        help="Question to ask"
    )
    
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Initialize agent
    agent = SVAgent()
    
    try:
        if args.command == "process":
            # Original batch processing functionality
            with open(args.batch_config, "r") as f:
                batch_config = json.load(f)
            
            agent_config = {}
            if args.config:
                with open(args.config, "r") as f:
                    agent_config = json.load(f)
            
            agent = SVAgent(config=agent_config)
            results = agent.process_batch(batch_config)
            
            args.output.mkdir(parents=True, exist_ok=True)
            with open(args.output / "results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"Processing completed. Results saved to {args.output}")
        
        elif args.command == "convert":
            # Convert workflows
            results = agent.convert_gatksv_to_cwl(
                output_dir=args.output,
                modules=args.modules
            )
            print(f"Converted {len(results['converted'])} workflows")
            if results['failed']:
                print(f"Failed: {len(results['failed'])} workflows")
                for failure in results['failed'][:3]:
                    print(f"  - {failure['file']}: {failure['error']}")
        
        elif args.command == "analyze":
            # Analyze workflow
            analysis = agent.analyze_gatksv_workflow(args.workflow)
            print(json.dumps(analysis, indent=2))
        
        elif args.command == "chat":
            # Interactive chat mode
            chat = SVAgentChat(agent)
            
            if not args.no_banner:
                print("🧬 Welcome to SV-Agent Chat!")
                print("=" * 50)
                print("I'm your domain-specific agent for structural variant analysis.")
                print("Type 'help' to see what I can do, or 'exit' to quit.\n")
            
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
                    print(f"\nSV-Agent: Sorry, I encountered an error: {e}\n")
        
        elif args.command == "ask":
            # Single question mode
            chat = SVAgentChat(agent)
            question = " ".join(args.question)
            response = chat.chat(question)
            print(response)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()