"""Test the refactored sv-agent using AWLKit base classes."""

import pytest
from pathlib import Path
import sys

# Add awlkit to path
sys.path.insert(0, str(Path(__file__).parent.parent / "awlkit" / "src"))

from sv_agent import SVAgent
from sv_agent.chat import SVAgentChat
from sv_agent.knowledge import SVKnowledgeBase


class TestRefactoredSVAgent:
    """Test suite for refactored sv-agent."""
    
    def test_sv_agent_initialization(self):
        """Test SVAgent inherits from AWLKit Agent properly."""
        agent = SVAgent()
        
        # Check it has base class methods
        assert hasattr(agent, 'process_batch')
        assert hasattr(agent, 'analyze_workflow')
        assert hasattr(agent, 'get_capabilities')
        assert hasattr(agent, 'get_metadata')
        
        # Check SV-specific attributes
        assert hasattr(agent, 'knowledge')
        assert hasattr(agent, 'gatksv_path')
        assert isinstance(agent.knowledge, SVKnowledgeBase)
        
        # Check capabilities include both base and domain
        capabilities = agent.get_capabilities()
        assert 'process_batch' in capabilities  # Base capability
        assert 'sv_detection' in capabilities   # Domain capability
    
    def test_process_batch_with_validation(self):
        """Test batch processing with AWLKit validation."""
        agent = SVAgent()
        
        # Test invalid config - should fail AWLKit validation
        with pytest.raises(ValueError, match="must contain 'samples'"):
            agent.process_batch({})
        
        # Test valid config
        batch_config = {
            'samples': [
                {'id': 'sample1', 'bam': 'sample1.bam'},
                {'id': 'sample2', 'bam': 'sample2.bam'}
            ],
            'reference': '/path/to/ref.fa',
            'output_dir': '/path/to/output'
        }
        
        result = agent.process_batch(batch_config)
        
        # Check result has metadata from base class
        assert '_metadata' in result
        assert result['_metadata']['agent'] == 'SVAgent'
        assert result['_metadata']['samples_requested'] == 2
        
        # Check SV-specific results
        assert result['pipeline'] == 'GATK-SV'
        assert 'modules_executed' in result
    
    def test_sv_specific_validation(self):
        """Test SV-specific validation on top of base validation."""
        agent = SVAgent()
        
        # Test coverage validation
        batch_config = {
            'samples': [
                {'id': 'sample1', 'bam': 'sample1.bam', 'coverage': 10}  # Too low
            ],
            'reference': '/path/to/ref.fa',
            'output_dir': '/path/to/output'
        }
        
        with pytest.raises(ValueError, match="insufficient coverage"):
            agent.process_batch(batch_config)
    
    def test_chat_interface_inheritance(self):
        """Test SVAgentChat inherits from AWLKit ChatInterface."""
        agent = SVAgent()
        chat = SVAgentChat(agent, llm_provider="none")
        
        # Check base class attributes
        assert hasattr(chat, 'handlers')
        assert hasattr(chat, 'memory')
        assert hasattr(chat, 'process_query')
        assert hasattr(chat, 'chat_loop')
        
        # Check SV-specific handlers registered
        assert 'explain' in chat.handlers
        assert 'troubleshoot' in chat.handlers
        
        # Test handler execution
        response = chat.process_query("What is a deletion?")
        assert response is not None
    
    def test_workflow_analysis_uses_awlkit(self):
        """Test workflow analysis uses AWLKit utilities."""
        agent = SVAgent()
        
        # Create a mock WDL file
        mock_wdl = Path("/tmp/test_workflow.wdl")
        mock_wdl.write_text("""
        version 1.0
        workflow TestWorkflow {
            input {
                File input_bam
            }
            output {
                File output_vcf = "test.vcf"
            }
        }
        """)
        
        try:
            # Analyze using inherited method
            analysis = agent.analyze_workflow(str(mock_wdl))
            
            # Should have standard analysis fields from AWLKit
            assert 'path' in analysis
            assert 'type' in analysis
            assert 'inputs' in analysis
            assert 'outputs' in analysis
            
            # If module is known, should have SV info
            # (won't for this test file)
            
        finally:
            mock_wdl.unlink(missing_ok=True)
    
    def test_metadata_includes_domain_info(self):
        """Test agent metadata includes domain-specific info."""
        agent = SVAgent()
        metadata = agent.get_metadata()
        
        assert metadata['name'] == 'SVAgent'
        assert 'sv_detection' in metadata['capabilities']
        assert 'sv_filtering' in metadata['capabilities']
    
    def test_knowledge_base_integration(self):
        """Test knowledge base is properly integrated."""
        agent = SVAgent()
        
        # Test knowledge is accessible
        assert agent.knowledge is not None
        
        # Test knowledge contains SV info
        sv_info = agent.knowledge.get_sv_type_info('DEL')
        assert sv_info is not None
        assert 'description' in sv_info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])