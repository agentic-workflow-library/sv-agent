# AWLKit Usage Guide for SV-Agent

## Overview

AWLKit (Agentic Workflow Library Kit) is a framework developed to convert GATK-SV's WDL workflows to CWL format. This enables the SV-Agent to work with different workflow execution engines and platforms.

## Installation

```bash
# From sv-agent root directory
pip install -e awlkit/

# Or install with development dependencies
pip install -e "awlkit/[dev]"
```

## Using AWLKit with SV-Agent

### 1. Converting GATK-SV Workflows

```python
from sv_agent import SVAgent

agent = SVAgent()

# Convert all GATK-SV workflows
results = agent.convert_gatksv_to_cwl(output_dir=Path("cwl_output"))

# Convert specific modules
results = agent.convert_gatksv_to_cwl(
    output_dir=Path("cwl_output"),
    modules=["Module00a", "Module00b"]
)
```

### 2. Analyzing Workflow Structure

```python
# Analyze a specific workflow
analysis = agent.analyze_gatksv_workflow("GATKSVPipelineBatch")

print(f"Workflow: {analysis['name']}")
print(f"Inputs: {analysis['inputs']}")
print(f"Tasks: {analysis['tasks']}")
print(f"Dependencies: {analysis['statistics']}")
```

### 3. Direct AWLKit Usage

```python
from awlkit import WDLParser, CWLWriter, WDLToCWLConverter

# Simple conversion
converter = WDLToCWLConverter()
converter.convert_file(Path("input.wdl"), Path("output.cwl"))

# Parse and manipulate workflows
parser = WDLParser()
workflow = parser.parse_file(Path("workflow.wdl"))

# Modify workflow programmatically
for task in workflow.tasks.values():
    if task.runtime and not task.runtime.docker:
        task.runtime.docker = "broadinstitute/gatk:latest"

# Write modified workflow
writer = CWLWriter()
writer.write_file(workflow, Path("modified.cwl"))
```

## Command Line Usage

AWLKit provides a CLI for quick conversions:

```bash
# Convert a single file
awlkit convert workflow.wdl workflow.cwl

# Convert with validation
awlkit convert workflow.wdl workflow.cwl --validate

# Convert entire directory
awlkit convert-dir gatk-sv/wdl/ cwl_output/

# Parse and display workflow structure
awlkit parse workflow.wdl
```

## Extending AWLKit

### Adding New Features

1. **Supporting New WDL Features**
   - Edit `awlkit/src/awlkit/parsers/wdl_parser.py`
   - Add parsing logic for the new feature
   - Update IR classes if needed

2. **Improving CWL Generation**
   - Edit `awlkit/src/awlkit/writers/cwl_writer.py`
   - Add new CWL constructs as needed

3. **Custom Converters**
   ```python
   from awlkit.converters import WDLToCWLConverter
   
   class CustomConverter(WDLToCWLConverter):
       def convert_file(self, wdl_path, cwl_path):
           # Add custom preprocessing
           workflow = self.parser.parse_file(wdl_path)
           
           # Custom modifications
           self.apply_custom_rules(workflow)
           
           # Continue with conversion
           self.writer.write_file(workflow, cwl_path)
   ```

## Handling GATK-SV Specifics

GATK-SV workflows have some specific patterns that AWLKit handles:

1. **Complex Imports**: GATK-SV uses many imported workflows
2. **Scatter Operations**: Heavy use of scatter for parallel processing
3. **Runtime Requirements**: Specific Docker containers and resource needs

### Example: Converting a GATK-SV Module

```python
# Convert Module00a with all its dependencies
from awlkit import WDLParser
from pathlib import Path

parser = WDLParser()
wdl_path = Path("gatk-sv/wdl/Module00aSampleQC.wdl")

# Parse main workflow
workflow = parser.parse_file(wdl_path)

# Handle imports
for import_path in workflow.imports:
    full_path = wdl_path.parent / import_path
    imported = parser.parse_file(full_path)
    # Merge imported tasks
    workflow.tasks.update(imported.tasks)

# Now convert the complete workflow
from awlkit import CWLWriter
writer = CWLWriter()
writer.write_file(workflow, Path("Module00a_complete.cwl"))
```

## Troubleshooting

### Common Issues

1. **Import Resolution**
   - AWLKit currently doesn't automatically resolve imports
   - Manually parse and merge imported files as shown above

2. **Complex WDL Constructs**
   - Some advanced WDL features may not be fully supported
   - Check the generated CWL and manually adjust if needed

3. **Validation Errors**
   - Use `cwltool --validate` to check generated CWL files
   - AWLKit includes basic validation but external validation is recommended

### Debugging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

converter = WDLToCWLConverter()
converter.convert_file(wdl_path, cwl_path)
```

## Future Development

AWLKit is designed to be extended as needed. Planned features:

1. **Automatic Import Resolution**: Recursively parse and include imported workflows
2. **Workflow Execution**: Direct execution support using CWL runners
3. **Optimization**: Analyze and optimize workflow structure
4. **Additional Formats**: Support for Nextflow, Snakemake conversions

## Contributing

To contribute to AWLKit development:

1. Add tests for new features in `awlkit/tests/`
2. Ensure compatibility with GATK-SV workflows
3. Document new functionality
4. Run tests: `pytest awlkit/tests/`