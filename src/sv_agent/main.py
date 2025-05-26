"""CLI entry point for SVAgent."""

import argparse
import json
import sys
from pathlib import Path

from sv_agent import SVAgent


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SVAgent - Automated GATK-SV pipeline processing"
    )
    
    parser.add_argument(
        "batch_config",
        type=Path,
        help="Path to batch configuration JSON file"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to agent configuration file"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Output directory for results (default: results)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Load batch configuration
    try:
        with open(args.batch_config, "r") as f:
            batch_config = json.load(f)
    except Exception as e:
        print(f"Error loading batch configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load agent configuration if provided
    agent_config = {}
    if args.config:
        try:
            with open(args.config, "r") as f:
                agent_config = json.load(f)
        except Exception as e:
            print(f"Error loading agent configuration: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Initialize and run agent
    try:
        agent = SVAgent(config=agent_config)
        results = agent.process_batch(batch_config)
        
        # Save results
        args.output.mkdir(parents=True, exist_ok=True)
        with open(args.output / "results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Processing completed. Results saved to {args.output}")
        
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()