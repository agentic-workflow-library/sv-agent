#!/usr/bin/env python3
"""Example script to test sv-agent chat with Gemma model."""

import sys
from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat
from sv_agent.llm import OllamaProvider


def test_gemma_chat():
    """Test sv-agent chat with Gemma model."""
    print("Testing sv-agent chat with Gemma model...")
    print("=" * 50)
    
    # Check if Ollama is available
    ollama = OllamaProvider(model="gemma:2b")
    if not ollama.is_available():
        print("❌ Ollama is not running!")
        print("\nPlease start Ollama:")
        print("  ollama serve")
        return False
    
    # Check if Gemma is available
    models = ollama.list_models()
    print(f"\nAvailable models: {models}")
    
    if "gemma:2b" not in models and "gemma:7b" not in models:
        print("\n❌ Gemma model not found!")
        print("\nPlease pull the model:")
        print("  ollama pull gemma:2b")
        return False
    
    # Use gemma:7b if available, otherwise gemma:2b
    model = "gemma:7b" if "gemma:7b" in models else "gemma:2b"
    print(f"\n✅ Using model: {model}")
    
    # Initialize chat with Gemma
    ollama_provider = OllamaProvider(model=model)
    agent = SVAgent()
    chat = SVAgentChat(agent, llm_provider=ollama_provider)
    
    # Test questions
    test_questions = [
        "What is a structural variant?",
        "What coverage do I need for SV detection?",
        "Explain Module00a in GATK-SV",
        "How do I convert WDL to CWL?",
        "What are the main types of SVs?"
    ]
    
    print("\n" + "=" * 50)
    print("Testing Gemma responses:")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 50)
        
        try:
            response = chat.chat(question)
            print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
            print(f"(Full response length: {len(response)} chars)")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Test conversation memory
    print("\n" + "=" * 50)
    print("Testing conversation memory:")
    print("=" * 50)
    
    print("\nQ1: What is Module00b?")
    response1 = chat.chat("What is Module00b?")
    print(f"Response: {response1[:150]}...")
    
    print("\nQ2: What are its inputs?")
    response2 = chat.chat("What are its inputs?")
    print(f"Response: {response2[:150]}...")
    print("\n(Should reference Module00b from previous question)")
    
    print("\n✅ All tests completed successfully!")
    return True


def compare_providers():
    """Compare responses from different providers."""
    print("\nComparing LLM providers...")
    print("=" * 50)
    
    agent = SVAgent()
    question = "What is the purpose of Module00a in GATK-SV?"
    
    # Test with Gemma
    print("\n1. Gemma response:")
    print("-" * 30)
    try:
        gemma = OllamaProvider(model="gemma:2b")
        if gemma.is_available() and "gemma:2b" in gemma.list_models():
            chat_gemma = SVAgentChat(agent, llm_provider=gemma)
            response = chat_gemma.chat(question)
            print(response[:200] + "...")
        else:
            print("Gemma not available")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with rule-based
    print("\n2. Rule-based response:")
    print("-" * 30)
    chat_rules = SVAgentChat(agent, llm_provider="none")
    response = chat_rules.chat(question)
    print(response[:200] + "...")
    
    # Test with auto-detect
    print("\n3. Auto-detected provider:")
    print("-" * 30)
    chat_auto = SVAgentChat(agent)
    print(f"Provider type: {type(chat_auto.llm).__name__}")
    response = chat_auto.chat(question)
    print(response[:200] + "...")


if __name__ == "__main__":
    print("SV-Agent Gemma Test Script")
    print("=" * 50)
    
    # Run tests
    success = test_gemma_chat()
    
    if success:
        print("\n" + "=" * 50)
        compare_providers()
    
    sys.exit(0 if success else 1)