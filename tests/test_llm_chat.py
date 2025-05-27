"""Tests for LLM chat capabilities using Gemma via Ollama."""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import json
import os

from sv_agent.chat import SVAgentChat
from sv_agent.llm import OllamaProvider, RuleBasedProvider, detect_available_provider
from sv_agent.llm.utils import ConversationMemory


class TestOllamaProvider:
    """Test Ollama provider with Gemma model."""
    
    @pytest.fixture
    def ollama_provider(self):
        """Create an Ollama provider instance."""
        return OllamaProvider(model="gemma:2b", base_url="http://localhost:11434")
    
    @pytest.fixture
    def mock_ollama_response(self):
        """Mock response from Ollama API."""
        return {
            "model": "gemma:2b",
            "response": "For reliable SV detection, you need at least 30x coverage.",
            "context": [1, 2, 3],
            "total_duration": 1000000000,
            "eval_count": 50
        }
    
    def test_ollama_initialization(self, ollama_provider):
        """Test Ollama provider initialization."""
        assert ollama_provider.model == "gemma:2b"
        assert ollama_provider.base_url == "http://localhost:11434"
        assert ollama_provider._available is None
    
    @patch('requests.get')
    def test_ollama_availability_check(self, mock_get, ollama_provider):
        """Test checking if Ollama is available."""
        # Mock successful response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [
                {"name": "gemma:2b", "size": 1626585344},
                {"name": "llama2:13b", "size": 7365960704}
            ]
        }
        
        assert ollama_provider.is_available() is True
        assert ollama_provider._available is True
        mock_get.assert_called_with(
            "http://localhost:11434/api/tags",
            timeout=2
        )
    
    @patch('requests.get')
    def test_ollama_not_available(self, mock_get, ollama_provider):
        """Test when Ollama is not available."""
        mock_get.side_effect = Exception("Connection refused")
        
        assert ollama_provider.is_available() is False
        assert ollama_provider._available is False
    
    @patch('requests.get')
    def test_list_models(self, mock_get, ollama_provider):
        """Test listing available Ollama models."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [
                {"name": "gemma:2b"},
                {"name": "gemma:7b"},
                {"name": "codellama:13b"}
            ]
        }
        
        models = ollama_provider.list_models()
        assert "gemma:2b" in models
        assert "gemma:7b" in models
        assert len(models) == 3
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_generate_response(self, mock_session_class, ollama_provider, mock_ollama_response):
        """Test generating response with Gemma model."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: mock_ollama_response)
        
        # Create mock session
        mock_session = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Test generation
        prompt = "What coverage do I need for SV detection?"
        response = await ollama_provider.generate(prompt)
        
        assert response == "For reliable SV detection, you need at least 30x coverage."
        
        # Verify API call
        expected_payload = {
            "model": "gemma:2b",
            "prompt": prompt,
            "stream": False
        }
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"
        assert call_args[1]['json'] == expected_payload


class TestLLMChat:
    """Test chat interface with LLM integration."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock SV agent."""
        agent = Mock()
        agent.convert_gatksv_to_cwl = Mock(return_value={
            "converted": ["Module00a.cwl"],
            "failed": []
        })
        return agent
    
    @pytest.fixture
    def chat_with_mock_llm(self, mock_agent):
        """Create chat with mocked LLM."""
        mock_llm = Mock()
        mock_llm.generate = Mock(return_value="This is a test response about SVs.")
        mock_llm.is_available = Mock(return_value=True)
        
        chat = SVAgentChat(agent=mock_agent, llm_provider=mock_llm)
        return chat, mock_llm
    
    def test_chat_initialization_with_llm(self, chat_with_mock_llm):
        """Test chat initialization with LLM provider."""
        chat, mock_llm = chat_with_mock_llm
        
        assert chat.has_llm is True
        assert chat.llm == mock_llm
        assert isinstance(chat.memory, ConversationMemory)
    
    def test_chat_with_llm_response(self, chat_with_mock_llm):
        """Test chat response using LLM."""
        chat, mock_llm = chat_with_mock_llm
        
        # Configure mock to return a coroutine
        async def mock_generate(prompt, **kwargs):
            return "Gemma says: For SV detection, 30x coverage is recommended."
        
        mock_llm.generate = mock_generate
        
        response = chat.chat("What coverage for SVs?")
        assert "30x coverage" in response
    
    def test_chat_fallback_to_rules(self, mock_agent):
        """Test fallback to rule-based when LLM fails."""
        # Create a failing LLM
        mock_llm = Mock()
        mock_llm.generate = Mock(side_effect=Exception("LLM error"))
        mock_llm.is_available = Mock(return_value=True)
        
        chat = SVAgentChat(agent=mock_agent, llm_provider=mock_llm)
        
        # Should fall back to rule-based
        response = chat.chat("What is Module00a?")
        assert "Module00a" in response or "don't have specific information" in response
    
    def test_rule_based_provider(self, mock_agent):
        """Test using rule-based provider explicitly."""
        chat = SVAgentChat(agent=mock_agent, llm_provider="none")
        
        assert isinstance(chat.llm, RuleBasedProvider)
        assert chat.has_llm is False
        
        # Test basic patterns
        response = chat.chat("What coverage for SV?")
        assert "coverage" in response.lower()
        assert "30x" in response or "recommend" in response.lower()


