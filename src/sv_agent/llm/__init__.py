"""LLM provider abstraction for sv-agent."""

from abc import ABC, abstractmethod
import os
import json
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference."""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._available = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama."""
        import aiohttp
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        if self._available is not None:
            return self._available
            
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self._available = response.status_code == 200
            if self._available:
                logger.info(f"Ollama is available at {self.base_url}")
        except Exception:
            self._available = False
            logger.debug("Ollama is not available")
        
        return self._available
    
    def list_models(self) -> list:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._available = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        import openai
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert in structural variant analysis and GATK-SV pipelines."},
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        if self._available is not None:
            return self._available
            
        self._available = bool(self.api_key)
        if self._available:
            logger.info("OpenAI API is available")
        else:
            logger.debug("OpenAI API key not found")
        
        return self._available


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._available = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic API."""
        import anthropic
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=self.api_key)
        
        response = await client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def is_available(self) -> bool:
        """Check if Anthropic API is available."""
        if self._available is not None:
            return self._available
            
        self._available = bool(self.api_key)
        if self._available:
            logger.info("Anthropic API is available")
        else:
            logger.debug("Anthropic API key not found")
        
        return self._available


class RuleBasedProvider(LLMProvider):
    """Fallback rule-based provider when no LLM is available."""
    
    def __init__(self, knowledge_base=None):
        self.knowledge_base = knowledge_base
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using rules and templates."""
        prompt_lower = prompt.lower()
        
        # Basic pattern matching for common questions
        if "coverage" in prompt_lower and "sv" in prompt_lower:
            return "For reliable SV detection with GATK-SV, we recommend:\n- Minimum 30x coverage for short-read WGS\n- Higher coverage (40-50x) improves sensitivity for smaller SVs\n- At least 10x coverage for population-scale studies"
        
        elif "manta" in prompt_lower or "melt" in prompt_lower:
            return "GATK-SV integrates multiple SV callers:\n- Manta: Detects all SV types using PE/SR evidence\n- MELT: Specializes in mobile element insertions\n- Wham: Multiple signal SV detection\n- cn.MOPS & gCNV: Copy number variation detection"
        
        elif "module" in prompt_lower and ("00a" in prompt_lower or "gather" in prompt_lower):
            return "Module00a (GatherSampleEvidence) collects SV evidence from individual samples:\n- Runs SV callers (Manta, MELT, Scramble, Wham)\n- Extracts read depth, paired-end, and split-read signals\n- Outputs: PE, SR, RD, BAF evidence files per sample"
        
        elif "convert" in prompt_lower or "cwl" in prompt_lower:
            return "To convert GATK-SV workflows to CWL:\n1. Use: sv-agent convert -o output_dir\n2. Specific modules: sv-agent convert -m Module00a\n3. With validation: sv-agent convert --validate"
        
        else:
            return "I can help with GATK-SV pipeline questions. Try asking about:\n- Specific modules (Module00a-06)\n- SV callers (Manta, MELT, etc.)\n- Coverage requirements\n- Workflow conversion to CWL\n- Pipeline execution steps"
    
    def is_available(self) -> bool:
        """Rule-based provider is always available."""
        return True


def detect_available_provider(preferred: Optional[str] = None) -> LLMProvider:
    """Auto-detect and return the best available LLM provider."""
    providers = [
        ("ollama", OllamaProvider),
        ("openai", OpenAIProvider),
        ("anthropic", AnthropicProvider),
        ("rules", RuleBasedProvider)
    ]
    
    # If preferred provider is specified, try it first
    if preferred:
        for name, provider_class in providers:
            if name == preferred:
                provider = provider_class()
                if provider.is_available():
                    logger.info(f"Using preferred provider: {name}")
                    return provider
                else:
                    logger.warning(f"Preferred provider {name} is not available")
    
    # Try providers in order
    for name, provider_class in providers:
        provider = provider_class()
        if provider.is_available():
            logger.info(f"Using provider: {name}")
            return provider
    
    # This should never happen since RuleBasedProvider is always available
    logger.warning("Falling back to rule-based provider")
    return RuleBasedProvider()