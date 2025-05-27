#!/usr/bin/env python3
"""Example of using sv-agent with Ollama for air-gapped environments."""

from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat
from sv_agent.llm import OllamaProvider


def main():
    """Demonstrate Ollama integration with sv-agent."""
    
    # Initialize agent
    agent = SVAgent()
    
    # Example 1: Use Ollama for chat (auto-detect)
    print("=== Example 1: Auto-detect Ollama ===")
    chat = SVAgentChat(agent)
    response = chat.chat("What coverage do I need for reliable SV detection?")
    print(f"Response: {response}\n")
    
    # Example 2: Explicitly use Ollama with specific model
    print("=== Example 2: Specific Ollama model ===")
    ollama = OllamaProvider(model="codellama:13b")
    if ollama.is_available():
        chat_with_ollama = SVAgentChat(agent, llm_provider=ollama)
        response = chat_with_ollama.chat("Convert Module00a to CWL - explain the process")
        print(f"Response: {response}\n")
    else:
        print("Ollama not available. Please install and run Ollama first.\n")
    
    # Example 3: List available Ollama models
    print("=== Example 3: Available models ===")
    if ollama.is_available():
        models = ollama.list_models()
        print(f"Available Ollama models: {models}\n")
    
    # Example 4: Use without LLM (rule-based only)
    print("=== Example 4: Rule-based mode (no LLM) ===")
    chat_no_llm = SVAgentChat(agent, llm_provider="none")
    response = chat_no_llm.chat("What is Module00a?")
    print(f"Response: {response}\n")
    
    # Example 5: Best practices for air-gapped setup
    print("=== Air-gapped Setup Guide ===")
    print("""
    For air-gapped environments:
    
    1. On internet-connected machine:
       - Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh
       - Pull models: ollama pull codellama:13b
       - Export models: ollama list (note model paths)
    
    2. Transfer to air-gapped machine:
       - Copy Ollama binary and model files
       - Install sv-agent with: pip install -e '.[ollama]'
    
    3. Run Ollama server:
       - ollama serve (default port 11434)
    
    4. Use sv-agent:
       - sv-agent chat --llm-provider ollama
       - sv-agent ask "your question" --ollama-model codellama:13b
    """)


if __name__ == "__main__":
    main()