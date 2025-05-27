# Submodules Directory

This directory contains the git submodules used by sv-agent:

## awlkit/
The Agentic Workflow Language Kit - provides base infrastructure for building domain-specific agents.
- Base agent classes
- Chat and notebook interfaces  
- LLM integration framework
- Workflow utilities

## gatk-sv/
The Broad Institute's GATK-SV pipeline for structural variant discovery.
- 90+ WDL workflow files
- SV calling modules (Module00a-Module06)
- Reference data and documentation

## awl-handbook/
The AWL project handbook and documentation.
- Developer guides
- Architecture documentation
- Best practices

## Updating Submodules

To update all submodules to their latest versions:
```bash
git submodule update --remote
```

To update a specific submodule:
```bash
git submodule update --remote submodules/awlkit
```