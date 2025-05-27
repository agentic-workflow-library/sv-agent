# AWLKit Development Guide

## Overview

AWLKit (Agentic Workflow Library Kit) is a framework for converting between workflow languages (WDL, CWL, Nextflow) and providing tools for workflow manipulation and execution. In the context of sv-agent, it's used to convert GATK-SV's WDL workflows to CWL format.

## Architecture

### Core Components

1. **Workflow Parsers**: Parse workflow definitions from various languages
   - `WDLParser`: Parses WDL files into intermediate representation
   - `CWLParser`: Parses CWL files into intermediate representation

2. **Intermediate Representation (IR)**: Language-agnostic workflow representation
   - `Workflow`: Top-level workflow object
   - `Task`: Individual computational task
   - `Input/Output`: Data flow definitions
   - `Runtime`: Resource requirements

3. **Workflow Writers**: Generate workflow definitions in target languages
   - `CWLWriter`: Generates CWL from IR
   - `WDLWriter`: Generates WDL from IR

4. **Converters**: High-level conversion interfaces
   - `WDLToCWLConverter`: Complete WDL to CWL conversion pipeline

5. **Utilities**: Helper functions for common operations
   - Graph analysis
   - Dependency resolution
   - Resource optimization

## Development Steps

### Phase 1: Core Infrastructure
1. Set up basic package structure
2. Implement intermediate representation classes
3. Create base parser and writer interfaces

### Phase 2: WDL Parser
1. Implement WDL syntax parser
2. Build WDL to IR converter
3. Handle WDL-specific features (imports, sub-workflows)

### Phase 3: CWL Writer
1. Implement IR to CWL converter
2. Generate CWL v1.2 compliant output
3. Handle tool wrappers and requirements

### Phase 4: Integration
1. Create high-level converter API
2. Add validation and error handling
3. Implement logging and debugging features

### Phase 5: Testing
1. Unit tests for each component
2. Integration tests with real WDL files
3. Validation of generated CWL files

## Usage in sv-agent

```python
from awlkit.converters import WDLToCWLConverter
from awlkit.parsers import WDLParser
from awlkit.writers import CWLWriter

# Convert a WDL workflow to CWL
converter = WDLToCWLConverter()
cwl_workflow = converter.convert_file("path/to/workflow.wdl")
cwl_workflow.save("path/to/workflow.cwl")

# Or use individual components
parser = WDLParser()
workflow_ir = parser.parse_file("path/to/workflow.wdl")
writer = CWLWriter()
cwl_content = writer.write(workflow_ir)
```

## Implementation Notes

1. **WDL Features to Handle**:
   - Task definitions with runtime requirements
   - Workflow definitions with call statements
   - Import statements
   - Scatter/gather operations
   - Conditional execution
   - Sub-workflows

2. **CWL Generation Considerations**:
   - CommandLineTool vs Workflow
   - Input/output binding
   - Resource requirements
   - Docker container specifications
   - Scatter operations mapping

3. **GATK-SV Specific Challenges**:
   - Complex nested workflows
   - Multiple import dependencies
   - Custom runtime attributes
   - Large number of parameters

## Testing Strategy

1. Start with simple WDL tasks and verify CWL output
2. Progress to complex workflows with scatter/gather
3. Test with actual GATK-SV WDL files
4. Validate generated CWL with cwltool --validate

## Resources

- [WDL Specification](https://github.com/openwdl/wdl/blob/main/versions/1.1/SPEC.md)
- [CWL Specification](https://www.commonwl.org/v1.2/)
- [GATK-SV WDL Examples](../gatk-sv/wdl/)