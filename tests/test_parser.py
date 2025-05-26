"""Tests for CLI parser and main function."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from sv_agent.main import main


class TestCLIParser:
    """Test cases for CLI parser."""
    
    def test_main_with_valid_batch_config(self, tmp_path):
        """Test main function with valid batch configuration."""
        # Create temporary batch config
        batch_config = {
            "samples": ["sample1", "sample2"],
            "reference": "/path/to/reference.fa",
            "output_dir": str(tmp_path / "output")
        }
        
        batch_file = tmp_path / "batch.json"
        with open(batch_file, "w") as f:
            json.dump(batch_config, f)
        
        # Mock SVAgent
        with patch('sv_agent.main.SVAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.process_batch.return_value = {"status": "success"}
            mock_agent_class.return_value = mock_agent
            
            # Test with minimal arguments
            with patch('sys.argv', ['sv_agent', str(batch_file)]):
                main()
            
            # Verify agent was called
            mock_agent_class.assert_called_once_with(config={})
            mock_agent.process_batch.assert_called_once_with(batch_config)
    
    def test_main_with_agent_config(self, tmp_path):
        """Test main function with agent configuration."""
        # Create temporary files
        batch_config = {
            "samples": ["sample1"],
            "reference": "/path/to/reference.fa",
            "output_dir": str(tmp_path / "output")
        }
        agent_config = {
            "max_samples": 50,
            "memory": "16G"
        }
        
        batch_file = tmp_path / "batch.json"
        agent_file = tmp_path / "agent.json"
        
        with open(batch_file, "w") as f:
            json.dump(batch_config, f)
        
        with open(agent_file, "w") as f:
            json.dump(agent_config, f)
        
        # Mock SVAgent
        with patch('sv_agent.main.SVAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.process_batch.return_value = {"status": "success"}
            mock_agent_class.return_value = mock_agent
            
            # Test with agent config
            with patch('sys.argv', ['sv_agent', str(batch_file), '--config', str(agent_file)]):
                main()
            
            # Verify agent was called with config
            mock_agent_class.assert_called_once_with(config=agent_config)
    
    def test_main_with_invalid_batch_file(self, tmp_path):
        """Test main function with invalid batch file."""
        batch_file = tmp_path / "nonexistent.json"
        
        with patch('sys.argv', ['sv_agent', str(batch_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
    
    def test_main_with_custom_output(self, tmp_path):
        """Test main function with custom output directory."""
        # Create temporary batch config
        batch_config = {
            "samples": ["sample1"],
            "reference": "/path/to/reference.fa",
            "output_dir": str(tmp_path / "workflow_output")
        }
        
        batch_file = tmp_path / "batch.json"
        custom_output = tmp_path / "custom_results"
        
        with open(batch_file, "w") as f:
            json.dump(batch_config, f)
        
        # Mock SVAgent
        with patch('sv_agent.main.SVAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.process_batch.return_value = {"status": "success"}
            mock_agent_class.return_value = mock_agent
            
            # Test with custom output
            with patch('sys.argv', ['sv_agent', str(batch_file), '--output', str(custom_output)]):
                main()
            
            # Verify output directory was created
            assert custom_output.exists()
            assert (custom_output / "results.json").exists()