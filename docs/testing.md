# Testing Guide for SV-Agent

This document describes the test suite for sv-agent, including unit tests, integration tests with LLMs, and testing best practices.

## Overview

The sv-agent test suite includes:
- **Unit tests**: Test core functionality with mocked dependencies
- **Integration tests**: Test actual LLM interactions (requires Ollama)
- **Performance tests**: Measure conversion and response times
- **Example scripts**: Demonstrate real-world usage

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_agent.py            # Core agent functionality tests
├── test_llm_chat.py         # LLM and chat interface tests
├── test_parser.py           # WDL parser tests
└── test_gemma_setup.sh      # Automated test setup script

examples/
├── test_gemma_chat.py       # Interactive Gemma testing
└── ollama_usage.py          # Ollama integration examples
```

## Running Tests

### Quick Start

```bash
# Run all tests (unit tests only, no LLM required)
pytest

# Run with coverage report
pytest --cov=sv_agent --cov-report=html

# Run specific test file
pytest tests/test_llm_chat.py -v
```

### Integration Tests with Ollama

Integration tests require Ollama with a language model (e.g., Gemma):

```bash
# Automated setup and test
./tests/test_gemma_setup.sh

# Manual setup
ollama serve                    # Start Ollama server
ollama pull gemma:2b           # Download Gemma model
pytest --run-integration       # Run integration tests
```

## Test Categories

### 1. Unit Tests (No External Dependencies)

These tests use mocks and run without Ollama:

```python
# test_llm_chat.py - TestOllamaProvider
def test_ollama_initialization(self, ollama_provider):
    """Test Ollama provider initialization."""
    assert ollama_provider.model == "gemma:2b"
    assert ollama_provider.base_url == "http://localhost:11434"
```

**Key unit test areas:**
- Provider initialization
- API response parsing
- Fallback mechanisms
- Conversation memory
- Intent recognition

### 2. Integration Tests (Requires Ollama)

Marked with `@pytest.mark.integration`, these test real LLM interactions:

```python
@pytest.mark.integration
def test_gemma_sv_question(self, gemma_chat):
    """Test Gemma answering SV-related question."""
    response = gemma_chat.chat("What is a structural variant?")
    assert "structural" in response.lower()
```

**Integration test coverage:**
- Real model responses
- Multi-turn conversations
- Domain-specific questions
- Response quality
- Latency measurements

### 3. Chat Interface Tests

Test the complete chat experience:

```python
def test_chat_with_llm_response(self, chat_with_mock_llm):
    """Test chat response using LLM."""
    chat, mock_llm = chat_with_mock_llm
    response = chat.chat("What coverage for SVs?")
    assert "30x coverage" in response
```

**Chat test scenarios:**
- Question intent detection
- Knowledge base integration
- LLM enhancement
- Fallback behavior
- Error handling

## Test Fixtures

### Key Fixtures in `conftest.py`

```python
@pytest.fixture
def ollama_model(pytestconfig):
    """Get the Ollama model to use for tests."""
    return pytestconfig.getoption("--ollama-model")

@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for tests."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return monkeypatch

@pytest.fixture
def temp_cwl_dir(tmp_path):
    """Create temporary directory for CWL output."""
    return tmp_path / "cwl_output"
```

## Command Line Options

Custom pytest options for flexibility:

```bash
# Run with specific Ollama model
pytest --run-integration --ollama-model gemma:7b

# Skip integration tests (default behavior)
pytest  # Only runs unit tests

# Run specific test categories
pytest -k "not integration"  # Unit tests only
pytest -k "integration"      # Integration only
```

## Testing Best Practices

### 1. Mock External Services

```python
@patch('requests.get')
def test_ollama_availability_check(self, mock_get, ollama_provider):
    mock_get.return_value.status_code = 200
    assert ollama_provider.is_available() is True
```

### 2. Test Error Conditions

```python
def test_chat_fallback_to_rules(self, mock_agent):
    """Test fallback when LLM fails."""
    mock_llm = Mock(side_effect=Exception("LLM error"))
    chat = SVAgentChat(agent=mock_agent, llm_provider=mock_llm)
    response = chat.chat("What is Module00a?")
    assert "Module00a" in response  # Still works
```

### 3. Parameterized Tests

```python
@pytest.mark.parametrize("model,expected", [
    ("gemma:2b", True),
    ("llama2:13b", True),
    ("invalid-model", False)
])
def test_model_validation(self, model, expected):
    # Test different model configurations
```

### 4. Performance Testing

```python
def test_response_time(self, gemma_chat):
    """Ensure reasonable response times."""
    import time
    start = time.time()
    response = gemma_chat.chat("What is SV?")
    duration = time.time() - start
    assert duration < 10  # Should respond within 10 seconds
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -e '.[dev]'
      - name: Run unit tests
        run: pytest -v --cov=sv_agent

  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Install Ollama
        run: |
          curl -fsSL https://ollama.ai/install.sh | sh
          ollama serve &
          sleep 5
          ollama pull gemma:2b
      - name: Run integration tests
        run: pytest -v --run-integration
```

## Debugging Tests

### Verbose Output

```bash
# See detailed test output
pytest -vv tests/test_llm_chat.py::TestGemmaIntegration::test_gemma_sv_question

# Show print statements
pytest -s

# Debug specific test
pytest --pdb tests/test_llm_chat.py::test_name
```

### Common Issues

1. **Ollama not running**
   ```
   Error: Connection refused at localhost:11434
   Solution: Start Ollama with 'ollama serve'
   ```

2. **Model not found**
   ```
   Error: Model 'gemma:2b' not found
   Solution: Pull model with 'ollama pull gemma:2b'
   ```

3. **Timeout errors**
   ```
   Error: Test timeout exceeded
   Solution: Increase timeout or use smaller model
   ```

## Test Data

### Sample Test Questions

Located in test files and examples:

```python
test_questions = [
    "What is a structural variant?",
    "What coverage do I need for SV detection?",
    "Explain Module00a in GATK-SV",
    "How do I convert WDL to CWL?",
    "What are the main types of SVs?"
]
```

### Expected Responses

Tests validate that responses contain relevant keywords and concepts:
- Technical accuracy
- Domain terminology
- Helpful guidance
- Proper formatting

## Adding New Tests

### Template for New LLM Tests

```python
class TestNewFeature:
    @pytest.fixture
    def setup(self):
        """Setup test dependencies."""
        return {...}
    
    def test_unit_behavior(self, setup):
        """Test without external dependencies."""
        # Use mocks
        pass
    
    @pytest.mark.integration
    def test_with_llm(self, setup):
        """Test with real LLM."""
        # Requires Ollama
        pass
```

## Performance Benchmarks

Expected performance metrics:

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| Unit test suite | < 5 seconds | No external calls |
| Integration test | < 30 seconds | With Gemma:2b |
| Single chat response | < 5 seconds | Gemma:2b |
| WDL conversion | < 1 second | Per file |

## Summary

The sv-agent test suite ensures:
- Core functionality works without external dependencies
- LLM integration enhances but doesn't break functionality  
- Performance meets expectations
- Error handling is robust
- Documentation stays synchronized with code

Run `./tests/test_gemma_setup.sh` for a complete test experience!