class TestGemmaIntegration:
    """Integration tests with Gemma model (requires Ollama running)."""
    
    @pytest.fixture
    def gemma_chat(self):
        """Create chat with Gemma model."""
        # Check if Ollama is available
        ollama = OllamaProvider(model="gemma:2b")
        if not ollama.is_available():
            pytest.skip("Ollama not available - skipping integration test")
        
        # Check if Gemma model is available
        models = ollama.list_models()
        if "gemma:2b" not in models and "gemma:7b" not in models:
            pytest.skip("Gemma model not available - pull with: ollama pull gemma:2b")
        
        return SVAgentChat(llm_provider=ollama)
    
    @pytest.mark.integration
    def test_gemma_sv_question(self, gemma_chat):
        """Test Gemma answering SV-related question."""
        response = gemma_chat.chat("What is a structural variant?")
        
        # Check that response is relevant
        assert len(response) > 50  # Non-trivial response
        assert any(term in response.lower() for term in [
            "structural", "variant", "genomic", "dna", "chromosome"
        ])
    
    @pytest.mark.integration
    def test_gemma_module_explanation(self, gemma_chat):
        """Test Gemma explaining GATK-SV module."""
        response = gemma_chat.chat("Explain Module00a in GATK-SV")
        
        # Should mention evidence gathering
        assert len(response) > 100
        assert any(term in response.lower() for term in [
            "module", "evidence", "sample", "gatk"
        ])
    
    @pytest.mark.integration
    def test_gemma_conversation_memory(self, gemma_chat):
        """Test conversation memory with Gemma."""
        # First question
        response1 = gemma_chat.chat("What is Module00a?")
        assert "Module00a" in response1 or "module" in response1.lower()
        
        # Follow-up question
        response2 = gemma_chat.chat("What are its main outputs?")
        
        # Should reference the previous context
        assert len(response2) > 50
        assert "output" in response2.lower() or "file" in response2.lower()


class TestLLMProviderDetection:
    """Test automatic LLM provider detection."""
    
    @patch('sv_agent.llm.OllamaProvider.is_available')
    @patch('sv_agent.llm.OpenAIProvider.is_available')
    def test_detect_ollama_first(self, mock_openai, mock_ollama):
        """Test Ollama is preferred when available."""
        mock_ollama.return_value = True
        mock_openai.return_value = True
        
        provider = detect_available_provider()
        assert isinstance(provider, OllamaProvider)
    
    @patch('sv_agent.llm.OllamaProvider.is_available')
    def test_fallback_to_rules(self, mock_ollama):
        """Test fallback to rule-based when no LLM available."""
        mock_ollama.return_value = False
        
        # Remove any API keys from environment
        with patch.dict(os.environ, {}, clear=True):
            provider = detect_available_provider()
            assert isinstance(provider, RuleBasedProvider)
    
    @patch('sv_agent.llm.OllamaProvider.is_available')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_detect_openai_when_ollama_unavailable(self, mock_ollama):
        """Test OpenAI detection when Ollama unavailable."""
        mock_ollama.return_value = False
        
        provider = detect_available_provider()
        # Should detect OpenAI based on API key
        assert provider.is_available()


class TestConversationMemory:
    """Test conversation memory functionality."""
    
    def test_memory_storage(self):
        """Test storing conversation turns."""
        memory = ConversationMemory(max_turns=3)
        
        memory.add_turn("What is SV?", "SV stands for structural variant.")
        memory.add_turn("What types exist?", "DEL, DUP, INV, INS, BND")
        
        assert len(memory.history) == 2
        assert memory.history[0]["user"] == "What is SV?"
        assert memory.history[1]["assistant"] == "DEL, DUP, INV, INS, BND"
    
    def test_memory_limit(self):
        """Test memory limits conversation history."""
        memory = ConversationMemory(max_turns=2)
        
        memory.add_turn("Q1", "A1")
        memory.add_turn("Q2", "A2")
        memory.add_turn("Q3", "A3")
        
        assert len(memory.history) == 2
        assert memory.history[0]["user"] == "Q2"
        assert memory.history[1]["user"] == "Q3"
    
    def test_get_context(self):
        """Test retrieving conversation context."""
        memory = ConversationMemory()
        
        memory.add_turn("What is Module00a?", "It's the evidence gathering module.")
        memory.add_turn("What does it output?", "PE, SR, RD, and BAF files.")
        
        context = memory.get_context(n_turns=2)
        assert "Module00a" in context
        assert "evidence gathering" in context
        assert "PE, SR, RD" in context


# Fixtures for integration testing
@pytest.fixture(scope="session")
def ensure_gemma_model():
    """Ensure Gemma model is available for tests."""
    ollama = OllamaProvider()
    if ollama.is_available():
        models = ollama.list_models()
        if "gemma:2b" not in models:
            print("\nNote: Gemma model not found. Install with: ollama pull gemma:2b")
            print("Integration tests will be skipped.\n")


def pytest_collection_modifyitems(config, items):
    """Mark tests that require Ollama as integration tests."""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)