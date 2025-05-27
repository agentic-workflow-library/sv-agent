"""Pytest configuration for sv-agent tests."""

import pytest
import os


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require Ollama"
    )
    parser.addoption(
        "--ollama-model",
        action="store",
        default="gemma:2b",
        help="Ollama model to use for tests (default: gemma:2b)"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as requiring Ollama/LLM integration"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="Integration tests skipped without --run-integration flag"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


@pytest.fixture(scope="session")
def ollama_model(pytestconfig):
    """Get the Ollama model to use for tests."""
    return pytestconfig.getoption("--ollama-model")


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for tests."""
    # Clear any existing API keys
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    
    yield monkeypatch


@pytest.fixture
def temp_cwl_dir(tmp_path):
    """Create a temporary directory for CWL output."""
    cwl_dir = tmp_path / "cwl_output"
    cwl_dir.mkdir()
    return cwl_dir