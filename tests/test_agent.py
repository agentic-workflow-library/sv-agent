"""Tests for SVAgent."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from sv_agent import SVAgent


class TestSVAgent:
    """Test cases for SVAgent class."""
    
    def test_agent_initialization(self):
        """Test SVAgent initialization."""
        agent = SVAgent()
        assert agent.name == "SVAgent"
        assert agent.gatksv_path.exists()
    
    def test_agent_with_config(self):
        """Test SVAgent initialization with configuration."""
        config = {"max_samples": 100, "memory": "32G"}
        agent = SVAgent(config=config)
        assert agent.config == config
    
    def test_validate_batch_config_valid(self):
        """Test batch configuration validation with valid config."""
        agent = SVAgent()
        config = {
            "samples": ["sample1", "sample2"],
            "reference": "/path/to/reference.fa",
            "output_dir": "/path/to/output"
        }
        # Should not raise exception
        agent._validate_batch_config(config)
    
    def test_validate_batch_config_missing_field(self):
        """Test batch configuration validation with missing field."""
        agent = SVAgent()
        config = {
            "samples": ["sample1", "sample2"],
            "reference": "/path/to/reference.fa"
            # Missing output_dir
        }
        with pytest.raises(ValueError, match="Missing required field: output_dir"):
            agent._validate_batch_config(config)
    
    def test_prepare_workflow_inputs(self):
        """Test workflow input preparation."""
        agent = SVAgent()
        config = {
            "samples": ["sample1", "sample2"],
            "reference": "/path/to/reference.fa",
            "output_dir": "/path/to/output"
        }
        inputs = agent._prepare_workflow_inputs(config)
        
        assert inputs["samples"] == config["samples"]
        assert inputs["reference"] == config["reference"]
        assert inputs["output_directory"] == config["output_dir"]
    
    @patch('sv_agent.agent.WorkflowEngine')
    def test_process_batch(self, mock_workflow_engine):
        """Test batch processing."""
        # Mock workflow engine
        mock_engine = Mock()
        mock_engine.run.return_value = {"status": "success", "outputs": {}}
        mock_workflow_engine.return_value = mock_engine
        
        agent = SVAgent()
        config = {
            "samples": ["sample1", "sample2"],
            "reference": "/path/to/reference.fa",
            "output_dir": "/path/to/output"
        }
        
        results = agent.process_batch(config)
        
        # Verify workflow was called
        mock_engine.run.assert_called_once()
        assert results["status"] == "success"