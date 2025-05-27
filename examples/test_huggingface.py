#!/usr/bin/env python3
"""Test HuggingFace integration with SV-Agent."""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "submodules" / "awlkit" / "src"))

from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat

logging.basicConfig(level=logging.INFO)


def test_huggingface_chat():
    """Test HuggingFace provider with SVAgentChat."""
    print("Testing HuggingFace integration with SV-Agent\n")
    
    # Initialize agent
    agent = SVAgent()
    
    # Configure HuggingFace provider
    llm_config = {
        "provider": "huggingface",
        "model_id": "microsoft/phi-2",  # Small model for testing
        "device": "cpu",  # Use CPU for compatibility
        "load_in_4bit": False,  # Disable quantization for CPU
    }
    
    # Create chat interface
    chat = SVAgentChat(agent, llm_provider=None, llm_config=llm_config)
    
    # Test questions
    questions = [
        "What coverage is recommended for SV detection?",
        "Explain Module00a briefly",
        "What are structural variants?",
    ]
    
    for question in questions:
        print(f"Q: {question}")
        try:
            response = chat.chat(question)
            print(f"A: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")


def test_rule_based_fallback():
    """Test rule-based fallback when HuggingFace is not available."""
    print("\nTesting rule-based fallback mode\n")
    
    agent = SVAgent()
    
    # Use 'none' to force rule-based provider
    chat = SVAgentChat(agent, llm_provider="none")
    
    question = "What coverage do I need for SV detection?"
    print(f"Q: {question}")
    response = chat.chat(question)
    print(f"A: {response}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("SV-Agent HuggingFace Integration Test")
    print("=" * 60)
    
    # Test rule-based first (always works)
    test_rule_based_fallback()
    
    # Test HuggingFace if available
    try:
        import transformers
        print("\nTransformers library detected, testing HuggingFace provider...")
        print("NOTE: This will download a model on first run (~1.5GB for phi-2)")
        print("=" * 60)
        test_huggingface_chat()
    except ImportError:
        print("\nTransformers library not installed.")
        print("Install with: pip install transformers torch")
        print("Or: pip install -e '.[huggingface]'")